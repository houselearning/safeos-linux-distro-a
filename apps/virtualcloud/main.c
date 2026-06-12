#include "../common/safeos_app.h"
#include "main.h"

int virtualcloud_main(void) {
    return safeos_app_run("Virtualcloud");
}

int main(void) {
    return virtualcloud_main();
}
