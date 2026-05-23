#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE_BUILD_DIR="$ROOT_DIR/live-build"
ISO_DIR="$ROOT_DIR/iso"

log() {
  echo "[safeos-build] $*"
}

log "Preparing SafeOS build workspace"
mkdir -p "$ISO_DIR"

if ! command -v lb >/dev/null 2>&1; then
  log "live-build is not installed. Install it before building an ISO."
  exit 1
fi

log "Preparing live-build configuration"
"$ROOT_DIR/scripts/prepare_live_build.sh"

log "Generating live-build structure"
cat > "$LIVE_BUILD_DIR/config/branding.conf" <<'EOF'
SAFEOS_BRAND=SafeOS
SAFEOS_THEME=retro-xp-blue
SAFEOS_BOOT_DIAGNOSTICS=Krow Diagnostics
SAFEOS_STARTUP_SOUND=enabled
EOF

log "Live-build staging complete. Next step: run lb build from $LIVE_BUILD_DIR"
log "Output artifacts will be written to $ISO_DIR"
