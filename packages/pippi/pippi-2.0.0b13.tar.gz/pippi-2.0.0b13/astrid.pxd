#cython: language_level=3

from pippi.soundbuffer cimport *

cdef extern from "mqueue.h":
    ctypedef int mqd_t

cdef extern from "stdatomic.h":
    ctypedef struct atomic_size_t:
        pass
    ctypedef struct atomic_int:
        pass

cdef extern from "astrid.h":
    ctypedef struct ringbuf_worker_t:
        pass
    cdef const int NOTE_ON
    cdef const int NOTE_OFF
    cdef const int CONTROL_CHANGE
    cdef const int NAME_MAX
    cdef const int ASTRID_MAX_AUTOTRIGGERS
    cdef const int ASTRID_MAX_AUTOTRIGGER_SUBEVENTS

    enum MainMQProducers:
        MAINMQ_MAIN_PRODUCER,
        MAINMQ_C_INSTRUMENT_PRODUCER,
        MAINMQ_PY_INSTRUMENT_PRODUCER,
        MAINMQ_AUTOTRIGGER_PRODUCER,
        MAINMQ_SCHEDULER_PRODUCER,
        MAINMQ_UDP_PRODUCER, 
        MAINMQ_MIDI_PRODUCER, 
        MAINMQ_POSIX_INBOX_PRODUCER,
        MAINMQ_RENDER_CALLBACK_PRODUCER,
        NUM_MAINMQ_PRODUCERS

    enum LPMessageTypes:
        LPMSG_EMPTY,
        LPMSG_PLAY,
        LPMSG_TRIGGER,
        LPMSG_AUTOTRIGGER_REPLACE_ALL,
        LPMSG_AUTOTRIGGER_UPDATE,
        LPMSG_UPDATE,
        LPMSG_SERIAL,
        LPMSG_UDP,
        LPMSG_SCHEDULE,
        LPMSG_LOAD,
        LPMSG_RENDER_COMPLETE,
        LPMSG_DATA,
        LPMSG_SHUTDOWN,
        LPMSG_SET_COUNTER,
        LPMSG_MIDI_FROM_DEVICE,
        LPMSG_MIDI_TO_DEVICE,
        LPMSG_GRAPH_UPDATE_READY,
        LPMSG_CONNECT,
        LPMSG_DISCONNECT,
        NUM_LPMESSAGETYPES

    enum LPMessageFlags:
        LPFLAG_NONE,
        LPFLAG_IS_SCHEDULED,
        LPFLAG_IS_ENCODED_PARAM,
        LPFLAG_IS_FLOAT_ENCODED,
        LPFLAG_IS_INT32_ENCODED

    enum LPParamTypes:
        LPPARAM_NONE,
        LPPARAM_STRING,
        LPPARAM_INT32,
        LPPARAM_SIZE_T,
        LPPARAM_FLOAT,
        LPPARAM_FLOATLIST,
        LPPARAM_DOUBLE,
        LPPARAM_PATTERNBUF,
        LPPARAM_USER1,
        LPPARAM_USER2,
        LPPARAM_USER3,
        NUM_LPPARAMTYPES

    enum AstridSharedTypes:
        ASTRID_TYPE_FLOAT,
        ASTRID_TYPE_INT,
        ASTRID_TYPE_STRING,
        ASTRID_TYPE_NAME,
        ASTRID_TYPE_PATH,
        ASTRID_TYPE_MESSAGE,
        ASTRID_TYPE_MUSTARD,
        ASTRID_TYPE_PATTERN,
        ASTRID_TYPE_TRIGGERS,
        ASTRID_TYPE_INSTRUMENT,
        ASTRID_TYPE_BUFFER,
        ASTRID_TYPE_ARRAY,
        ASTRID_TYPE_BYTES,
        ASTRID_TYPE_NONE,
        NUMSHAREDTYPES

    enum AstridSharedFlags:
        ASTRID_FLAG_NONE,
        ASTRID_FLAG_VALUE_STORED_IN_HEADER,
        NUMFLAGS

    ctypedef struct lpmsg_t:
        double scheduled;
        double max_processing_time;
        size_t initiated;
        size_t onset_delay;
        size_t voice_id;
        size_t count;
        uint16_t flags;
        uint16_t type;
        char msg[LPMAXMSG];
        char instrument_name[LPMAXNAME];

    ctypedef struct atomic_uint:
        pass

    ctypedef struct lpmsgq_meta_t:
        char queue_shm_name[16];
        size_t total_size;
        size_t buffer_size;
        unsigned num_workers;
        atomic_uint next_worker_id;

    ctypedef struct lpmsgq_t:
        lpmsgq_meta_t * meta;
        void * shm_base;
        void * rb;
        char * buffer;
        int shmfd;

    ctypedef struct astrid_shared_resource_header_t:
        uint64_t size
        uint32_t flags
        uint32_t type
        unsigned char value[512]

    ctypedef struct astrid_shared_resource_t:
        astrid_shared_resource_header_t header
        char lock_name[4096];
        void * txn
        void * lock
        int shmfd
        unsigned char * data

    ctypedef struct astrid_session_qs_t:
        lpmsgq_meta_t internal_messages;
        lpmsgq_meta_t internal_relay_messages;
        lpmsgq_meta_t midi_messages[4];
        lpmsgq_meta_t gpio_messages;

    ctypedef struct astrid_session_t:
        char instrument_name[16]
        char lock_name[4096]
        char datapath[4096]
        size_t buffer_count
        int inbox_messages;
        astrid_session_qs_t * qs;
        astrid_shared_resource_t qs_resource;
        lpmsgq_t q_internal_messages;
        lpmsgq_t q_internal_relay_messages;
        lpmsgq_t q_midi_messages[4];
        lpmsgq_t q_gpio_messages;

    ctypedef struct lpparamset_t:
       u_int32_t keys[4096]; 
       u_int32_t types[4096];
       int num_params;

    ctypedef struct lpscheduler_t:
        pass

    ctypedef struct lpautotrigger_t:
        double speed
        size_t phase
        size_t period
        int num_onsets;
        int has_triggered[ASTRID_MAX_AUTOTRIGGER_SUBEVENTS];
        size_t onsets[ASTRID_MAX_AUTOTRIGGER_SUBEVENTS]; 
        lpmsg_t messages[ASTRID_MAX_AUTOTRIGGER_SUBEVENTS];

    ctypedef struct lpautotrigger_table_t:
        int num_active_triggers
        int num_retired_triggers
        int active_triggers[ASTRID_MAX_AUTOTRIGGERS]
        int retired_triggers[ASTRID_MAX_AUTOTRIGGERS]
        lpautotrigger_t autotriggers[ASTRID_MAX_AUTOTRIGGERS]

    ctypedef struct lpinstrument_config_t:
        char * name;
        int input_channels;
        int output_channels;
        lpfloat_t initial_volume;
        lpfloat_t requested_samplerate;
        lpfloat_t adc_length;
        lpfloat_t resampler_length;
        int ext_relay_enabled;
        int is_interactive;
        lpfloat_t bpm;
        void * ctx;
        char * tty;
        int udp_port;
        char * midiin_device_names[8];
        int num_midiin_device_names;
        char * midiout_device_names[8];
        int num_midiout_device_names;
        int (*stream_callback)(size_t blocksize, float ** input, float ** output, void * instrument);
        int (*post_init_callback)(void * instrument);
        int (*renderer_callback)(void * instrument);
        int (*update_callback)(void * instrument, char * key, char * val);
        int (*midi_callback)(void * instrument, unsigned char mtype, unsigned char mid, unsigned char mval);
        int (*trigger_callback)(void * instrument);

    ctypedef struct lpinstrument_t:
        char * name;
        int input_channels;
        int output_channels;
        int is_interactive;
        lpfloat_t initial_volume;
        volatile int is_running;
        volatile int is_waiting;
        volatile int is_ready;
        int has_been_initialized;
        lpfloat_t samplerate;

        astrid_session_t session;

        volatile int autotrigger_is_enabled;
        lpmsg_t autotrigger_msg;

        char cmdbuf[1024];

        uint32_t param_volume;
        uint32_t param_trigger_reset;
        uint32_t param_period_in_ticks;
        uint32_t param_offset_in_ticks;
        uint32_t param_last_trigger_time;

        char adcname[4096];
        char resamplername[4096];

        int ext_relay_enabled;
        lpmsg_t msg;
        lpmsg_t cmd;

        int midiin_device_ids[8];
        int num_midiin_devices;
        int midiout_device_id;

        void * context;
        int (*trigger)(void * instrument);
        int (*update)(void * instrument, char * key, char * val);
        int (*midievent)(void * instrument, unsigned char mtype, unsigned char mid, unsigned char mval);
        int (*renderer)(void * instrument);
        int (*stream)(size_t blocksize, float ** input, float ** output, void * instrument);
        void (*shutdown)(int sig);

    ctypedef struct astrid_session_factory_t:
        int (*create)(astrid_session_t * session, char * name);
        int (*open)(astrid_session_t * session, char * name);
        int (*close)(astrid_session_t * session);
        int (*get_info)(astrid_session_t * session, char * key, astrid_shared_resource_header_t * header);
        size_t (*get_size)(astrid_session_t * session, char * key);
        uint32_t (*get_type)(astrid_session_t * session, char * key);
        int (*set_float)(astrid_session_t * session, char * key, lpfloat_t val);
        lpfloat_t (*get_float)(astrid_session_t * session, char * key);
        lpfloat_t (*get_float_from_hash)(astrid_session_t * session, uint32_t key_hash);
        int (*set_float_from_hash)(astrid_session_t * session, uint32_t key_hash, lpfloat_t val);
        int (*exists)(astrid_session_t * session, char * key);
        int (*exists_from_hash)(astrid_session_t * session, uint32_t key_hash);
        int (*set_int)(astrid_session_t * session, char * key, lpint_t val);
        lpint_t (*get_int)(astrid_session_t * session, char * key);
        int (*set_string)(astrid_session_t * session, char * key, char * str);
        int (*get_string)(astrid_session_t * session, char * key, char * str);
        int (*set_buffer)(astrid_session_t * session, char * key, lpbuffer_t * buf);
        lpbuffer_t * (*get_buffer)(astrid_session_t * session, char * key);

    extern const astrid_session_factory_t AstridSession;

    uint32_t lphashstr(char * str);

    int astrid_write_ringbuffer_block(lpbuffer_t * buf, float ** block, int channels, size_t blocksize_in_frames);
    int astrid_write_floatblock_to_ringbuffer(lpbuffer_t * buf, float ** block, int channels, size_t blocksize_in_frames);
    int astrid_read_ringbuffer_block(lpbuffer_t * buf, size_t offset_in_frames, lpbuffer_t * out);
    int astrid_overdub_ringbuffer_block(lpbuffer_t * buf, float ** block, int channels, lpfloat_t volume, lpfloat_t feedback, size_t blocksize_in_frames);

    int lpipc_getid(char * path)
    ssize_t astrid_get_voice_id()

    int astrid_queue_send_message(mqd_t q, lpmsg_t msg)
    int send_message(char * qname, lpmsg_t msg)

    int astrid_msgq_init(astrid_session_t * session, char * qname)
    lpmsgq_t * astrid_msgq_produce(astrid_session_t * session, char * qname, int producer_id)
    lpmsgq_t * astrid_msgq_consume(astrid_session_t * session, char * qname)
    void astrid_msgq_close(lpmsgq_t * q)
    int astrid_msgq_read(lpmsgq_t * q, lpmsg_t * msg)
    int astrid_msgq_write(lpmsgq_t * q, lpmsg_t * msg)

    int lpmidi_setcc(int device_id, int cc, int value)
    int lpmidi_getcc(int device_id, int cc)
    int lpmidi_setnote(int device_id, int note, int velocity)
    int lpmidi_getnote(int device_id, int note)
    int lpmidi_relay_to_instrument(char * instrument_name, unsigned char device_index, unsigned char mtype, unsigned char mid, unsigned char mval)
    int lpmidi_encode_msg(lpmsg_t * msg, int channel, unsigned char message_type, int param, int value)
    int lpmidi_decode_eventbytes(char * payload, unsigned char * device_index, unsigned char * mtype, unsigned char * mid, unsigned char * mval)

    int lpserial_setctl(astrid_session_t * session, int device_id, int param_id, size_t value)
    int lpserial_getctl(astrid_session_t * session, int device_id, int param_id, lpfloat_t * value)

    int astrid_session_get_or_create_datadir_path(char * dbpath);

    int astrid_instrument_process_param_updates(lpinstrument_t * instrument);

    int astrid_autotrigger_init(lpautotrigger_t * at);
    int astrid_autotrigger_add_onset(lpautotrigger_t * at, size_t onset_time, size_t period, lpfloat_t speed, char * cmd);
    int astrid_autotrigger_table_get_free_slot(lpautotrigger_table_t * att);
    int astrid_autotrigger_table_clear(lpautotrigger_table_t * att);
    int astrid_autotrigger_update_speed(lpautotrigger_t * at, lpfloat_t speed);
    int astrid_autotrigger_update_onset_value(lpautotrigger_t * at, int onset_index, size_t onset_frames);
    int astrid_autotrigger_update_onset_cmd(lpautotrigger_t * at, int onset_index, char * cmd);
    int astrid_autotrigger_update_all_cmds(lpautotrigger_t * at, char * cmd);

    void scheduler_schedule_event(lpscheduler_t * s, lpbuffer_t * buf, size_t delay)
    int lpscheduler_get_now_seconds(double * now)
    int lpscheduler_get_now_ticks(size_t * now, int samplerate)

    lpbuffer_t * deserialize_buffer(char * str, lpmsg_t * msg)

    lpinstrument_config_t astrid_instrument_init_config(char * name)
    lpinstrument_t * astrid_instrument_start_from_config(lpinstrument_config_t config)
    lpinstrument_t * astrid_instrument_start_from_config_with_ptr(lpinstrument_config_t config, lpinstrument_t * instrument)
    int astrid_instrument_stop(lpinstrument_t * instrument)
    int astrid_instrument_tick(lpinstrument_t * instrument)
    int astrid_instrument_python_graph_stream_callback(size_t blocksize, float ** input, float ** output, void * instrument)
    void scheduler_cleanup_nursery(lpscheduler_t * s)
    int relay_message_to_seq(lpinstrument_t * instrument)
    int send_message(char * qname, lpmsg_t msg)
    int send_play_message(lpmsg_t msg)
    int send_serial_message(lpmsg_t msg)
    int parse_message_from_external_cmdline(char * cmdline, lpmsg_t * msg)

    int astrid_make_sem_name(char * name, char * sem_name);
    size_t astrid_get_resource_type_size(int resource_type, size_t size);

    int astrid_session_create(astrid_session_t * session, char * instrument_name);
    int astrid_session_open(astrid_session_t * session, char * instrument_name);
    int astrid_session_close(astrid_session_t * session);
    int astrid_session_publish_bufstr(astrid_session_t * session, lpmsgq_t * msgq, unsigned char * bufstr, size_t size);
    int astrid_session_publish_buffer(astrid_session_t * session, lpmsgq_t * msgq, lpbuffer_t * buf, int map_channels, int * channel_map);

    int astrid_session_get_or_create_datadir_path(char * dbpath);
    int astrid_session_register_shared_resource(astrid_session_t * session, char * name, void * value, int resource_type, size_t size);
    int astrid_session_set_shared_resource(astrid_session_t * session, char * name, void * value);
    int astrid_session_get_shared_resource(astrid_session_t * session, char * name, void * value);
    int astrid_session_aquire_shared_resource(astrid_session_t * session, astrid_shared_resource_t * resource, char * name);
    int astrid_session_release_shared_resource(astrid_session_t * session,  astrid_shared_resource_t * resource, char * name);
    int astrid_session_destroy_shared_resource(astrid_session_t * session, char * name);
    int astrid_resize_aquired_shared_resource(astrid_shared_resource_t * resource, size_t new_size);

    int astrid_session_get_info(astrid_session_t * session, char * key, astrid_shared_resource_header_t * header);
    size_t astrid_session_get_size(astrid_session_t * session, char * key);
    uint32_t astrid_session_get_type(astrid_session_t * session, char * key);
    lpint_t astrid_session_get_int(astrid_session_t * session, char * key);
    int astrid_session_set_int(astrid_session_t * session, char * key, lpint_t val);
    lpfloat_t astrid_session_get_float(astrid_session_t * session, char * key);
    lpfloat_t astrid_session_get_float_from_hash(astrid_session_t * session, uint32_t key_hash);
    int astrid_session_set_float(astrid_session_t * session, char * key, lpfloat_t val);
    int astrid_session_set_string(astrid_session_t * session, char * key, char * str);
    int astrid_session_get_string(astrid_session_t * session, char * key, char * str);
    int astrid_session_set_buffer(astrid_session_t * session, char * key, lpbuffer_t * buf);
    lpbuffer_t * astrid_session_get_buffer(astrid_session_t * session, char * key);

    int astrid_session_read_shared_ringbuffer_block(astrid_session_t * session, char * name, size_t offset_in_frames, lpbuffer_t * out); 
    int astrid_session_write_lpbuffer_to_shared_ringbuffer(astrid_session_t * session, char * name, lpbuffer_t * src); 

