#include "../common/safeos_app.h"
#include "main.h"

int safepainter_main(void) {
    return safeos_app_run("Safepainter");
}

int main(void) {
    return safepainter_main();
}
