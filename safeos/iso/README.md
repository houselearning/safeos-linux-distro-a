# ISO outputs

This directory stores release artifacts, checksum files, and installation media descriptions for SafeOS.

## Suggested contents
- `safeos-amd64.iso`
- `safeos-amd64.sha256`
- `release-notes.md`
- `manifest.json`

## Release workflow
1. Run `scripts/build_iso.sh`
2. Validate the resulting ISO with `scripts/validate_safeos.sh`
3. Publish the image and checksums to the SafeStore or internal mirror
