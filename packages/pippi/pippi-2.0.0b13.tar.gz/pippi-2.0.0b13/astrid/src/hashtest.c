#include "astrid.h"

int main(int argc, char * argv[]) {
    if(argc < 1) return 1;
    printf("hash src: %s\n", argv[1]);
    printf("hash key %d\n", lphashstr(argv[1]));
    return 0;
}
