#include "../common/safeos_app.h"
#include "main.h"

int safedeck_main(void) {
    return safeos_app_run("Safedeck");
}

int main(void) {
    return safedeck_main();
}
