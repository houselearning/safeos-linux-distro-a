# Installation and first run

## First-run setup

The live XFCE session starts the SafeOS GTK assistant automatically until setup completes. It configures a local account, locale, keyboard layout, time zone, host name, and optional larger text. Wi-Fi and wired connections use NetworkManager; offline setup is allowed. Passwords are sent to `chpasswd` over stdin and are not written to the setup record.

The completion record is `/var/lib/safeos/first-run.json`. A normal live session is temporary and loses changes at reboot. Persistence requires a live-boot persistence store; this ISO does not create one automatically.

## Debian Installer

The image includes Debian Installer in live mode and the `debian-installer-launcher` desktop entry. It is the Debian installer, not a verified SafeOS image-to-disk installer. Review the selected target carefully: installation can destroy existing data. The custom SafeOS profile, setup state, and applications have not been verified after disk installation.

## Recovery

Boot the live medium to inspect or back up accessible files before attempting repair. No automated disk repair is provided. Reinstalling can overwrite the target disk; maintain an independent backup. Installed-system and physical-hardware recovery are not certified.
