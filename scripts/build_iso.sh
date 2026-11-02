#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAFEOS_BUILD_ROOT="${SAFEOS_BUILD_ROOT:-/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a}"
LIVE_BUILD_DIR="${SAFEOS_LIVE_BUILD_DIR:-$SAFEOS_BUILD_ROOT/live-build}"
RELEASE_DIR="${SAFEOS_RELEASE_DIR:-$SAFEOS_BUILD_ROOT/releases}"
SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-$(git -c safe.directory="$ROOT_DIR" -C "$ROOT_DIR" log -1 --format=%ct)}"
export SOURCE_DATE_EPOCH
export TZ="UTC"
export LC_ALL="C.UTF-8"

log() {
  echo "[safeos-build] $*"
}

ensure_tool() {
  if ! command -v "$1" >/dev/null 2>&1; then
    log "Required tool '$1' is not installed. Install it before building an ISO."
    exit 1
  fi
}

ensure_tool lb
ensure_tool xorriso
ensure_tool sha256sum
ensure_tool python3

case "$SAFEOS_BUILD_ROOT" in
  "/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a"|"/safeos/SafeOS-build/safeos-linux-distro-a"|"/var/lib/safeos-build/safeos-linux-distro-a") ;;
  *) log "Refusing build root outside the external SafeOS workspace: $SAFEOS_BUILD_ROOT"; exit 1 ;;
esac
case "$RELEASE_DIR" in
  "/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/releases"|"/safeos/SafeOS-build/safeos-linux-distro-a/releases") ;;
  *) log "Refusing release path outside the external SafeOS workspace: $RELEASE_DIR"; exit 1 ;;
esac
if [[ -L "$SAFEOS_BUILD_ROOT" || -L "$LIVE_BUILD_DIR" || -L "$RELEASE_DIR" ]]; then
  log "Refusing symlinked SafeOS build or release directory"
  exit 1
