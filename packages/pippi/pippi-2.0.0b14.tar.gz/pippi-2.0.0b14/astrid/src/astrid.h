#ifndef LPASTRID_H
#define LPASTRID_H

#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <assert.h>
#include <errno.h>
#include <locale.h>
#include <limits.h>
#include <math.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <wchar.h>
#include <unistd.h>

#include <sys/random.h>

#include <arpa/inet.h>
#include <ctype.h>
#include <stdatomic.h>
#include <fcntl.h>
#include <mqueue.h>
#include <netinet/in.h>
#include <netdb.h>
#include <pthread.h>
#include <signal.h>
#include <sys/mman.h>
#include <sys/file.h>
#include <sys/syscall.h>
#include <semaphore.h>
#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/shm.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/socket.h>
#include <syslog.h>
#include <time.h>
#include <termios.h>
#include <unistd.h>
#include <linux/futex.h>

#include "lmdb.h"
#include "midl.h"
#include "ringbuf.h"

#include "linenoise.h"
#include "pqueue.h"
#include <jack/jack.h>
#include <jack/ringbuffer.h>
#include <alsa/asoundlib.h>

#ifdef ASTRID_GUI_ENABLED
#include <gtk/gtk.h>
#endif

#include "pippi.h"
#include "astridconstants.h"
#include "astridtypes.h"
#include "session.h"
#include "ugens.core.h"
#include "ugens.adc.h"
#include "ugens.mix.h"

void scheduler_schedule_event(astrid_session_t * session, lpscheduler_t * s, char * buffer_code, size_t delay);
void lpscheduler_tick(lpscheduler_t * s);
lpscheduler_t * scheduler_create(int, int, lpfloat_t);
void scheduler_destroy(lpscheduler_t * s);
int lpscheduler_get_now_seconds(double * now);
int lpscheduler_get_now_ticks(size_t * now, int samplerate);
int scheduler_cleanup_nursery(astrid_session_t * session, lpscheduler_t * s);

unsigned char * serialize_buffer(lpbuffer_t * buf, lpmsg_t * msg, size_t * strsize); 
lpbuffer_t * deserialize_buffer(char * buffer_code, lpmsg_t * msg); 

int parse_message_from_args(int argc, int arg_offset, char * argv[], lpmsg_t * msg);
int parse_message_from_cmdline(char * cmdline, size_t cmdlength, lpmsg_t * msg);
int parse_message_from_external_cmdline(char * cmdline, lpmsg_t * msg);

int decode_update_message_param(lpmsg_t * msg, uint16_t * id, float * value);
int encode_update_message_param(lpmsg_t * msg);

int init_instrument_message(lpmsg_t * msg, char * instrument_name);
int astrid_queue_send_message(mqd_t q, lpmsg_t msg);
int send_message(char * qname, lpmsg_t msg);
int send_play_message(lpmsg_t msg);
int get_play_message(char * instrument_name, lpmsg_t * msg);

mqd_t astrid_playq_open(const char * instrument_name);
int astrid_playq_read(mqd_t mqd, lpmsg_t * msg);
int astrid_playq_close(mqd_t mqd);

mqd_t astrid_posix_msgq_open(char * qname);
mqd_t astrid_posix_msgq_open_read(char * qname);
int astrid_posix_msgq_close(mqd_t mqd);
int astrid_posix_msgq_read(mqd_t mqd, lpmsg_t * msg);

int astrid_msgq_init(astrid_session_t * session, char * qname);
lpmsgq_t * astrid_msgq_produce(astrid_session_t * session, char * qname, int producer_id);
lpmsgq_t * astrid_msgq_consume(astrid_session_t * session, char * qname);
void astrid_msgq_close(lpmsgq_t * q);
int astrid_msgq_read(lpmsgq_t * q, lpmsg_t * msg);
int astrid_msgq_write(lpmsgq_t * q, lpmsg_t * msg);

/* TODO all this goes into LMDB */
int lpmidi_setcc(astrid_session_t * session, int device_id, int channel, int cc, int value);
int lpmidi_getcc(astrid_session_t * session, int device_id, int channel, int cc);
int lpmidi_setnote(astrid_session_t * session, int device_id, int channel, int note, int velocity);
int lpmidi_getnote(astrid_session_t * session, int device_id, int channel, int note);

/* in-progress MIDI APIs */
int lpmidi_relay_to_instrument(lpinstrument_t * instrument, lpmsgq_t * msgq, unsigned char device_index, unsigned char mtype, unsigned char mid, unsigned char mval);
int lpmidi_encode_eventbytes(unsigned char buf[3], int channel, unsigned char message_type, int param, int value);
int lpmidi_decode_eventbytes(char * payload, unsigned char * device_index, unsigned char * mtype, unsigned char * mid, unsigned char * mval);
int lpmidi_encode_msg(lpmsg_t * msg, int channel, unsigned char message_type, int param, int value);
int lpmidi_get_device_id_by_name(const char * device_name);

int astrid_jack_ringbuffer_write_block(jack_ringbuffer_t * rb, lpbuffer_t * buf, size_t numframes);
int astrid_jack_ringbuffer_read_block(jack_ringbuffer_t * rb, lpbuffer_t * buf, size_t numframes);

int astrid_write_ringbuffer_block(lpbuffer_t * buf, float ** block, int channels, size_t blocksize_in_frames);
int astrid_read_ringbuffer_block(lpbuffer_t * buf, size_t offset_in_frames, lpbuffer_t * out);

void lptimeit_since(struct timespec * start);

