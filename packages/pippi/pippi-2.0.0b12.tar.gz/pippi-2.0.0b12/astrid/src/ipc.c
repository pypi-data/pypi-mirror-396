#include "astrid.h"

#if 0 // TODO could profile other linux backends, or other platforms
// Set a default IPC type if one hasn't been set explicity by adding:
//      -DASTRID_IPC_TYPE=ASTRID_IPC_LMDB
// for example to set the IPC backend to LMDB
#ifndef ASTRID_IPC_TYPE
    #if defined(__linux__) && defined(SYS_futex)
        #define ASTRID_IPC_TYPE ASTRID_FUTEX
    #elif defined(_POSIX_VERSION) && (_POSIX_VERSION >= 200112L)
        #define ASTRID_IPC_TYPE ASTRID_IPC_POSIX
    #endif
#endif
#endif



// usage
lpmsg_t msg = {0};
astrid_instrument_get_shared_resource(instrument, "myresource", &msg, ASTRID_TYPE_MESSAGE);

msg.scheduled = 200;
astrid_instrument_set_shared_resource(instrument, "myresource", &msg, ASTRID_TYPE_MESSAGE);

lpbuffer_t * buffer = LPBuffer.create(4096, 2, 48000);
astrid_instrument_set_shared_resource(instrument, "mybuffer", buffer, ASTRID_TYPE_BUFFER);


