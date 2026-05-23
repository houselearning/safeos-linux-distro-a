#include "../common/safeos_app.h"
#include "main.h"

int camera_main(void) {
    return safeos_app_run("Camera");
}

int main(void) {
    return camera_main();
}
