#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE_BUILD_DIR="${SAFEOS_LIVE_BUILD_DIR:-/tmp/safeos-live-build}"
ISO_DIR="$ROOT_DIR/iso"
OUTPUT_ISO="$ISO_DIR/safeos-amd64.iso"

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

log "Preparing SafeOS live-build configuration"
SAFEOS_LIVE_BUILD_DIR="$LIVE_BUILD_DIR" "$ROOT_DIR/scripts/prepare_live_build.sh"

cd "$LIVE_BUILD_DIR"
log "Cleaning previous live-build artifacts"
if [[ $EUID -ne 0 ]]; then
  sudo lb clean --purge >/dev/null 2>&1 || true
  log "Building with sudo to satisfy live-build root requirements"
  sudo lb build
else
  lb clean --purge >/dev/null 2>&1 || true
  lb build
fi

iso_found=$(find "$LIVE_BUILD_DIR" -type f \( -name '*.iso' -o -name '*.hybrid' -o -name '*.img' \) | sort | tail -n1 || true)
if [[ -z "$iso_found" ]]; then
  echo "Live-build did not produce an ISO artifact in $LIVE_BUILD_DIR"
  echo "Search path: $LIVE_BUILD_DIR"
  find "$LIVE_BUILD_DIR" -type f | sort | tail -n20
  exit 1
fi

mkdir -p "$ISO_DIR"
mv "$iso_found" "$OUTPUT_ISO"
log "Created bootable Linux distro ISO: $OUTPUT_ISO"

sha256sum "$OUTPUT_ISO" > "$ISO_DIR/safeos-amd64.sha256"
log "Generated checksum: $ISO_DIR/safeos-amd64.sha256"
