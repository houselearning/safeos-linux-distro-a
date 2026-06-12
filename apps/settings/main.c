#include "../common/safeos_app.h"
#include "main.h"

int settings_main(void) {
    return safeos_app_run("Settings");
}

int main(void) {
    return settings_main();
}