// these all should be replaced with key/value store by type interfaces
int lpipc_createvalue(char * path, size_t size);
int lpipc_setvalue(char * path, void * value, size_t size);
int lpipc_unsafe_getvalue(char * path, void ** value);
int lpipc_getvalue(char * path, void ** value);
void * lpipc_aquirevalue(char * path);
int lpipc_releaseandunmap_value(char * path, void * shmaddr, size_t size);
int lpipc_releasevalue(char * id_path) {
int lpipc_destroyvalue(char * path) {
int lpsampler_get_path(const char * name, char * path);
lpbuffer_t * lpsampler_create(char * name, double length_in_seconds, int channels, int samplerate);
lpbuffer_t * lpsampler_aquire_and_map(char * name);
int lpsampler_aquire(char * name);
int lpsampler_release(char * name);
int lpsampler_release_and_unmap(char * name, lpbuffer_t * buf);
int lpsampler_destroy_and_unmap(char * name, lpbuffer_t * buf);
int lpsampler_destroy(char * name);

// ringbuffers: these should just take a pointer and not care anything about IPC
int lpsampler_write_ringbuffer_block(char * name, lpbuffer_t * buf, float ** block, int channels, size_t blocksize_in_frames);
int lpsampler_overdub_ringbuffer_block(char * name, lpbuffer_t * buf, float ** block, int channels, lpfloat_t volume, lpfloat_t feedback, size_t blocksize_in_frames);
int lpsampler_read_ringbuffer_block(char * name, __attribute__((unused)) lpbuffer_t * _buf, size_t offset_in_frames, lpbuffer_t * out);

// these are special buffer publishing interfaces -- they place the name of a shared memory buffer + an lpmsg_t onto a queue
int astrid_instrument_publish_bufstr(char * instrument_name, unsigned char * bufstr, size_t size);
lpbuffer_t * deserialize_buffer(char * buffer_code, lpmsg_t * msg);

// robot utility functions
static int futex_wait_timeout(atomic_int *futex_addr, int expected, const struct timespec *timeout);
static int futex_wake(atomic_int *futex_addr, int count);
static int is_process_alive(pid_t pid);
static int acquire_futex_lock(atomic_int *futex, pid_t *owner_pid, time_t *lock_timestamp);
static int release_futex_lock(atomic_int *futex, pid_t *owner_pid);
int lpsampler_force_cleanup(const char *name);
int lpsampler_is_locked(const char *name);
int lpsampler_get_lock_info(const char *name, pid_t *owner_pid, time_t *lock_time);



/* INTERPROCESS  (IPC)
 * COMMUNICATION TOOLS
 *
 * - key/value store by type
 *   - lpfloat_t
 *   - lpint_t
 *   - lpbuffer_t
 *   - lppatternbuf_t
 *   - lpmsg_t
 *   - lparray_t
 *   - lpautotrigger_t
 *   - lpinstrument_t
 *
 * *******************/
int lpipc_createvalue(char * path, size_t size) {
    int shmfd;
    sem_t * sem;
    char * semname;

    /* Construct the sempahore name by stripping the /tmp prefix */
    semname = path + 4;

    // always write over an existing value
    //sem_unlink(semname);
    //shm_unlink(semname);

    // create the sempahore (and initialize to 1) if it doesn't exist
    if((sem = sem_open(semname, O_CREAT | O_EXCL, LPIPC_PERMS, 1)) == NULL) {
        syslog(LOG_ERR, "lpipc_createvalue failed to create semaphore %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Create the POSIX shared memory segment */
    if((shmfd = shm_open(semname, O_CREAT | O_RDWR, LPIPC_PERMS)) < 0) {
        syslog(LOG_ERR, "lpipc_createvalue Could not create shared memory segment. (%s) %s\n", semname, strerror(errno));
        return -1;
    }

    if(ftruncate(shmfd, size) < 0) {
        syslog(LOG_ERR, "lpipc_createvalue Could not truncate shared memory segment to size %ld. (%s) %s\n", size, semname, strerror(errno));
        return -1;
    }

    if(sem_close(sem) < 0) {
        syslog(LOG_ERR, "lpipc_createvalue sem_close Could not close semaphore\n");
        return -1;
    }

    close(shmfd);

    return 0;
}

int lpipc_setvalue(char * path, void * value, size_t size) {
    int fd;
    sem_t * sem;
    void * shmaddr;
    char * semname;

    /* Construct the sempahore name by stripping the /tmp prefix */
    /* FIXME move path prefixes to config */
    semname = path + 4;

    /* Open the semaphore */
    if((sem = sem_open(semname, 0)) == SEM_FAILED) {
        syslog(LOG_ERR, "lpipc_setvalue failed to open semaphore %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Aquire a lock on the semaphore */
    if(sem_wait(sem) < 0) {
        syslog(LOG_ERR, "lpipc_setvalue failed to decrementsem %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Get the file descriptor for the shared memory segment */
    if((fd = shm_open(semname, O_RDWR, LPIPC_PERMS)) < 0) {
        syslog(LOG_ERR, "lpipc_setvalue Could not open shared memory segment. (%s) %s\n", semname, strerror(errno));
        return -1;
    }

    /* Attach the shared memory to the pointer */
    if((shmaddr = (void*)mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        syslog(LOG_ERR, "lpipc_setvalue Could not mmap shared memory segment to size %ld. (%s) %s\n", size, semname, strerror(errno));
        return -1;
    }

    /* Write the value into the shared memory segment */
    memcpy(shmaddr, value, size);

    /* unmap the shared memory... */
    munmap(shmaddr, size);

    /* Release the lock on the semaphore */
    if(sem_post(sem) < 0) {
        syslog(LOG_ERR, "lpipc_setvalue failed to unlock %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }
    
    /* Clean up sempahore resources */
    if(sem_close(sem) < 0) {
        syslog(LOG_ERR, "lpipc_setvalue sem_close Could not close semaphore\n");
        return -1;
    }

    close(fd);

    return 0;
}

int lpipc_unsafe_getvalue(char * path, void ** value) {
    struct stat statbuf;
    void * shmaddr;
    int fd;

    /* Get the file descriptor for the shared memory segment */
    if((fd = shm_open(path+4, O_RDWR, LPIPC_PERMS)) < 0) {
        syslog(LOG_ERR, "lpipc_unsafe_getvalue Could not open shared memory segment. (%s) %s\n", path, strerror(errno));
        return -1;
    }

    /* Get the size of the segment */
    if(fstat(fd, &statbuf) < 0) {
        syslog(LOG_ERR, "lpipc_unsafe_getvalue Could not stat shm. Error: %s\n", strerror(errno));
        return -1;
    }

    /* Attach the shared memory to the pointer */
    if((shmaddr = (void*)mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        syslog(LOG_ERR, "lpipc_unsafe_getvalue Could not mmap shared memory segment to size %ld. (%s) %s\n", statbuf.st_size, path, strerror(errno));
        return -1;
    }

    memcpy(*value, shmaddr, statbuf.st_size);

    /* unmap the shared memory... */
    munmap(shmaddr, statbuf.st_size);

    close(fd);

    return 0;
}

int lpipc_getvalue(char * path, void ** value) {
    struct stat statbuf;
    int fd;
    sem_t * sem;
    void * shmaddr;
    char * semname;

    /* Construct the sempahore name by stripping the /tmp prefix */
    semname = path + 4;

    /* Open the semaphore */
    if((sem = sem_open(semname, 0, LPIPC_PERMS)) == SEM_FAILED) {
        syslog(LOG_ERR, "lpipc_setvalue failed to open semaphore %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Aquire a lock on the semaphore */
    if(sem_wait(sem) < 0) {
        syslog(LOG_ERR, "lpipc_setvalue failed to decrementsem %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Get the file descriptor for the shared memory segment */
    if((fd = shm_open(semname, O_RDWR, LPIPC_PERMS)) < 0) {
        syslog(LOG_ERR, "lpipc_getvalue Could not open shared memory segment. (%s) %s\n", semname, strerror(errno));
        return -1;
    }

    /* Get the size of the segment */
    if(fstat(fd, &statbuf) < 0) {
        syslog(LOG_ERR, "lpipc_getvalue Could not stat shm. Error: %s\n", strerror(errno));
        return -1;
    }

    /* Attach the shared memory to the pointer */
    if((shmaddr = (void*)mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        syslog(LOG_ERR, "lpipc_getvalue Could not mmap shared memory segment to size %ld. (%s) %s\n", statbuf.st_size, semname, strerror(errno));
        return -1;
    }

    memcpy(*value, shmaddr, statbuf.st_size);

    /* unmap the shared memory... */
    munmap(shmaddr, statbuf.st_size);

    /* Clean up sempahore resources */
    if(sem_close(sem) < 0) {
        syslog(LOG_ERR, "lpipc_getvalue sem_close Could not close semaphore\n");
        return -1;
    }

    close(fd);

    return 0;
}

void * lpipc_aquirevalue(char * path) {
    struct stat statbuf;
    int fd;
    sem_t * sem;
    void * shmaddr;
    char * semname;

    /* Construct the sempahore name by stripping the /tmp prefix */
    semname = path + 4;

    /* Open the semaphore */
    if((sem = sem_open(semname, 0, LPIPC_PERMS)) == SEM_FAILED) {
        syslog(LOG_ERR, "lpipc_setvalue failed to open semaphore %s. Error: %s\n", semname, strerror(errno));
        return NULL;
    }

    /* Aquire a lock on the semaphore */
    if(sem_wait(sem) < 0) {
        syslog(LOG_ERR, "lpipc_setvalue failed to decrementsem %s. Error: %s\n", semname, strerror(errno));
        return NULL;
    }

    /* Get the file descriptor for the shared memory segment */
    if((fd = shm_open(semname, O_RDWR, LPIPC_PERMS)) < 0) {
        syslog(LOG_ERR, "lpipc_getvalue Could not open shared memory segment. (%s) %s\n", semname, strerror(errno));
        return NULL;
    }

    /* Get the size of the segment */
    if(fstat(fd, &statbuf) < 0) {
        syslog(LOG_ERR, "lpipc_getvalue Could not stat shm. Error: %s\n", strerror(errno));
        return NULL;
    }

    /* Attach the shared memory to the pointer */
    if((shmaddr = (void*)mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        syslog(LOG_ERR, "lpipc_getvalue Could not mmap shared memory segment to size %ld. (%s) %s\n", statbuf.st_size, semname, strerror(errno));
        return NULL;
    }

    /* Clean up sempahore resources */
    if(sem_close(sem) < 0) {
        syslog(LOG_ERR, "lpipc_getvalue sem_close Could not close semaphore\n");
        return NULL; 
    }

    close(fd);

    return shmaddr;
}

int lpipc_releaseandunmap_value(char * path, void * shmaddr, size_t size) {
    sem_t * sem;
    char * semname;

    /* Construct the sempahore name by stripping the /tmp prefix */
    semname = path + 4;

    /* unmap the shared memory... */
    munmap(shmaddr, size);

    /* Open the semaphore */
    if((sem = sem_open(semname, 0)) == SEM_FAILED) {
        syslog(LOG_ERR, "lpipc_releasevalue failed to open semaphore %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Release the lock on the semaphore */
    if(sem_post(sem) < 0) {
        syslog(LOG_ERR, "lpipc_releasevalue failed to unlock %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Clean up sempahore resources */
    if(sem_close(sem) < 0) {
        syslog(LOG_ERR, "lpipc_releasevalue sem_close Could not close semaphore\n");
        return -1;
    }

    return 0;
}


int lpipc_releasevalue(char * id_path) {
    sem_t * sem;
    char * semname;

    /* Construct the sempahore name by stripping the /tmp prefix */
    semname = id_path + 4;

    /* Open the semaphore */
    if((sem = sem_open(semname, 0)) == SEM_FAILED) {
        syslog(LOG_ERR, "lpipc_releasevalue failed to open semaphore %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Release the lock on the semaphore */
    if(sem_post(sem) < 0) {
        syslog(LOG_ERR, "lpipc_releasevalue failed to unlock %s. Error: %s\n", semname, strerror(errno));
        return -1;
    }

    /* Clean up sempahore resources */
    if(sem_close(sem) < 0) {
        syslog(LOG_ERR, "lpipc_releasevalue sem_close Could not close semaphore\n");
        return -1;
    }

    return 0;
}

int lpipc_destroyvalue(char * path) {
    char * semname;

    semname = path + 4;

    if(sem_unlink(semname) < 0) {
        syslog(LOG_ERR, "lpipc_destroyvalue sem_unlink Could not destroy semaphore\n");
        return -1;
    }

    return 0;
}


// BEGIN ROBOT CODE
#define FUTEX_TIMEOUT_SEC 1
#define MAX_SEGMENT_AGE_SEC 30

// Futex operation wrappers
static int futex_wait_timeout(atomic_int *futex_addr, int expected, const struct timespec *timeout) {
    return syscall(SYS_futex, futex_addr, FUTEX_WAIT_PRIVATE, expected, timeout, NULL, 0);
}

static int futex_wake(atomic_int *futex_addr, int count) {
    return syscall(SYS_futex, futex_addr, FUTEX_WAKE_PRIVATE, count, NULL, NULL, 0);
}

// Process alive check
static int is_process_alive(pid_t pid) {
    if (pid <= 0) return 0;
    return kill(pid, 0) == 0;
}

// Shared futex lock acquisition with timeout
static int acquire_futex_lock(atomic_int *futex, pid_t *owner_pid, time_t *lock_timestamp) {
    struct timespec timeout = {
        .tv_sec = FUTEX_TIMEOUT_SEC,
        .tv_nsec = 0
    };
    
    time_t current_time = time(NULL);
    int expected = 0;
    
    // Check for dead owner
    if (*owner_pid != 0) {
        if (!is_process_alive(*owner_pid) || 
            (current_time - *lock_timestamp) > FUTEX_TIMEOUT_SEC) {
            atomic_store(futex, 0);
            *owner_pid = 0;
            futex_wake(futex, 1);
        }
    }

    while (!atomic_compare_exchange_strong(futex, &expected, 1)) {
        if (futex_wait_timeout(futex, 1, &timeout) < 0) {
            if (errno == ETIMEDOUT) {
                syslog(LOG_ERR, "Lock acquisition timed out\n");
                return -1;
            }
            if (errno != EAGAIN) {
                syslog(LOG_ERR, "Futex wait failed: %s\n", strerror(errno));
                return -1;
            }
        }
        expected = 0;
    }

    *owner_pid = getpid();
    *lock_timestamp = time(NULL);
    return 0;
}

// Shared futex lock release
static int release_futex_lock(atomic_int *futex, pid_t *owner_pid) {
    if (*owner_pid == getpid()) {
        *owner_pid = 0;
        atomic_store(futex, 0);
        return futex_wake(futex, 1);
    }
    return -1;
}

// Path helper function
int lpsampler_get_path(const char * name, char * path) {
    snprintf(path, PATH_MAX, "/lpsamp-%s", name);
    return 0;
}

// Sampler creation
lpbuffer_t * lpsampler_create(char * name, double length_in_seconds, int channels, int samplerate) {
    int shmfd;
    lpshared_t * shared;
    size_t bufsize;
    char path[PATH_MAX] = {0};
    size_t length = (size_t)(length_in_seconds * samplerate);

    lpsampler_get_path(name, path);

    bufsize = sizeof(lpshared_t) + (length * channels * sizeof(lpfloat_t));

    // Clean up any existing segment
    shm_unlink(path);

    if((shmfd = shm_open(path, O_CREAT | O_RDWR | O_EXCL, LPIPC_PERMS)) < 0) {
        syslog(LOG_ERR, "lpsampler_create: Could not create shared memory segment\n");
        return NULL; 
    }

    if(ftruncate(shmfd, bufsize) < 0) {
        close(shmfd);
        shm_unlink(path);
        return NULL;
    }

    if((shared = mmap(NULL, bufsize, PROT_READ | PROT_WRITE, MAP_SHARED, shmfd, 0)) == MAP_FAILED) {
        close(shmfd);
        shm_unlink(path);
        return NULL;
    }

    memset(shared, 0, bufsize);
    atomic_init(&shared->futex, 0);
    shared->owner_pid = 0;
    shared->lock_timestamp = time(NULL);

    shared->buffer.channels = channels;
    shared->buffer.length = length;
    shared->buffer.samplerate = samplerate;
    shared->buffer.boundry = length-1;
    shared->buffer.range = length;

    close(shmfd);
    return &shared->buffer;
}

// Acquire and map sampler
lpbuffer_t * lpsampler_aquire_and_map(char * name) {
    struct stat statbuf;
    int fd;
    lpshared_t * shared;
    char path[PATH_MAX] = {0};
    
    lpsampler_get_path(name, path);

    if((fd = shm_open(path, O_RDWR, LPIPC_PERMS)) < 0) {
        return NULL;
    }

    if(fstat(fd, &statbuf) < 0 || (size_t)statbuf.st_size < sizeof(lpshared_t)) {
        close(fd);
        return NULL;
    }

    if((shared = mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        close(fd);
        return NULL;
    }

    if (acquire_futex_lock(&shared->futex, &shared->owner_pid, &shared->lock_timestamp) < 0) {
        munmap(shared, statbuf.st_size);
        close(fd);
        return NULL;
    }

    close(fd);
    return &shared->buffer;
}

// Acquire lock
int lpsampler_aquire(char * name) {
    lpbuffer_t * buf = lpsampler_aquire_and_map(name);
    return buf ? 0 : -1;
}

// Release lock
int lpsampler_release(char * name) {
    struct stat statbuf;
    int fd;
    lpshared_t * shared;
    char path[PATH_MAX] = {0};
    
    lpsampler_get_path(name, path);

    if((fd = shm_open(path, O_RDWR, LPIPC_PERMS)) < 0) {
        return -1;
    }

    if(fstat(fd, &statbuf) < 0) {
        close(fd);
        return -1;
    }

    if((shared = mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        close(fd);
        return -1;
    }

    int result = release_futex_lock(&shared->futex, &shared->owner_pid);
    
    munmap(shared, statbuf.st_size);
    close(fd);
    return result;
}

// Release and unmap
int lpsampler_release_and_unmap(char * name, lpbuffer_t * buf) {
    (void)name;
    lpshared_t * shared = (lpshared_t *)((char *)buf - offsetof(lpshared_t, buffer));
    size_t total_size = sizeof(lpshared_t) + (buf->length * buf->channels * sizeof(lpfloat_t));

    int result = release_futex_lock(&shared->futex, &shared->owner_pid);
    munmap(shared, total_size);
    return result;
}

// Destroy and unmap
int lpsampler_destroy_and_unmap(char * name, lpbuffer_t * buf) {
    char path[PATH_MAX] = {0};
    lpshared_t * shared = (lpshared_t *)((char *)buf - offsetof(lpshared_t, buffer));
    size_t total_size = sizeof(lpshared_t) + (buf->length * buf->channels * sizeof(lpfloat_t));

    lpsampler_get_path(name, path);

    // Wake any waiting processes
    atomic_store(&shared->futex, 0);
    futex_wake(&shared->futex, INT_MAX);

    munmap(shared, total_size);
    return shm_unlink(path);
}

// Destroy
int lpsampler_destroy(char * name) {
    char path[PATH_MAX] = {0};
    lpsampler_get_path(name, path);
    return shm_unlink(path);
}

// Publish buffer string
int astrid_instrument_publish_bufstr(char * instrument_name, unsigned char * bufstr, size_t size) {
    int shmfd;
    lpshared_bufstr_t *shmaddr;
    char buffer_code[LPKEY_MAXLENGTH] = {0};
    ssize_t buffer_id = 0;
    lpmsg_t msg = {0};
    size_t total_size;
    
    buffer_id = getpid() + (rand() % 100000);
    
    if(lpencode_with_prefix(instrument_name, buffer_id, buffer_code) < 0) {
        return -1;
    }

    // Clean up any existing segment
    shm_unlink(buffer_code);

    total_size = sizeof(lpshared_bufstr_t) + size;
    
    if((shmfd = shm_open(buffer_code, O_CREAT | O_RDWR | O_EXCL, LPIPC_PERMS)) < 0) {
        return -1;
    }

    if(ftruncate(shmfd, total_size) < 0) {
        close(shmfd);
        shm_unlink(buffer_code);
        return -1;
    }

    if((shmaddr = mmap(NULL, total_size, PROT_READ | PROT_WRITE, MAP_SHARED, shmfd, 0)) == MAP_FAILED) {
        close(shmfd);
        shm_unlink(buffer_code);
        return -1;
    }

    memset(shmaddr, 0, sizeof(lpshared_bufstr_t));
    atomic_init(&shmaddr->futex, 0);
    shmaddr->lock_timestamp = time(NULL);
    
    memcpy(shmaddr->data, bufstr, size);

    memcpy(msg.instrument_name, instrument_name, strlen(instrument_name));
    memcpy(msg.msg, buffer_code, strlen(buffer_code));
    msg.type = LPMSG_RENDER_COMPLETE;

    munmap(shmaddr, total_size);
    close(shmfd);

    if(send_play_message(msg) < 0) {
        shm_unlink(buffer_code);
        return -1;
    }

    return 0;
}

// Deserialize buffer
lpbuffer_t * deserialize_buffer(char * buffer_code, lpmsg_t * msg) {
    struct stat statbuf;
    lpshared_bufstr_t *shmaddr;
    lpbuffer_t *buf = NULL;
    unsigned char *str;
    int fd;
    size_t audiosize, offset, length, onset;
    int channels, samplerate, is_looping;

    if((fd = shm_open(buffer_code, O_RDWR, LPIPC_PERMS)) < 0) {
        return NULL;
    }

    if(fstat(fd, &statbuf) < 0 || (size_t)statbuf.st_size < sizeof(lpshared_bufstr_t)) {
        close(fd);
        return NULL;
    }

    if (time(NULL) - statbuf.st_mtime > MAX_SEGMENT_AGE_SEC) {
        close(fd);
        shm_unlink(buffer_code);
        return NULL;
    }

    if((shmaddr = mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        close(fd);
        return NULL;
    }

    if (acquire_futex_lock(&shmaddr->futex, &shmaddr->owner_pid, &shmaddr->lock_timestamp) < 0) {
        munmap(shmaddr, statbuf.st_size);
        close(fd);
        shm_unlink(buffer_code);
        return NULL;
    }

    size_t data_size = statbuf.st_size - sizeof(lpshared_bufstr_t);
    str = (unsigned char *)LPMemoryPool.alloc(1, data_size);
    memcpy(str, shmaddr->data, data_size);

    offset = 0;
    memcpy(&audiosize, str + offset, sizeof(size_t));
    offset += sizeof(size_t);
    memcpy(&length, str + offset, sizeof(size_t));
    offset += sizeof(size_t);
    memcpy(&channels, str + offset, sizeof(int));
    offset += sizeof(int);
    memcpy(&samplerate, str + offset, sizeof(int));
    offset += sizeof(int);
    memcpy(&is_looping, str + offset, sizeof(int));
    offset += sizeof(int);
    memcpy(&onset, str + offset, sizeof(size_t));
    offset += sizeof(size_t);

    buf = (lpbuffer_t *)LPMemoryPool.alloc(1, sizeof(lpbuffer_t) + audiosize);
    memcpy(buf->data, str + offset, audiosize);
    offset += audiosize;
    memcpy(msg, str + offset, sizeof(lpmsg_t));

    buf->length = length;
    buf->channels = channels;
    buf->samplerate = samplerate;
    buf->is_looping = is_looping;
    buf->onset = onset;
    buf->phase = 0.f;
    buf->pos = 0;
    buf->boundry = length-1;
    buf->range = length;

    LPMemoryPool.free(str);
    
    release_futex_lock(&shmaddr->futex, &shmaddr->owner_pid);
    munmap(shmaddr, statbuf.st_size);
    shm_unlink(buffer_code);
    close(fd);

    return buf;
}

// Helper function to force cleanup of stale resources
int lpsampler_force_cleanup(const char *name) {
    char path[PATH_MAX] = {0};
    struct stat statbuf;
    int fd;
    lpshared_t *shared;
    
    lpsampler_get_path(name, path);
    
    if((fd = shm_open(path, O_RDWR, LPIPC_PERMS)) < 0) {
        return -1; // Already cleaned up or doesn't exist
    }

    if(fstat(fd, &statbuf) < 0) {
        close(fd);
        return -1;
    }

    if((shared = mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        close(fd);
        return -1;
    }

    // Force wake all waiters
    atomic_store(&shared->futex, 0);
    futex_wake(&shared->futex, INT_MAX);

    munmap(shared, statbuf.st_size);
    close(fd);
    shm_unlink(path);
    
    return 0;
}

// Helper function to check if a sampler is locked
int lpsampler_is_locked(const char *name) {
    char path[PATH_MAX] = {0};
    struct stat statbuf;
    int fd;
    lpshared_t *shared;
    int is_locked = 0;
    
    lpsampler_get_path(name, path);
    
    if((fd = shm_open(path, O_RDWR, LPIPC_PERMS)) < 0) {
        return -1;
    }

    if(fstat(fd, &statbuf) < 0) {
        close(fd);
        return -1;
    }

    if((shared = mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        close(fd);
        return -1;
    }

    // Check if locked and owner is still alive
    if (atomic_load(&shared->futex) == 1) {
        if (shared->owner_pid != 0 && is_process_alive(shared->owner_pid)) {
            is_locked = 1;
        }
    }

    munmap(shared, statbuf.st_size);
    close(fd);
    
    return is_locked;
}

// Helper function to get lock owner information
int lpsampler_get_lock_info(const char *name, pid_t *owner_pid, time_t *lock_time) {
    char path[PATH_MAX] = {0};
    struct stat statbuf;
    int fd;
    lpshared_t *shared;
    
    lpsampler_get_path(name, path);
    
    if((fd = shm_open(path, O_RDWR, LPIPC_PERMS)) < 0) {
        return -1;
    }

    if(fstat(fd, &statbuf) < 0) {
        close(fd);
        return -1;
    }

    if((shared = mmap(NULL, statbuf.st_size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0)) == MAP_FAILED) {
        close(fd);
        return -1;
    }

    *owner_pid = shared->owner_pid;
    *lock_time = shared->lock_timestamp;

    munmap(shared, statbuf.st_size);
    close(fd);
    
    return 0;
}
// END ROBOT CODE