lpinstrument_t * astrid_instrument_start(
        char * name, 
        int input_channels, 
        int output_channels, 
        int ext_relay_enabled, 
        double adc_length, 
        double resampler_length, 
        void * ctx, 
        char ** midiin_device_names, 
        int num_midiin_device_names,
        char ** midiout_device_names, 
        int num_midiout_device_names,
        int (*stream)(size_t blocksize, float ** input, float ** output, void * instrument), 
        int (*renderer)(void * instrument), 
        int (*update)(void * instrument, char * key, char * val), 
        int (*trigger)(void * instrument)
    );

int astrid_split_port_names(char * cmd, char * a, char * b);

lpinstrument_config_t astrid_instrument_init_config(char * name);
lpinstrument_t * astrid_instrument_start_from_config(lpinstrument_config_t config);
lpinstrument_t * astrid_instrument_start_from_config_with_ptr(lpinstrument_config_t config, lpinstrument_t * instrument);
int astrid_instrument_connect(lpinstrument_t * instrument, char * cmd);
int astrid_instrument_disconnect(lpinstrument_t * instrument, char * cmd);
int astrid_instrument_stop(lpinstrument_t * instrument);

int send_render_to_mixer(lpinstrument_t * instrument, lpbuffer_t * buf);

#ifdef ASTRID_GUI_ENABLED
lpgui_t * astrid_gui_init(char * name, int width, int height);
int astrid_gui_config_waveform(lpgui_t * gui, char * buffer_name);
int astrid_gui_run_forever(lpgui_t * gui);
int astrid_gui_destroy(lpgui_t * gui);
#endif

int astrid_autotrigger_init(lpautotrigger_t * at);
int astrid_autotrigger_add_onset(lpautotrigger_t * at, size_t onset_time, size_t period, lpfloat_t speed, char * cmd);
int astrid_autotrigger_table_get_free_slot(lpautotrigger_table_t * att);
int astrid_autotrigger_table_clear(lpautotrigger_table_t * att);
int astrid_autotrigger_update_speed(lpautotrigger_t * at, lpfloat_t speed);
int astrid_autotrigger_update_onset_value(lpautotrigger_t * at, int onset_index, size_t onset_frames);
int astrid_autotrigger_update_onset_cmd(lpautotrigger_t * at, int onset_index, char * cmd);
int astrid_autotrigger_update_all_cmds(lpautotrigger_t * at, char * cmd);

int astrid_instrument_process_param_updates(lpinstrument_t * instrument);
int astrid_instrument_tick(lpinstrument_t * instrument);
astrid_graph_t * astrid_graph_create_from_message(lpmsg_t msg, astrid_session_t * session);
int astrid_instrument_update_graph(lpinstrument_t * instrument);
int astrid_instrument_python_graph_stream_callback(size_t blocksize, float ** input, float ** output, void * instrument);
int relay_message_to_seq(lpinstrument_t * instrument, lpmsg_t msg);
int astrid_schedule_message(lpinstrument_t * instrument, lpmsg_t msg);

int extract_int32_from_token(char * token, int32_t * val);
int extract_float_from_token(char * token, float * val);
int extract_floatlist_from_token(char * tokenlist, lpfloat_t * val, int size);
int extract_patternbuf_from_token(char * token, unsigned char * patternbuf, size_t * pattern_length);

int lpencode_with_prefix(char * prefix, size_t val, char * encoded);
size_t lpdecode_with_prefix(char * encoded);

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
int astrid_session_destroy_shared_resource_fast(astrid_session_t * session, char * name);
int astrid_resize_aquired_shared_resource(astrid_shared_resource_t * resource, size_t new_size);

int astrid_session_get_info(astrid_session_t * session, char * key, astrid_shared_resource_header_t * header);
size_t astrid_session_get_size(astrid_session_t * session, char * key);
uint32_t astrid_session_get_type(astrid_session_t * session, char * key);
lpint_t astrid_session_get_int(astrid_session_t * session, char * key);
int astrid_session_set_int(astrid_session_t * session, char * key, lpint_t val);
lpfloat_t astrid_session_get_float(astrid_session_t * session, char * key);
lpfloat_t astrid_session_get_float_from_hash(astrid_session_t * session, uint32_t key_hash);
int astrid_session_set_float(astrid_session_t * session, char * key, lpfloat_t val);
int astrid_session_set_float_from_hash(astrid_session_t * session, uint32_t key_hash, lpfloat_t val);
int astrid_session_exists(astrid_session_t * session, char * key);
int astrid_session_exists_from_hash(astrid_session_t * session, uint32_t key_hash);
int astrid_session_set_string(astrid_session_t * session, char * key, char * str);
int astrid_session_get_string(astrid_session_t * session, char * key, char * str);
int astrid_session_set_buffer(astrid_session_t * session, char * key, lpbuffer_t * buf);
lpbuffer_t * astrid_session_get_buffer(astrid_session_t * session, char * key);

int astrid_session_release_resource_lock(astrid_shared_resource_t * resource);
int astrid_session_aquire_resource_lock(astrid_shared_resource_t * resource, char * name);

int astrid_session_read_shared_ringbuffer_block(astrid_session_t * session, char * name, size_t offset_in_frames, lpbuffer_t * out); 
int astrid_session_write_lpbuffer_to_shared_ringbuffer(astrid_session_t * session, char * name, lpbuffer_t * src); 

void scheduler_debug(lpscheduler_t * s);
size_t safe_index(size_t i, ssize_t offset, int c, size_t length, int channels);

#endif
