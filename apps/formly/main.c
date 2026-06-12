#include "../common/safeos_app.h"
#include "main.h"

int formly_main(void) {
    return safeos_app_run("Formly");
}

int main(void) {
    return formly_main();
}
