#ifndef LPASTRIDTYPES_H
#define LPASTRIDTYPES_H

// Used for messaging between astrid instruments
typedef struct lpmsg_t {
    /* Relative delay for target completion time 
     * from initiation time.
     *
     * This value is given by the score as the onset time
     * in seconds and is relative to the initiation time.
     * */
    double scheduled;     

    /* The longest a message in this sequence has taken 
     * so far to be processed and reach completion.
     *
     * This is used by the seq scheduler to estimate how
     * far ahead of the target time the message should be
     * sent to the renderer.
     *
     * The initial value before any estimates can be made 
     * is 75% of the scheduled interval time.
     *
     * The estimated value is overwritten each time the 
     * completed timestamp is recorded, by taking the difference 
     * between the initiation time and the completed time.
     *
     * It is preserved... where, in the instrument cache? sqlite?
     * */
    double max_processing_time;     

    /* Timestamp when the message was initiated in frames/ticks. 
     *
     * Always get this with lpscheduler_get_now_ticks
     *
     * This is the time when the message was originally sent.
     * */
    size_t initiated;     

    /* Time of arrival at mixer minus scheduled target
     * time rounded to nearest frame FIXME this is ignored currently */
    size_t onset_delay;   

    /* The voice ID is currently unused */
    size_t voice_id;

    /* Autotriggers and other message sequencers can track 
     * a sequence of events with this field. */
    size_t count;

    /* An optional flag bitfield populated with LPMessageFlags */
    uint16_t flags;

    /* LPMessageTypes enum */
    uint16_t type;
    char msg[LPMAXMSG];

    /* The destination instrument name for this message */
    char instrument_name[LPMAXNAME];
} lpmsg_t;

/* Holds a bit pattern for sequences -- unused */
typedef struct lppatternbuf_t {
    size_t length;
    unsigned char pattern[LPMAXPAT];
} lppatternbuf_t;

/* A node in the message scheduler priority queue */
typedef struct lpmsgpq_node_t {
    size_t timestamp;
    lpmsg_t msg;
    size_t pos;
    int index; /* index in node pool */
} lpmsgpq_node_t;

/* Interfaces to the ringbuf library used for message queues */
typedef struct ringbuf ringbuf_t;
typedef struct ringbuf_worker ringbuf_worker_t;

/* An autotrigger is like an LFO for lpmsg_t messages,
 * with messages scheduled as onsets within the LFO period. */
typedef struct lpautotrigger_t {
    double speed;
    size_t phase;
    size_t period;

    int num_onsets;
    int has_triggered[ASTRID_MAX_AUTOTRIGGER_SUBEVENTS]; // onset in frames to fire message
    size_t onsets[ASTRID_MAX_AUTOTRIGGER_SUBEVENTS]; // onset in frames to fire message
    lpmsg_t messages[ASTRID_MAX_AUTOTRIGGER_SUBEVENTS]; // message to fire
} lpautotrigger_t;

/* The autotrigger table contains all the autotrigger LFOs for an instrument */
typedef struct lpautotrigger_table_t {
    int num_active_triggers;
    int num_retired_triggers;
    int active_triggers[ASTRID_MAX_AUTOTRIGGERS];
    int retired_triggers[ASTRID_MAX_AUTOTRIGGERS]; // may be reclaimed if needed
    lpautotrigger_t autotriggers[ASTRID_MAX_AUTOTRIGGERS];
} lpautotrigger_table_t;

/* Metadata for shared resources, but also holds the resource 
 * value directly for small values (512 bytes or less) */
typedef struct astrid_shared_resource_header_t {
    uint64_t size;
    uint32_t flags;
    uint32_t type;
    unsigned char value[512]; // value stored locally in header if small enough
    int map_channels;         // number of mapped channels (0 = no channel mapping)
    int channel_map[256];     // channel routing array (stored inline to avoid separate shm segment)
} astrid_shared_resource_header_t;

/* A handle for a shared memory resource. Only used for large values. */
typedef struct astrid_shared_resource_t {
    astrid_shared_resource_header_t header;
    char lock_name[LPMAXPATH];
    sem_t * lock;         // resource lock -- skipped for header-only reads
    MDB_txn * txn;        // private LMDB write transaction
    unsigned char * data; // mmapped pointer to POSIX shm for large objects
    size_t mapped_size;   // actual size mmapped (for correct munmap)
} astrid_shared_resource_t;

/* A handle for a message queue. The queue ringbuf and buffer are 
 * stored in shared memory and support multiple producers and a single consumer */
typedef struct lpmsgq_t {
    char name[LPMAXKEY];
    int is_producer; // ==1 for producers
    astrid_shared_resource_t ringbuf_r; // shm for ringbuf_t
    astrid_shared_resource_t buffer_r;  // shm for data buffer
    ringbuf_t * rb;   // mapped on msgq_init
    lpmsg_t * buffer; // mapped on msgq_init
    ringbuf_worker_t * w; // assigned on msgq_produce
} lpmsgq_t;

