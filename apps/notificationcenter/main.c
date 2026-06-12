#include "../common/safeos_app.h"
#include "main.h"

int notificationcenter_main(void) {
    return safeos_app_run("Notificationcenter");
}

int main(void) {
    return notificationcenter_main();
}
