#include "../common/safeos_app.h"
#include "main.h"

int orbitalcode_main(void) {
    return safeos_app_run("Orbitalcode");
}

int main(void) {
    return orbitalcode_main();
}
