#ifndef LPASTRIDCONSTANTS_H
#define LPASTRIDCONSTANTS_H

#define NSEC_PER_SEC 1000000000 // 1_000_000_000
#define USEC_PER_SEC 1000000    // 1_000_000
#define NUM_NODES 4096
#define NUM_RENDERERS 10
#define ASTRID_CHANNELS 2
#define ASTRID_SAMPLERATE 48000

#define TOKEN_PROJECT_ID 'x'
#define LPIPC_PERMS (S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP)

#define ASTRID_GRAPH_MAX_NODES 64          // Maximum nodes per graph

#define ASTRID_MAX_WAITING_BUFFERS 40960
#define ASTRID_MAX_NURSERY_EVENTS 256      // Maximum events in cleanup nursery ringbuf
#define ASTRID_MAX_AUTOTRIGGERS 256
#define ASTRID_MAX_AUTOTRIGGER_SUBEVENTS 256
#define ASTRID_MQ_MAXMSG 10 // POSIX qs
#define ASTRID_MAX_MSGQ 512 // internal shm q (was 32, increased to handle high event rates)
#define ASTRID_MAX_MIDI_DEVICES 4  // Maximum MIDI input devices per instrument
#define ASTRID_MAX_MSGQ_WORKERS 64  // 30 Python workers + C threads + headroom
#define ASTRID_MSGQ_BUFSIZE (ASTRID_MAX_MSGQ * sizeof(lpmsg_t) * 2)


/* queue paths */
#define LPPLAYQ "/astridq"
#define ASTRID_MSGQ_PATH "/astrid-msgq"
#define LPMAXQNAME (12 + 1 + LPMAXNAME)

#define ASTRID_SESSIONDB_PATH "/tmp/astrid_session.db"
#define ASTRID_MIDI_TRIGGERQ_PATH "/tmp/astrid-miditriggerq"
#define ASTRID_MIDI_CCBASE_PATH "/tmp/astrid-mididevice%d-cc%d"
#define ASTRID_MIDI_NOTEBASE_PATH "/tmp/astrid-mididevice%d-note%d"
#define ASTRID_MIDIMAP_NOTEBASE_PATH "/tmp/astrid-midimap-device%d-note%d"
#define ASTRID_IPC_IDBASE_PATH "/tmp/astrid-idfile-%s"

#define ASTRID_SERIAL_CTLBASE_PATH "/tmp/astrid-serialdevice%d-ctl%d"

#define ASTRID_SESSION_SNAPSHOT_NAME "/astrid-session-snapshot"

#define LPMAXNAME 16 // instrument name
#define LPMAXKEY 64

// The total message size target == sizeof(lpmsg_t)
#define LPMSGSIZE 1024 

// max message payload size
#define LPMAXMSG (LPMSGSIZE - (sizeof(double) * 2) - (sizeof(size_t) * 4) - (sizeof(uint16_t) * 2) - LPMAXNAME)
#define LPMAXPATH PATH_MAX
#define LPMAXPAT 512 - sizeof(size_t)
#define LPMAXCHANNELS 32 /* used for temp storage for channel mapping, mostly. can be bumped up. should be only limited by hardware, really. */

#define LPKEY_MAXLENGTH 4096
#define ASTRID_MAX_CMDLINE 4096
#define ASTRID_MAX_PARAMS 4096

#ifndef NOTE_ON
#define NOTE_ON 0x90
#endif

#ifndef NOTE_OFF
#define NOTE_OFF 0x80
#endif

#ifndef CONTROL_CHANGE
#define CONTROL_CHANGE 0xB0
#endif

#ifndef PROGRAM_CHANGE
#define PROGRAM_CHANGE 0xC0
#endif

#define SEPARATOR 31
#define SPACE ' '

#define ASTRID_DEVICEID_PATH "/tmp/astrid_device_id"

#ifndef LMDB_LOCATION
#define LMDB_LOCATION "/tmp/astrid.db"
#endif

