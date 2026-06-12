# Live-build customization

SafeOS now uses Debian live-build to produce a real bootable Linux distro image.

## Structure
- `config/` — package lists, hooks, and chroot customizations
- `binary/` — generated install images and boot assets
- `cache/` — package cache for reproducible builds

## Build flow
- Install `live-build` and `debootstrap`
- Run `bash scripts/prepare_live_build.sh` to create the live-build tree
- Run `bash scripts/build_iso.sh` to build the actual bootable Debian-based SafeOS ISO

## Notes
The build uses Debian mode (`lb config --mode debian`) with Debian Bookworm repositories and Debian security mirrors.
The image includes an XFCE desktop, LightDM login manager, Firefox ESR, Chromium, Python3, and the SafeOS milestoneService background monitoring app.
