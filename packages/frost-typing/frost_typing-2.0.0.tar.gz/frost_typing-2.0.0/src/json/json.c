#include "json/json.h"

int
json_setup(void)
{
    if (decoder_setup() < 0 || encoder_setup() < 0) {
        return -1;
    }
    return 0;
}

void
json_free(void)
{
    decoder_free();
    encoder_free();
}