/* A handle to the LMDB session shared across all astrid instruments */
typedef struct astrid_session_t {
    char instrument_name[LPMAXNAME];
    char lock_name[LPMAXPATH]; // session lock: POSIX sempahore which guards the LMDB writes
    char datapath[PATH_MAX];   // the XDG config dir where LMDB sessions live
    sem_t * lock;              // session lock: convenience for LMDB writes
    MDB_env * dbenv;
    MDB_dbi dbi;
    MDB_txn * dbtxn_read;      // this transaction is held and renewed for optimized reads
    size_t buffer_count;

    // inboxes for external communication
    mqd_t inbox_messages; // POSIX message inbox from other instruments or processes
                          // TODO: could support other input frontends, like a file
                          // descriptor and network messages, etc
} astrid_session_t;


/* These events are what is stored in the 
 * scheduler's linked lists where it tracks 
 * which buffers are queued, playing, and 
 * completed, and which have pending callbacks.
 * */
typedef struct lpevent_t {
    size_t id;
    char buffer_code[LPMAXKEY];
    astrid_shared_resource_t resource;
    lpbuffer_t * buf;
    size_t pos;
    size_t onset;
    void * next;
    void (*callback)(lpmsg_t msg);
    lpmsg_t msg;
    size_t callback_onset;
    int callback_fired;
    int channel_map[256];  // Channel remapping: src channel index for each dest channel
    int map_channels;      // Number of channels in the map (0 = no mapping)
} lpevent_t;

/* This is the async render buffer playback scheduler */
typedef struct lpscheduler_t {
    lpfloat_t * current_frame;
    int channels;
    int realtime;
    lpfloat_t samplerate;
    struct timespec * init;
    struct timespec * now;
    size_t ticks;
    size_t tick_ns;
    size_t event_count;
    size_t numzeros;
    lpfloat_t last_sum;
    lpevent_t * waiting[ASTRID_MAX_WAITING_BUFFERS];
    int last_waiting_removed;
    int last_waiting_added;
    int num_waiting; // Count of buffers in waiting queue (for circular buffer handling)
    lpevent_t * playing_stack_head;

    // Lock-free nursery ringbuf for finished events cleanup
    ringbuf_t * nursery_ringbuf;
    lpevent_t ** nursery_buffer;
    ringbuf_worker_t * nursery_worker;
} lpscheduler_t;

/* Used to provide configuration defaults on instruments */
typedef struct lpinstrument_config_t {
    char * name; // FIXME use a static buffer for all names
    int input_channels;
    int output_channels;
    lpfloat_t initial_volume;
    lpfloat_t requested_samplerate; // TODO use jack API to adjust samplerate here
    lpfloat_t adc_length;
    lpfloat_t resampler_length;
    int ext_relay_enabled;
    int is_interactive;
    lpfloat_t bpm;
    void * ctx;
    int udp_port;
    char * midiin_device_names[ASTRID_MAX_MIDI_DEVICES];
    int num_midiin_device_names;
    char * midiout_device_names[ASTRID_MAX_MIDI_DEVICES];
    int num_midiout_device_names;
    int (*stream_callback)(size_t blocksize, float ** input, float ** output, void * instrument);
    int (*post_init_callback)(void * instrument);
    int (*renderer_callback)(void * instrument);
    int (*update_callback)(void * instrument, char * key, char * val);
    int (*midi_callback)(void * instrument, unsigned char device_index, unsigned char mtype, unsigned char mid, unsigned char mval);
    int (*trigger_callback)(void * instrument);
} lpinstrument_config_t;

/* A simple ugen graph */
typedef struct astrid_graph_t {
    size_t num_nodes;                        // Number of ugens in the graph
    ugen_t * nodes[ASTRID_GRAPH_MAX_NODES]; // Array of ugen pointers (connections stored in ugens themselves)
    ugen_t * output_node;                    // Main output node
    float output_gain;                       // Main output gain
} astrid_graph_t;