cdef class MessageEvent:
    cdef Renderer r
    cdef lpmsg_t msg
    cpdef int schedule(MessageEvent self, size_t now=*)

cdef class ParamBucket:
    cdef object _params
    cdef str _play_params

cdef class Router:
    pass

cdef class EventTriggerFactory:
    cdef Renderer r
    cpdef midinote(self, double onset, str instrument_name, double length, double freq=*, double amp=*, int note=*, int velocity=*, int channel=*, int device_index=*)
    cpdef midi(self, double onset, str instrument_name, int b1, int b2, int b3, int device_index=*)

cdef class Renderer:
    cdef public str name
    cdef public str path
    cdef char * adcname

    cdef uint32_t name_hash

    cdef astrid_session_t session
    cdef lpmsgq_t * msgq  # producer handle for publishing buffers to internal message queue
    cdef lpmsgq_t * relay_msgq  # consumer handle for reading from relay queue
    cdef lpmsg_t msg # a copy of the last message received

    cdef public object _renderer
    cdef public object graph

    cdef public int channels
    cdef public int input_channels
    cdef public int output_channels
    cdef public double samplerate

    cdef public double max_processing_time
    cdef public size_t last_reload
    cdef public dict midi_device_mapping
    cdef public dict _hash_cache

    cpdef EventContext get_event_context(Renderer self)
    cdef SoundBuffer read_from_adc(Renderer self, double length, double offset=*, int channels=*, int samplerate=*)
    cpdef void set_autotrigger(Renderer self, int autotrigger_id, double freq, str cmd)

    cpdef object get_session_value(Renderer self, str key, object default=*)
    cpdef void set_session_value(Renderer self, str key, object value)
    cpdef void set_session_param_hash(Renderer self, str key, double value)
    cdef int write_to_internal_queue(Renderer self, lpmsg_t * msg)


