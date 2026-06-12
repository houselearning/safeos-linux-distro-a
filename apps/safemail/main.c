#include "../common/safeos_app.h"
#include "main.h"

int safemail_main(void) {
    return safeos_app_run("Safemail");
}

int main(void) {
    return safemail_main();
}
