#include "../common/safeos_app.h"
#include "main.h"

int fileexplorer_main(void) {
    return safeos_app_run("Fileexplorer");
}

int main(void) {
    return fileexplorer_main();
}
