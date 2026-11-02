# SafeOS Build and Test

## Target and storage

The supported virtual target for this release is Debian Bookworm `amd64` under QEMU. Physical hardware and Secure Boot are not certified. Build tools, Docker images, live-build caches, VM disks, logs, test binaries, and releases must remain under `/Volumes/Other Storage`.

The repository path contains spaces, and live-build rejects a work directory containing spaces. The build therefore mounts the repository at `/src`, mounts the external drive at `/safeos`, and stores the live-build tree/cache in a dedicated Docker named volume on a Colima VM whose disk lives under `/Volumes/Other Storage/.colima`.

## Create the isolated builder

Run once from macOS:

```sh
export COLIMA_HOME="/Volumes/Other Storage/.colima"
colima start safeos-build --cpu 4 --memory 8 --disk 80 --arch x86_64 \
  --mount "/Volumes/Other Storage:w" --activate=false
docker --context colima-safeos-build volume create safeos-build-workspace
docker --context colima-safeos-build build \
  --file scripts/Dockerfile.builder \
  --tag safeos-builder:bookworm-20261031T210000Z scripts
```

The Dockerfile pins the Debian base image by digest, uses the signed Debian snapshot at `2026-10-31T21:00Z`, and pins direct builder package versions. The build container records its installed package versions at `/usr/share/safeos-builder/package-versions.txt`. APT signature checking is not disabled.

## Run source tests

```sh
docker --context colima-safeos-build run --rm \
  --volume safeos-build-workspace:/var/lib/safeos-build \
  --volume "/Volumes/Other Storage:/safeos" \
  --volume "$PWD:/src:ro" --workdir /src \
  --env SAFEOS_BUILD_ROOT=/var/lib/safeos-build/safeos-linux-distro-a \
  safeos-builder:bookworm-20261031T210000Z bash scripts/test_source.sh
```

This checks Bash syntax, parses Python source, runs unittest cases, compiles the C launcher with warnings as errors, checks its behavior, verifies the exact app allowlist, and tests the APT update command with a mock package manager. Test binaries and temporary files are created only in the dedicated external Docker volume.

## Build and validate the ISO

```sh
docker --context colima-safeos-build run --rm --privileged \
  --volume safeos-build-workspace:/var/lib/safeos-build \
  --volume "/Volumes/Other Storage:/safeos" \
  --volume "$PWD:/src:ro" --workdir /src \
  --env SAFEOS_BUILD_ROOT=/var/lib/safeos-build/safeos-linux-distro-a \
  --env SAFEOS_RELEASE_DIR=/safeos/SafeOS-build/safeos-linux-distro-a/releases \
  safeos-builder:bookworm-20261031T210000Z bash scripts/build_iso.sh
```

The ISO is content-addressed in `/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/releases/`. A SHA-256 file, Debian package manifest, and builder package-version manifest accompany it. The release is not valid until `check_image_manifest.py`, the checksum check, ISO boot-entry inspection, and QEMU boot/install tests pass.

## QEMU boot and install smoke test

Set `ISO` to the built ISO and keep the VM disk and logs on the external volume:

```sh
ISO="/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/releases/<built-image>.iso"
DISK="/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/tests/install-smoke.qcow2"
qemu-img create -f qcow2 "$DISK" 32G
qemu-system-x86_64 -accel tcg -m 4096 -cdrom "$ISO" \
  -drive "file=$DISK,format=qcow2,if=virtio" -boot order=d -display cocoa
```

For live boot, select the live desktop and verify the SafeOS first-run assistant appears after XFCE starts. Complete setup with a disposable account, verify the XFCE session and NetworkManager editor, then log out and confirm the created account can sign in. Setup changes are lost on reboot unless a live-boot persistence store is configured.

To test Debian installation, select Debian Installer from the boot menu or launch it from the desktop; select only the disposable `install-smoke.qcow2` disk, complete account creation, remove the ISO, and boot the installed disk. This currently validates Debian Installer, not installation of the customized SafeOS live profile. Never point this smoke test at a host physical disk.

For BIOS boot, run the ISO without a disk and confirm the live desktop appears:

```sh
qemu-system-x86_64 -accel tcg -m 4096 -cdrom "$ISO" -boot order=d -display cocoa
```

For EFI boot, use the checksum-verified OVMF files downloaded from Debian and stored under the external test directory. Copy the variable store before boot because firmware may modify it:

```sh
TEST_DIR="/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/tests"
(cd "$TEST_DIR/ovmf" && shasum -a 256 --check ovmf.sha256)
VARS_FILE="$(mktemp "$TEST_DIR/OVMF_VARS.XXXXXX.fd")"
cp "$TEST_DIR/ovmf/extracted-safe/usr/share/OVMF/OVMF_VARS.fd" "$VARS_FILE"
qemu-system-x86_64 -machine q35 -accel tcg -m 4096 \
  -drive "if=pflash,format=raw,unit=0,readonly=on,file=$TEST_DIR/ovmf/extracted-safe/usr/share/OVMF/OVMF_CODE.fd" \
  -drive "if=pflash,format=raw,unit=1,file=$VARS_FILE" \
  -cdrom "$ISO" -boot order=d -display cocoa
```

To test installation, create only the disposable disk shown above. Select the live desktop, open Debian Installer, select only that QCOW2 disk, complete account creation, remove the ISO, and boot the installed disk. Record whether BIOS, EFI, installer, and installed login each succeeded. Do not mark the image installable based solely on a successful build or an ISO file, and never point the smoke test at a host physical disk.

## Current limitations

- No SafeCloud, SafeAI, SafeStore, SafeSuite, VirtualCloud, custom driver, malware scanning, ZeroCheat, or remote-management backend is included.
- Debian Installer provides local account setup; there is no SafeOS first-boot wizard, recovery partition, or rollback mechanism.
- The live session is ephemeral unless the user configures persistence.
- QEMU does not verify physical Wi-Fi, sound, touch, webcam, Thunderbolt, Chromebook, NVIDIA, or other hardware compatibility.
- No hidden telemetry or student monitoring is included.