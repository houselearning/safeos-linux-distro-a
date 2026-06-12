#include "../common/safeos_app.h"
#include "main.h"

int krowdiagnostics_main(void) {
    return safeos_app_run("Krowdiagnostics");
}

int main(void) {
    return krowdiagnostics_main();
}
