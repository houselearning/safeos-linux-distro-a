#include "../apps/common/safeos_app.h"

#include <stddef.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    if (safeos_app_run("SafeAI") != 69) {
        return 1;
    }
    if (safeos_app_run(NULL) != 64) {
        return 2;
    }

    pid_t child = fork();
    if (child < 0) {
        return 3;
    }
    if (child == 0) {
        _exit(safeos_app_run("SafeBrowser"));
    }

    int status = 0;
    if (waitpid(child, &status, 0) != child || !WIFEXITED(status) || WEXITSTATUS(status) != 42) {
        return 4;
    }
    return 0;
}