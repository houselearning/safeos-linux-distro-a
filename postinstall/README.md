# Postinstall

`first_boot.py` is the GTK first-run assistant included in the live image and started by XFCE autostart. Its SafeOS-specific shell uses the shield wallpaper, a six-step navigation rail, and locally branded colors rather than the stock GTK Assistant. `setup_wizard.sh` is its command-line entrypoint.

The assistant applies a local account, password hash through `chpasswd`, locale, keyboard layout, time zone, host name, and optional larger XFCE text. It uses NetworkManager's connection editor and supports continuing offline. The password is passed over a pipe to the system password service and is excluded from the setup record.

The completion record is `/var/lib/safeos/first-run.json`. It is stored on the current root filesystem. A normal live ISO session is ephemeral; this record and account changes survive reboot only when live persistence is configured. This project does not claim that Debian Installer installs the customized SafeOS live profile.

SafeCloud enrollment, Krow diagnostics, classroom-policy sync, recovery, and a SafeOS disk installer are not provided. They remain unavailable rather than being represented by simulated actions.
