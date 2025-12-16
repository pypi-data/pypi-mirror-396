#include "astrid.h"

int main() {
    int device_id;
    device_id = lpmidi_get_device_id_by_name("Faderfox MX12");
    printf("device id %d\n", device_id);
    return 0;
}
