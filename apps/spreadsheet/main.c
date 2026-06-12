#include "../common/safeos_app.h"
#include "main.h"

int spreadsheet_main(void) {
    return safeos_app_run("Spreadsheet");
}

int main(void) {
    return spreadsheet_main();
}
