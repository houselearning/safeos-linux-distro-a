# Live-build customization

SafeOS uses Debian live-build to produce an x86_64 Debian Bookworm live/install ISO with XFCE and Debian Installer.

## Structure
- `config/` — generated package lists and staged image files
- `binary/` — generated install images and boot assets
- `cache/` — package cache for repeatable builds; stored on the external build volume

## Build flow
- Start the pinned builder and external storage profile described in `docs/build-and-test.md`.
- Run `scripts/test_source.sh` before building.
- Run `scripts/build_iso.sh` inside the builder; it validates staging, the package manifest, checksum, and boot catalog.

## Notes
The build uses a digest-pinned Debian builder and signed Debian Bookworm, updates, and security snapshots. The image includes XFCE, LightDM, packaged local applications, and Debian Installer. It does not include or autostart milestone tracking, cloud services, or custom SafeOS application backends.