/* The main instrument struct, holds references to all callbacks and threads */
typedef struct lpinstrument_t {
    char * name;
    int input_channels;
    int output_channels;
    int is_interactive;
    lpfloat_t initial_volume;
    volatile int is_running; // threads, pools, loops, etc
    volatile int is_waiting; // for lpmsg_t messages
    volatile int is_ready;   // for console commands
    int has_been_initialized;
    lpfloat_t samplerate;

    // The LMDB / shared memory session handles for this instrument
    astrid_session_t session;

    // linenoise cmd buf
    struct linenoiseState cmdstate;
    char cmdbuf[1024];

    uint32_t param_volume;
    uint32_t param_trigger_reset;
    uint32_t param_period_in_ticks;
    uint32_t param_offset_in_ticks;
    uint32_t param_last_trigger_time;

    // The ringbuf names
    char adcname[PATH_MAX];
    char resamplername[PATH_MAX];

    int ext_relay_enabled;

    lpmsg_t msg;
    lpmsg_t cmd;

    char * midiin_device_names[ASTRID_MAX_MIDI_DEVICES];
    int midiin_device_ids[ASTRID_MAX_MIDI_DEVICES];
    int num_midiin_devices;
    char * midiout_device_names[ASTRID_MAX_MIDI_DEVICES];
    int midiout_device_ids[ASTRID_MAX_MIDI_DEVICES];
    int num_midiout_devices;

    int udp_port;
    int udp_is_enabled;
    pthread_t udp_listener_thread;

    // Message scheduling pq nodes
    pqueue_t * msgpq;
    lpmsgpq_node_t * pqnodes;
    int pqnode_index;

    // Thread refs
    pthread_t cleanup_thread;
    pthread_t autotrigger_thread;
    pthread_t audio_slow_lane_thread;
    pthread_t message_feed_thread;
    pthread_t midi_listener_thread;
    pthread_t midi_output_threads[ASTRID_MAX_MIDI_DEVICES];
    pthread_t message_scheduler_pq_thread;
    pthread_t posix_inbox_thread;
    lpscheduler_t * async_mixer;
    lpbuffer_t * lastbuf;

    pthread_mutex_t emergency_brake;

    // Jack refs
    jack_port_t ** inports;
    jack_port_t ** outports;
    jack_client_t * jack_client;
    jack_ringbuffer_t * jack_input_ringbuffer;
    jack_ringbuffer_t * jack_output_ringbuffer;

    // Optional local context struct for callbacks
    void * context;

    // Trigger update callback
    int (*trigger)(void * instrument);

    // Param update callback
    int (*update)(void * instrument, char * key, char * val);

    // MIDI update callback
    int (*midievent)(void * instrument, unsigned char device_index, unsigned char mtype, unsigned char mid, unsigned char mval);

    // Async renderer callback (C-compat only)
    int (*renderer)(void * instrument);

    // Stream callback
    int (*stream)(size_t blocksize, float ** input, float ** output, void * instrument);

    // Shutdown signal handler (SIGTERM & SIGKILL)
    void (*shutdown)(int sig);
    
    volatile astrid_graph_t * current_graph;  // Currently active graph (processed in Jack callback)
    volatile astrid_graph_t * new_graph;      // New graph waiting to be swapped in
    volatile int graph_swap_ready;            // Flag: new graph is ready for swap
    volatile int graph_cleanup_ready;         // Flag: old graph is ready for cleanup
} lpinstrument_t;

/* This is deprecated but was previously used to hold a set of params in a session */
typedef struct lpparamset_t {
   u_int32_t keys[ASTRID_MAX_PARAMS]; 
   u_int32_t types[ASTRID_MAX_PARAMS];
   int num_params;
} lpparamset_t;

/* A nice interface for C instruments and others to use */
typedef struct astrid_session_factory_t {
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
} astrid_session_factory_t;

extern const astrid_session_factory_t AstridSession;

/* This probably can be deprecated, we're not using it faithfully now */
static const size_t astrid_shared_type_sizes[] = {
    sizeof(lpfloat_t),                                 // float
    sizeof(lpint_t),                                   // int
    sizeof(char) * LPMAXMSG,                           // string
    sizeof(char) * LPMAXKEY,                           // name/key
    sizeof(char) * LPMAXPATH,                          // path
    sizeof(lpmsg_t),                                   // message
    0,                                                 // MUSTARD
    0, //sizeof(lppatternbuf_t),                            // pattern
    0, //sizeof(lpautotrigger_t) * ASTRID_MAX_AUTOTRIGGERS, // triggers
    0, //sizeof(lpinstrument_t),                            // instrument
    0,                                                 // (variable) buffer
    0,                                                 // (variable) array
    0                                                  // (variable) bytes
};

#ifdef ASTRID_GUI_ENABLED
/* In-progress GUI APIs */
enum AstridGUITypes {
    ASTRID_GUI_EMPTY,
    ASTRID_GUI_WAVEFORM,
    ASTRID_GUI_NUM_TYPES
};

typedef struct lpgui_waveform_widget_t {
    char name[LPMAXKEY]; /* shared resource name */
    astrid_shared_resource_t resource;
} lpgui_waveform_widget_t;

typedef struct lpgui_t {
    char name[LPMAXNAME];
    int width;
    int height;
    int type;
    lpfloat_t font_size;
    lpfloat_t mouse_x;
    lpfloat_t mouse_y;

    astrid_session_t session;

    // widgets
    lpgui_waveform_widget_t waveform;

    GtkWidget * window;
    GtkWidget * container; // for menu & canvas
    GtkWidget * canvas;
    GtkWidget * menubar;
    GtkWidget * fileMenu;
    GtkWidget * fileMenuItem;
    GtkWidget * quitMenuItem;
} lpgui_t;
#endif

typedef struct lpmidiout_device_t {
    lpinstrument_t * instrument;
    int device_id;
    int device_index;
} lpmidiout_device_t;

#endif
