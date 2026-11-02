#include "safeos_app.h"

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <unistd.h>

struct app_target {
    const char *name;
    const char *command;
    const char *argument;
};

static const struct app_target app_targets[] = {
    {"Safebrowser", "firefox-esr", NULL},
    {"Fileexplorer", "thunar", NULL},
    {"Calculator", "galculator", NULL},
    {"Spreadsheet", "libreoffice", "--calc"},
    {"Safewriter", "libreoffice", "--writer"},
    {"Safedeck", "libreoffice", "--impress"},
    {"Mediaplayer", "parole", NULL},
    {"Camera", "cheese", NULL},
    {"Settings", "xfce4-settings-manager", NULL},
    {"Jiraffeterminal", "xfce4-terminal", NULL},
    {"Orbitalcode", "geany", NULL},
};

int safeos_app_run(const char *name) {
    if (name == NULL) {
        fprintf(stderr, "SafeOS app name is required\n");
        return 64;
    }

    for (size_t index = 0; index < sizeof(app_targets) / sizeof(app_targets[0]); index++) {
        if (strcasecmp(name, app_targets[index].name) != 0) {
            continue;
        }

        char *arguments[] = {
            (char *)app_targets[index].command,
            (char *)app_targets[index].argument,
            NULL,
        };
        if (arguments[1] == NULL) {
            arguments[1] = NULL;
        } else {
            arguments[2] = NULL;
        }

        execvp(app_targets[index].command, arguments);
        int launch_error = errno;
        fprintf(stderr, "SafeOS app '%s' could not start '%s': %s\n",
            name, app_targets[index].command, strerror(launch_error));
        return launch_error == ENOENT ? 127 : 126;
    }

    fprintf(stderr, "SafeOS app '%s' is not implemented in this image\n", name);
    return 69;
}
