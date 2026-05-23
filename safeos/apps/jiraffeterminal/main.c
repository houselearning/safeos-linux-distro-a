#include "../common/safeos_app.h"
#include "main.h"

int jiraffeterminal_main(void) {
    return safeos_app_run("Jiraffeterminal");
}

int main(void) {
    return jiraffeterminal_main();
}