#ifndef LMDB_MAPSIZE
#define LMDB_MAPSIZE (2LL * 1024 * 1024 * 1024) // 2GB session size by default
#endif

/* MESSAGES */
#define PLAY_MESSAGE 'p'
#define UPDATE_MESSAGE 'u'
#define TRIGGER_MESSAGE 't'
#define UDP_MESSAGE 'n' // n for network...
#define SCHEDULE_MESSAGE 's'
#define LOAD_MESSAGE 'l'
#define SHUTDOWN_MESSAGE 'q'
#define SET_COUNTER_MESSAGE 'v' // FIXME what was this even for?
#define AUTOTRIGGER_UPDATE_MESSAGE 'a'
#define AUTOTRIGGER_REPLACE_MESSAGE 'A'

enum MainMQProducers {
    MAINMQ_MAIN_PRODUCER, // calls from the main foreground thread
    MAINMQ_C_INSTRUMENT_PRODUCER, // the main instrument message thread
    MAINMQ_PY_INSTRUMENT_PRODUCER, // the python message inbox / relay
    MAINMQ_AUTOTRIGGER_PRODUCER,
    MAINMQ_SCHEDULER_PRODUCER,
    MAINMQ_UDP_PRODUCER, 
    MAINMQ_MIDI_PRODUCER, 
    MAINMQ_POSIX_INBOX_PRODUCER,
    MAINMQ_RENDER_CALLBACK_PRODUCER, // C instrument render callbacks
    NUM_MAINMQ_PRODUCERS // This plus comrade ID becomes the producer ID for external renderer pools (+30 for python instruments)
};

enum LPMessageTypes {
    LPMSG_EMPTY,
    LPMSG_PLAY,
    LPMSG_TRIGGER,
    LPMSG_AUTOTRIGGER_REPLACE_ALL,
    LPMSG_AUTOTRIGGER_UPDATE,
    LPMSG_UPDATE,
    LPMSG_SERIAL, // TODO: reimplement tty writer
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
};

enum LPMessageFlags {
    LPFLAG_NONE            =0,
    LPFLAG_IS_SCHEDULED    =1 << 0,
    LPFLAG_IS_ENCODED_PARAM=1 << 1,
    LPFLAG_IS_FLOAT_ENCODED=1 << 2,
    LPFLAG_IS_INT32_ENCODED=1 << 3
};

enum LPParamTypes {
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
};

enum AstridSharedTypes {
    ASTRID_TYPE_FLOAT,      // sizeof(lpfloat_t)
    ASTRID_TYPE_INT,        // sizeof(lpint_t)
    ASTRID_TYPE_STRING,     // sizeof(char) * LPMAXMSG
    ASTRID_TYPE_NAME,       // sizeof(char) * LPMAXNAME
    ASTRID_TYPE_PATH,       // sizeof(char) * LPMAXPATH
    ASTRID_TYPE_MESSAGE,    // sizeof(lpmsg_t)
    ASTRID_TYPE_MUSTARD,    // CUT THE MUSTARD -- LMDB storage above, POSIX below
    ASTRID_TYPE_PATTERN,    // sizeof(lppatternbuf_t)
    ASTRID_TYPE_TRIGGERS,   // sizeof(lpautotrigger_t) * ASTRID_MAX_AUTOTRIGGERS
    ASTRID_TYPE_INSTRUMENT, // sizeof(lpinstrument_t)
    ASTRID_TYPE_BUFFER,     // lpbuffer_t
    ASTRID_TYPE_ARRAY,      // lparray_t
    ASTRID_TYPE_BYTES,      // some arbitrary object
    ASTRID_TYPE_NONE,       // returned when the resource doesn't exist
    NUMSHAREDTYPES
};

enum AstridSharedFlags {
    ASTRID_FLAG_NONE = 0,
    ASTRID_FLAG_VALUE_STORED_IN_HEADER = (1 << 0),
    NUMFLAGS
};


#endif
