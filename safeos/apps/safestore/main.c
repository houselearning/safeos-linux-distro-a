#include "../common/safeos_app.h"
#include "main.h"

int safestore_main(void) {
    return safeos_app_run("Safestore");
}

int main(void) {
    return safestore_main();
}
