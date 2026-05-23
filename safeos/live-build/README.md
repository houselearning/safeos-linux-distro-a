# Live-build customization

Live-build configuration for SafeOS should derive from Debian/Ubuntu live-build templates.

## Proposed structure
- `config/` — package lists, hooks, and chroot customization
- `binary/` — generated install images and boot assets
- `cache/` — package cache for reproducible builds

## Recommended customization flow
- Install `live-build` and `debootstrap`
- Layer in SafeOS branding and desktop themes
- Add SafeShell, SafeAI, and virtual classroom tooling
- Generate a custom ISO with a patched GRUB theme and a retro boot sequence
