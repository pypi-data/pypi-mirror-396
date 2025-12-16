#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <syslog.h>
#include <errno.h>
#include <time.h>

// Assuming these are defined in astrid.h
#include "astrid.h"

// Define constants if they're not already included
#ifndef LPMAXPATH
#define LPMAXPATH 256
#endif

#ifndef ASTRID_TYPE_BUFFER
#define ASTRID_TYPE_BUFFER 5  // Assuming this is the buffer type based on the code
#endif

#ifndef ASTRID_TYPE_MUSTARD
#define ASTRID_TYPE_MUSTARD 3  // From the code, this seems to be the dividing line
#endif

// Mock functions if they're not defined elsewhere
#ifndef HAVE_LPFILTERNAN
float lpfilternan(float value) {
    return value;  // For testing purposes
}
#endif

// For testing
void print_buffer_info(lpbuffer_t *buffer) {
    printf("Buffer Info:\n");
    printf("  Length: %zu frames\n", buffer->length);
    printf("  Channels: %d\n", buffer->channels);
    printf("  Samplerate: %d Hz\n", buffer->samplerate);
    printf("  Position: %zu\n", buffer->pos);
    printf("  First sample value: %f\n", buffer->data[0]);
}

int main(int argc, char *argv[]) {
    // Initialize logging
    openlog("session-buffer-test", LOG_PERROR | LOG_PID, LOG_USER);
    syslog(LOG_INFO, "Starting session buffer test");
    
    // Create a session
    astrid_session_t session;
    memset(&session, 0, sizeof(astrid_session_t));
    
    // Set up session name
    snprintf(session.instrument_name, LPMAXPATH, "test-session-%d", getpid());
    printf("Session name: %s\n", session.instrument_name);
    
    // Open the session
    if (astrid_session_open(&session) < 0) {
        syslog(LOG_ERR, "Failed to open session");
        return 1;
    }
    printf("Session opened successfully\n");
    
    // Create a test buffer name
    char buffer_name[LPMAXPATH];
    snprintf(buffer_name, LPMAXPATH, "test-buffer-%d", (int)time(NULL));
    printf("Buffer name: %s\n", buffer_name);
    
    // Create an empty sound buffer (lpbuffer_t)
    const size_t buffer_frames = 1024;
    const int channels = 2;
    const int samplerate = 44100;
    
    size_t buffer_size = sizeof(lpbuffer_t) + (buffer_frames * channels * sizeof(float));
    lpbuffer_t *test_buffer = (lpbuffer_t *)malloc(buffer_size);
    if (!test_buffer) {
        syslog(LOG_ERR, "Failed to allocate buffer memory");
        astrid_session_close(&session);
        return 1;
    }
    
    // Initialize the buffer
    memset(test_buffer, 0, buffer_size);
    test_buffer->length = buffer_frames;
    test_buffer->channels = channels;
    test_buffer->samplerate = samplerate;
    test_buffer->is_looping = 1;
    test_buffer->onset = 0;
    test_buffer->phase = 0.0f;
    test_buffer->pos = 0;
    test_buffer->boundry = buffer_frames - 1;
    test_buffer->range = buffer_frames;
    
    // Set a test value in the first sample
    test_buffer->data[0] = 0.5f;
    
    print_buffer_info(test_buffer);
    
    // Register the buffer with the session
    printf("Registering buffer to session...\n");
    if (astrid_session_register_shared_resource(&session, buffer_name, test_buffer, 
                                               ASTRID_TYPE_BUFFER, buffer_size) < 0) {
        syslog(LOG_ERR, "Failed to register shared resource");
        free(test_buffer);
        astrid_session_close(&session);
        return 1;
    }
    printf("Buffer registered successfully\n");
    
    // Now read it back using acquire/release
    printf("Acquiring buffer from session...\n");
    astrid_shared_resource_t resource;
    
    if (astrid_session_aquire_shared_resource(&session, &resource, buffer_name) < 0) {
        syslog(LOG_ERR, "Failed to acquire shared resource");
        free(test_buffer);
        astrid_session_close(&session);
        return 1;
    }
    printf("Buffer acquired successfully\n");
    
    // Check that we got the buffer back correctly
    lpbuffer_t *acquired_buffer = (lpbuffer_t *)resource.data;
    printf("Acquired buffer info:\n");
    print_buffer_info(acquired_buffer);
    
    // Release the resource
    printf("Releasing buffer...\n");
    if (astrid_session_release_shared_resource(&session, &resource, buffer_name) < 0) {
        syslog(LOG_ERR, "Failed to release shared resource");
        free(test_buffer);
        astrid_session_close(&session);
        return 1;
    }
    printf("Buffer released successfully\n");
    
    // Now destroy the resource
    printf("Destroying buffer...\n");
    if (astrid_session_destroy_shared_resource(&session, buffer_name) < 0) {
        syslog(LOG_ERR, "Failed to destroy shared resource");
        free(test_buffer);
        astrid_session_close(&session);
        return 1;
    }
    printf("Buffer destroyed successfully\n");
    
    // Clean up
    free(test_buffer);
    astrid_session_close(&session);
    printf("Session closed\n");
    
    syslog(LOG_INFO, "Test completed successfully");
    closelog();
    
    return 0;
}
