# SafeShell and JiraffeScript status

The image's Terminal launcher opens Debian's standard XFCE terminal and Bash. SafeShell and JiraffeScript are not implemented as a command interpreter or security boundary.

`jiraffe_shell.sh` starts a standard login Bash session. `jiraffescript.py` exits with an explicit unavailable message and does not parse or execute script files. No custom admin command, VM control, policy enforcement, or command filtering is provided.
