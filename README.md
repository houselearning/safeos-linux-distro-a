# SafeOS

SafeOS is an experimental, x86_64 Debian Bookworm live/install image with XFCE. It includes a local desktop, package-backed application launchers, and the Debian Installer. It is not a managed-school platform and does not provide SafeCloud, surveillance, exam enforcement, malware scanning, or custom driver support.

## Goals
- Debian Bookworm amd64 live/install image for x86_64 PCs and virtual machines
- Windows 95/XP-inspired UI with ChromeOS-like simplicity
- XFCE desktop with Firefox ESR, Thunar, LibreOffice, Galculator, Parole, Cheese, Geany, local notifications, and XFCE utilities
- `safeos-update check|apply` for explicit APT-backed updates; no unattended updater or rollback
- `safeos-settings` for a small allowlisted set of user-local preferences
- GTK first-run setup for local account, locale, keyboard, time zone, host name, network editor, offline setup, and larger text
- Debian Installer entry for disk installation

## Key folders
- `iso/` — legacy repository artifacts; new builds are written to the external workspace
- `live-build/` — live-build customization inputs
- `scripts/` — build and validation helpers
- `branding/` — logos, splash text, identity assets
- `icons/` — app and desktop icon manifest
- `themes/` — desktop themes and palette hints
- `wallpapers/` — backgrounds and custom wallpaper metadata
- `desktop/` — desktop environment and session configs
- `safeshell/` — SafeShell and JiraffeScript tooling
- `safemenu/` — Action Bar and start-menu logic
- `safenotify/` — notification center and filtering helpers
- `apps/` — application wrappers; only explicitly mapped Debian applications are launchable
- `system/` — local prototypes and explicit unavailable-service boundaries
- `drivers/` — driver management manifests
- `postinstall/` — first-boot and setup workflows
- `docs/` — architecture, UX, boot, API, and build documentation

## Build and test

Build on macOS using the pinned Debian container and the dedicated external Colima profile. The profile must mount the external drive, and the Docker named volume holds the live-build tree and package cache. The release ISO, checksum, logs, and VM test results are stored under `/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/`.

```sh
docker --context colima-safeos-build run --rm --privileged \
	--volume safeos-build-workspace:/var/lib/safeos-build \
	--volume "/Volumes/Other Storage:/safeos" \
	--volume "$PWD:/src:ro" --workdir /src \
	--env SAFEOS_BUILD_ROOT=/var/lib/safeos-build/safeos-linux-distro-a \
	--env SAFEOS_RELEASE_DIR=/safeos/SafeOS-build/safeos-linux-distro-a/releases \
	safeos-builder:bookworm-20261031T210000Z bash scripts/build_iso.sh
```

See `docs/build-and-test.md` for builder creation, source tests, image-content checks, and QEMU boot/install steps. No paid services or proprietary packages are required for the local image build.

## Support and limitations

- Target: Debian Bookworm amd64 on x86_64 PCs and QEMU. Physical hardware support has not been certified.
- Boot: GRUB BIOS and EFI entries are configured; boot verification is required before release.
- Installation: Debian Installer is included. Back up files first; a disk install can overwrite the selected target. Recovery and rollback are not currently provided.
- First run: the wizard configures the current writable root. Standard live sessions are ephemeral unless a live-boot persistence store is configured; installing the customized SafeOS profile has not been verified.
- Updates: Debian package signatures are verified by APT. SafeOS-specific update orchestration and rollback are not implemented.
- Release integrity: a SHA-256 checksum is produced; the ISO is not signed with a SafeOS publisher key.
- SafeCloud, SafeAI, SafeStore, VirtualCloud, SafeSuite, Krow Diagnostics, ZeroCheat, Candy, Defendant, and SafeAgent are not functional services/apps in this build.
- No telemetry is collected or autostarted. No student screen viewing, device takeover, hidden monitoring, punitive lockout, or exam surveillance is implemented.

This repository now uses Debian live-build to generate a bootable Linux distro image with XFCE, LightDM, and SafeOS branding.
The build script configures Debian Bookworm repositories and Debian security mirrors so the resulting ISO is built from a real Debian base.

