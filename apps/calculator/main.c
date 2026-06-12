#include "../common/safeos_app.h"
#include "main.h"

int calculator_main(void) {
    return safeos_app_run("Calculator");
}

int main(void) {
    return calculator_main();
}
