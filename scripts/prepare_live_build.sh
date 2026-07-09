#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LIVE_DIR="${SAFEOS_LIVE_BUILD_DIR:-/tmp/safeos-live-build}"

if ! command -v lb >/dev/null 2>&1; then
  echo "live-build is not installed. Install live-build to make a bootable Linux distro ISO."
  exit 1
fi

rm -rf "$LIVE_DIR/config" "$LIVE_DIR/binary" "$LIVE_DIR/cache"
mkdir -p "$LIVE_DIR"
cd "$LIVE_DIR"

lb config \
  --mode debian \
  --distribution bookworm \
  --archive-areas "main contrib non-free non-free-firmware" \
  --binary-images iso-hybrid \
  --bootappend-live "boot=live components quiet splash" \
  --debian-installer false \
  --linux-flavours amd64 \
  --mirror-bootstrap http://deb.debian.org/debian \
  --mirror-chroot http://deb.debian.org/debian \
  --mirror-binary http://deb.debian.org/debian \
  --keyring-packages debian-archive-keyring \
  --bootstrap-keyring debian-archive-keyring \
  --security false \
  --bootloader grub \
  --firmware-chroot true \
  --firmware-binary true

mkdir -p config/package-lists
mkdir -p config/includes.chroot/etc/branding
mkdir -p config/includes.chroot/etc/apt
mkdir -p config/includes.chroot/usr/share/safeos
mkdir -p config/includes.chroot/usr/local/bin
mkdir -p config/includes.chroot/etc/xdg/autostart
mkdir -p config/hooks

cat > config/package-lists/safeos.list.chroot <<'EOF'
# SafeOS core packages
locales
sudo
network-manager
live-config
live-boot
lightdm
lightdm-gtk-greeter
xfce4
xfce4-goodies
firefox-esr
chromium
python3
git
curl
wget
nano
pulseaudio
dbus-user-session
EOF

cat > config/includes.chroot/etc/branding/safeos-branding.conf <<'EOF'
safeos.brand=SafeOS
safeos.team=HouseLearning
safeos.theme=retro-xp-blue
safeos.boot=Krow Diagnostics
safeos.actionbar=Action Bar
safeos.shell=SafeShell
EOF

cat > config/hooks/01-safeos-branding.chroot <<'EOF'
#!/bin/sh
set -e
mkdir -p /usr/share/safeos
cp /etc/branding/safeos-branding.conf /usr/share/safeos/branding.conf
EOF
chmod +x config/hooks/01-safeos-branding.chroot

if [[ -f "$ROOT_DIR/apps/milestoneService/main.py" ]]; then
  cp "$ROOT_DIR/apps/milestoneService/main.py" config/includes.chroot/usr/share/safeos/milestone_service.py
fi

if [[ -f "$ROOT_DIR/desktop/autostart/milestone-service.sh" ]]; then
  cp "$ROOT_DIR/desktop/autostart/milestone-service.sh" config/includes.chroot/usr/share/safeos/milestone-service.sh
  chmod +x config/includes.chroot/usr/share/safeos/milestone-service.sh
fi

cat > config/includes.chroot/etc/xdg/autostart/safeos-milestone.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=SafeOS Milestone Service
Exec=/usr/share/safeos/milestone-service.sh
X-GNOME-Autostart-enabled=true
NoDisplay=true
EOF

if [[ -f "$ROOT_DIR/desktop/autostart/safeos-session.sh" ]]; then
  mkdir -p config/includes.chroot/usr/share/safeos
  cp "$ROOT_DIR/desktop/autostart/safeos-session.sh" config/includes.chroot/usr/share/safeos/safeos-session.sh
  chmod +x config/includes.chroot/usr/share/safeos/safeos-session.sh
fi

cat > config/includes.chroot/etc/xdg/autostart/safeos-session.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=SafeOS Session Startup
Exec=/usr/share/safeos/safeos-session.sh
X-GNOME-Autostart-enabled=true
NoDisplay=true
EOF

cat > config/includes.chroot/etc/apt/sources.list <<'EOF'
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security bookworm-security main contrib non-free
EOF

cat > config/includes.chroot/usr/share/safeos/safeos-session.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

notify-send "SafeOS" "Desktop session initialized" || true
python3 /usr/share/safeos/safenotify/notify.py --event startup || true
if command -v python3 >/dev/null 2>&1 && [[ -f "/usr/share/safeos/milestone_service.py" ]]; then
  python3 /usr/share/safeos/milestone_service.py --event startup --hidden >/dev/null 2>&1 &
fi
EOF

chmod +x config/includes.chroot/usr/share/safeos/safeos-session.sh

echo "Prepared live-build configuration for SafeOS"

# Provide a custom grub.cfg so the ISO boots the live XFCE desktop by default.
# This will be included into the ISO's /boot/grub/ and override the default menu.
mkdir -p config/includes.binary/boot/grub
cat > config/includes.binary/boot/grub/grub.cfg <<'EOF'
set default=0
set timeout=5

menuentry "SafeOS Live Desktop" {
  set gfxpayload=keep
  linux /live/vmlinuz boot=live components quiet splash
  initrd /live/initrd.img
}

# Keep existing diagnostics entry available under a second slot to fall back to.
menuentry "SafeOS Diagnostics Environment" {
  set gfxpayload=keep
  linux /live/vmlinuz boot=live components nosplash single
  initrd /live/initrd.img
}
EOF
