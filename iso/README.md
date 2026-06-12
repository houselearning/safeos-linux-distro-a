# ISO outputs

This directory stores release artifacts, checksum files, and installation media descriptions for SafeOS.

## Generated artifacts
- `safeos-amd64.iso` — bootable GRUB-based SafeOS ISO
- `safeos-amd64.sha256` — SHA-256 checksum for the ISO
- `release-notes.md` — build summary and release details
- `manifest.json` — ISO metadata for packaging and verification

## Build and validation
1. Run `bash scripts/build_iso.sh` to generate a bootable ISO.
2. Validate the output with `bash scripts/validate_safeos.sh`.
3. Optionally test locally with QEMU:
   - `qemu-system-x86_64 -cdrom iso/safeos-amd64.iso -boot d -m 512 -nographic -serial stdio`
4. Publish the ISO and checksum to SafeStore or your internal release channel.