fi
mkdir -p "$SAFEOS_BUILD_ROOT"
EXPECTED_BUILD_ROOT="$(cd "$SAFEOS_BUILD_ROOT" && pwd -P)"
case "$LIVE_BUILD_DIR" in
  "$SAFEOS_BUILD_ROOT"/*) ;;
  *) log "Refusing live-build path outside $EXPECTED_BUILD_ROOT: $LIVE_BUILD_DIR"; exit 1 ;;
esac
mkdir -p "$LIVE_BUILD_DIR" "$RELEASE_DIR"
LIVE_BUILD_REAL="$(cd "$LIVE_BUILD_DIR" && pwd -P)"
RELEASE_DIR_REAL="$(cd "$RELEASE_DIR" && pwd -P)"
case "$LIVE_BUILD_REAL" in
  "$EXPECTED_BUILD_ROOT"/*) ;;
  *) log "Refusing live-build path outside $EXPECTED_BUILD_ROOT: $LIVE_BUILD_REAL"; exit 1 ;;
esac
case "$RELEASE_DIR_REAL" in
  "/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/releases"|"/safeos/SafeOS-build/safeos-linux-distro-a/releases") ;;
  *) log "Refusing unexpected release directory: $RELEASE_DIR_REAL"; exit 1 ;;
esac
cd "$LIVE_BUILD_DIR"
for path in config binary cache; do
  if [[ -L "$LIVE_BUILD_DIR/$path" ]]; then
    log "Refusing symlinked live-build state: $LIVE_BUILD_DIR/$path"
    exit 1
  fi
done
if [[ -d config || -d binary || -d cache ]]; then
  log "Cleaning prior live-build state"
  if [[ $EUID -ne 0 ]]; then
    sudo lb clean
  else
    lb clean
  fi
fi

log "Preparing SafeOS live-build configuration"
SAFEOS_BUILD_ROOT="$SAFEOS_BUILD_ROOT" SAFEOS_LIVE_BUILD_DIR="$LIVE_BUILD_DIR" "$ROOT_DIR/scripts/prepare_live_build.sh"
SAFEOS_BUILD_ROOT="$SAFEOS_BUILD_ROOT" bash "$ROOT_DIR/scripts/test_source.sh"
SAFEOS_BUILD_ROOT="$SAFEOS_BUILD_ROOT" bash "$ROOT_DIR/apps/build.sh" \
  "$LIVE_BUILD_DIR/config/includes.chroot/usr/local/lib/safeos/apps"
python3 "$ROOT_DIR/scripts/check_image_tree.py" \
  "$LIVE_BUILD_DIR/config/includes.chroot"

if [[ $EUID -ne 0 ]]; then
  log "Building with sudo to satisfy live-build root requirements"
  sudo lb build
else
  lb build
fi

iso_found=$(find "$LIVE_BUILD_DIR" -type f \( -name '*.iso' -o -name '*.hybrid' \) | sort | tail -n1 || true)
if [[ -z "$iso_found" ]]; then
  echo "Live-build did not produce an ISO artifact in $LIVE_BUILD_DIR"
  echo "Search path: $LIVE_BUILD_DIR"
  find "$LIVE_BUILD_DIR" -type f | sort | tail -n20
  exit 1
fi

packages_found="$LIVE_BUILD_DIR/binary.packages"
if [[ ! -f "$packages_found" && -f "$LIVE_BUILD_DIR/live-image-amd64.packages" ]]; then
  packages_found="$LIVE_BUILD_DIR/live-image-amd64.packages"
fi
if [[ ! -f "$packages_found" ]]; then
  log "live-build did not produce a package manifest; refusing an unverified ISO"
  exit 1
fi
python3 "$ROOT_DIR/scripts/check_image_manifest.py" "$packages_found"

digest="$(sha256sum "$iso_found" | awk '{print $1}')"
artifact_name="safeos-amd64-$digest.iso"
output_iso="$RELEASE_DIR/$artifact_name"
checksum_file="$output_iso.sha256"
package_manifest="$output_iso.packages.txt"
builder_manifest="$output_iso.builder-packages.txt"
for release_file in "$output_iso" "$checksum_file" "$package_manifest" "$builder_manifest"; do
  if [[ -L "$release_file" ]]; then
    log "Refusing symlinked release file: $release_file"
    exit 1
  fi
done

if [[ -e "$output_iso" ]]; then
  existing_digest="$(sha256sum "$output_iso" | awk '{print $1}')"
  if [[ "$existing_digest" != "$digest" ]]; then
    log "Refusing to overwrite an artifact with a mismatched content hash: $output_iso"
    exit 1
  fi
else
  mv "$iso_found" "$output_iso"
fi

for artifact_pair in \
  "$packages_found:$package_manifest" \
  "/usr/share/safeos-builder/package-versions.txt:$builder_manifest"; do
  source_file="${artifact_pair%%:*}"
  destination_file="${artifact_pair#*:}"
  if [[ -e "$destination_file" ]]; then
    if ! cmp -s "$source_file" "$destination_file"; then
      log "Refusing to overwrite an unexpected release manifest: $destination_file"
      exit 1
    fi
  else
    cp "$source_file" "$destination_file"
  fi
done

if [[ -e "$checksum_file" ]]; then
  if [[ "$(<"$checksum_file")" != "$digest  $artifact_name" ]]; then
    log "Refusing to overwrite an unexpected checksum file: $checksum_file"
    exit 1
  fi
else
  printf '%s  %s\n' "$digest" "$artifact_name" > "$checksum_file"
fi

log "Created bootable Linux distro ISO: $output_iso"
log "Generated checksum: $checksum_file"
log "Generated package manifest: $package_manifest"
SAFEOS_RELEASE_DIR="$RELEASE_DIR" \
  SAFEOS_RELEASE_ISO="$output_iso" \
  SAFEOS_TEST_OUTPUT_DIR="${SAFEOS_TEST_OUTPUT_DIR:-$(dirname "$RELEASE_DIR")/tests}" \
  bash "$ROOT_DIR/scripts/validate_safeos.sh"
