#include "../common/safeos_app.h"
#include "main.h"

int safewriter_main(void) {
    return safeos_app_run("Safewriter");
}

int main(void) {
    return safewriter_main();
}
