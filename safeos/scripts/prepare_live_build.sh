#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE_DIR="$ROOT_DIR/live-build"

mkdir -p "$LIVE_DIR/config/archives"
mkdir -p "$LIVE_DIR/config/package-lists"
mkdir -p "$LIVE_DIR/config/hooks"
mkdir -p "$LIVE_DIR/config/includes.chroot/etc/branding"

cat > "$LIVE_DIR/config/package-lists/safeos.list.chroot" <<'EOF'
# SafeOS base packages
kde-plasma-desktop
xfce4
chromium
python3
git
curl
wget
EOF

cat > "$LIVE_DIR/config/includes.chroot/etc/branding/safeos-branding.conf" <<'EOF'
safeos.brand=SafeOS
safeos.team=HouseLearning
safeos.theme=retro-xp-blue
safeos.boot=Krow Diagnostics
safeos.actionbar=Action Bar
safeos.shell=SafeShell
EOF

cat > "$LIVE_DIR/config/hooks/01-safeos-branding.chroot" <<'EOF'
#!/bin/sh
set -e
mkdir -p /usr/share/safeos
cp /etc/branding/safeos-branding.conf /usr/share/safeos/branding.conf
EOF

chmod +x "$LIVE_DIR/config/hooks/01-safeos-branding.chroot"

echo "Prepared live-build configuration for SafeOS"
