#include "../common/safeos_app.h"
#include "main.h"

int safebrowser_main(void) {
    return safeos_app_run("Safebrowser");
}

int main(void) {
    return safebrowser_main();
}
