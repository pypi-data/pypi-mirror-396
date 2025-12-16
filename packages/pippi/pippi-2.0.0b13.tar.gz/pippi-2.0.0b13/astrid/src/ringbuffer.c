#include <stdatomic.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define RINGBUFFER_SIZE 256

typedef struct {
    uint8_t data[RINGBUFFER_SIZE];
} ringbuffer_t;

typedef struct {
    ringbuffer_t *buffer;
    atomic_uint_least32_t head;
    atomic_uint_least32_t tail;
} ringbuffer_state_t;

bool ringbuffer_init(ringbuffer_state_t *state, ringbuffer_t *buffer) {
    if (!state || !buffer) {
        return false;
    }

    state->buffer = buffer;
    state->head = 0;
    state->tail = 0;

    return true;
}

bool ringbuffer_write(ringbuffer_state_t *state, uint8_t data) {
    if (!state) {
        return false;
    }

    uint32_t head = atomic_load_explicit(&state->head, memory_order_relaxed);
    uint32_t next_head = (head + 1) % RINGBUFFER_SIZE;
    if (next_head == atomic_load_explicit(&state->tail, memory_order_acquire)) {
        // buffer is full
        return false;
    }

    state->buffer->data[head] = data;
    atomic_store_explicit(&state->head, next_head, memory_order_release);

    return true;
}

bool ringbuffer_read(ringbuffer_state_t *state, uint8_t *data) {
    if (!state || !data) {
        return false;
    }

    uint32_t tail = atomic_load_explicit(&state->tail, memory_order_relaxed);
    if (tail == atomic_load_explicit(&state->head, memory_order_acquire)) {
        // buffer is empty
        return false;
    }

    *data = state->buffer->data[tail];
    atomic_store_explicit(&state->tail, (tail + 1) % RINGBUFFER_SIZE, memory_order_release);

    return true;
}
