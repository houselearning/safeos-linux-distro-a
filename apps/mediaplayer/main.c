#include "../common/safeos_app.h"
#include "main.h"

int mediaplayer_main(void) {
    return safeos_app_run("Mediaplayer");
}

int main(void) {
    return mediaplayer_main();
}
