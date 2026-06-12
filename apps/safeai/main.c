#include "../common/safeos_app.h"
#include "main.h"

int safeai_main(void) {
    return safeos_app_run("Safeai");
}

int main(void) {
    return safeai_main();
}