cdef class Instrument:
    cdef public str name
    cdef public str midi_input_device
    cdef public str midi_output_device
    cdef public str path

    cdef lpmsgq_t * relay_msgq  # consumer handle for reading from relay queue
    cdef lpmsg_t msg # a copy of the last message received

    cdef public int channels
    cdef public int input_channels
    cdef public int output_channels
    cdef public double samplerate

    cdef public char ascii_name[256] # instrument name as a c string
    cdef public char ascii_midi_input_device_names[8][256]  # Array of device names
    cdef public char ascii_midi_output_device_names[8][256] 
    cdef public list midi_input_devices  # Python list of device names
    cdef public list midi_output_devices
    cdef public dict midi_device_mapping  # Maps device index to device ID

    cdef lpinstrument_t * i
    cdef lpinstrument_config_t config

    cpdef lpmsg_t get_message(Instrument self)

cdef class SessionParamBucket:
    cdef Renderer r

cdef class GraphNodeParamAccessor:
    cdef str node_name
    cdef Renderer r

cdef class GraphParamBucket:
    cdef Renderer r

cdef class MidiDeviceBucket:
    cdef Renderer r
    cdef int device_id
    cdef int channel

cdef class MidiBucket:
    cdef Renderer r
    cdef dict device_map

cdef class Seq:
    cdef Renderer r
    cdef list triggers

cdef class EventContext:
    cdef public ParamBucket p
    cdef public SessionParamBucket s
    cdef public MidiBucket m
    cdef public EventTriggerFactory t
    cdef public Renderer r
    cdef public Router _router
    cdef public Seq seq
    cdef public str instrument_name
    cdef public object sounds
    cdef public object _graph
    cdef public int count
    cdef public int tick
    cdef public int vid
    cdef public size_t now
    cdef public double max_processing_time

cdef tuple collect_players(Renderer r)
cdef set collect_trigger_planners(Renderer r)
cdef int render_event(Renderer r)
cdef int trigger_events(Renderer r)

cdef bytes serialize_lpmsg(lpmsg_t msg)
cdef void deserialize_lpmsg(bytes msgb, lpmsg_t * msg)
