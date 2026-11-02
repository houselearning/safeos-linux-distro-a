#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAFEOS_BUILD_ROOT="${SAFEOS_BUILD_ROOT:-/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a}"
LIVE_DIR="${SAFEOS_LIVE_BUILD_DIR:-$SAFEOS_BUILD_ROOT/live-build}"
DEBIAN_SNAPSHOT="https://snapshot.debian.org/archive/debian/20261031T210000Z/"
DEBIAN_SECURITY_SNAPSHOT="https://snapshot.debian.org/archive/debian-security/20261031T210000Z/"

case "$SAFEOS_BUILD_ROOT" in
  "/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a"|"/safeos/SafeOS-build/safeos-linux-distro-a"|"/var/lib/safeos-build/safeos-linux-distro-a") ;;
  *) echo "Refusing build root outside the external SafeOS workspace: $SAFEOS_BUILD_ROOT"; exit 1 ;;
esac
if [[ -L "$SAFEOS_BUILD_ROOT" ]]; then
  echo "Refusing symlinked SafeOS build root: $SAFEOS_BUILD_ROOT"
  exit 1
fi
mkdir -p "$SAFEOS_BUILD_ROOT"
EXPECTED_BUILD_ROOT="$(cd "$SAFEOS_BUILD_ROOT" && pwd -P)"
case "$LIVE_DIR" in
  "$SAFEOS_BUILD_ROOT"/*) ;;
  *) echo "Refusing live-build path outside $EXPECTED_BUILD_ROOT: $LIVE_DIR"; exit 1 ;;
esac
if [[ -L "$LIVE_DIR" ]]; then
  echo "Refusing symlinked live-build directory: $LIVE_DIR"
  exit 1
fi
mkdir -p "$LIVE_DIR"
LIVE_DIR_REAL="$(cd "$LIVE_DIR" && pwd -P)"
case "$LIVE_DIR_REAL" in
  "$EXPECTED_BUILD_ROOT"/*) ;;
  *) echo "Refusing live-build path outside $EXPECTED_BUILD_ROOT: $LIVE_DIR_REAL"; exit 1 ;;
esac
if ! command -v lb >/dev/null 2>&1; then
  echo "live-build is not installed. Install live-build to make a bootable Linux distro ISO."
  exit 1
fi

for path in config binary; do
  if [[ -L "$LIVE_DIR/$path" ]]; then
    echo "Refusing symlinked live-build state: $LIVE_DIR/$path"
    exit 1
  fi
done
rm -rf -- "$LIVE_DIR/config" "$LIVE_DIR/binary"
cd "$LIVE_DIR"

lb config \
  --mode debian \
  --distribution bookworm \
  --archive-areas "main non-free-firmware" \
  --binary-images iso-hybrid \
  --bootappend-live "boot=live components quiet splash" \
  --debian-installer live \
  --linux-flavours amd64 \
  --mirror-bootstrap "$DEBIAN_SNAPSHOT" \
  --mirror-chroot "$DEBIAN_SNAPSHOT" \
  --mirror-chroot-security "$DEBIAN_SECURITY_SNAPSHOT" \
  --mirror-binary "$DEBIAN_SNAPSHOT" \
  --mirror-binary-security "$DEBIAN_SECURITY_SNAPSHOT" \
  --keyring-packages debian-archive-keyring \
  --bootloaders "grub-pc grub-efi" \
  --firmware-chroot true \
  --firmware-binary true

GRUB_CONFIG_TEMPLATE="/usr/share/live/build/bootloaders/grub-pc/config.cfg"
if ! grep -Fq '    font=unicode' "$GRUB_CONFIG_TEMPLATE"; then
  echo "Expected GRUB font configuration was not found: $GRUB_CONFIG_TEMPLATE" >&2
  exit 1
fi
mkdir -p config/bootloaders/grub-pc
sed 's|^    font=unicode$|    font=$prefix/unicode.pf2|' \
  "$GRUB_CONFIG_TEMPLATE" > config/bootloaders/grub-pc/config.cfg

mkdir -p config/package-lists
mkdir -p config/includes.chroot/etc/branding
mkdir -p config/includes.chroot/etc/apt
mkdir -p config/includes.chroot/usr/share/safeos
mkdir -p config/includes.chroot/usr/share/applications
mkdir -p config/includes.chroot/usr/local/sbin
mkdir -p config/includes.chroot/usr/local/bin
mkdir -p config/includes.chroot/usr/local/lib/safeos
mkdir -p config/includes.chroot/usr/share/safeos/safenotify
mkdir -p config/includes.chroot/etc/xdg/autostart
mkdir -p config/hooks

cat > config/package-lists/safeos.list.chroot <<'EOF'
# SafeOS core packages
locales
ca-certificates
sudo
network-manager
network-manager-gnome
live-config
live-boot
lightdm
lightdm-gtk-greeter
xfce4
xfce4-goodies
firefox-esr
chromium
python3
python3-gi
gir1.2-gtk-3.0
git
curl
wget
nano
pulseaudio
dbus-user-session
thunar
galculator
libreoffice-calc
libreoffice-writer
libreoffice-impress
parole
cheese
xfce4-settings
xfce4-terminal
geany
debian-installer-launcher
libnotify-bin
EOF

write_launcher() {
  local desktop_id="$1"
  local display_name="$2"
  local app_id="$3"
  local categories="$4"
  cat > "config/includes.chroot/usr/share/applications/$desktop_id.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=$display_name
Exec=/usr/local/lib/safeos/apps/$app_id
Terminal=false
Categories=$categories
EOF
}

write_launcher safeos-browser SafeBrowser safebrowser 'Network;WebBrowser;X-Education;'
write_launcher safeos-files Files fileexplorer 'Utility;FileManager;X-FileManager;'
write_launcher safeos-calculator Calculator calculator 'Utility;Calculator;'
write_launcher safeos-spreadsheet Spreadsheet spreadsheet 'Office;Spreadsheet;'
write_launcher safeos-writer SafeWriter safewriter 'Office;WordProcessor;'
write_launcher safeos-presentation SafeDeck safedeck 'Office;Presentation;'
write_launcher safeos-media-player 'Media Player' mediaplayer 'AudioVideo;Player;'
write_launcher safeos-camera Camera camera 'AudioVideo;Video;'
write_launcher safeos-settings Settings settings 'Settings;'
write_launcher safeos-terminal Terminal jiraffeterminal 'System;TerminalEmulator;'
write_launcher safeos-code 'Orbital Code' orbitalcode 'Development;IDE;'

cat > config/includes.chroot/etc/branding/safeos-branding.conf <<'EOF'
safeos.brand=SafeOS
safeos.team=HouseLearning
safeos.theme=retro-xp-blue
safeos.boot=Krow Diagnostics
safeos.actionbar=Action Bar
safeos.shell=SafeShell
EOF

cp config/includes.chroot/etc/branding/safeos-branding.conf \
  config/includes.chroot/usr/share/safeos/branding.conf

cp "$ROOT_DIR/system/update_manager.sh" config/includes.chroot/usr/local/sbin/safeos-update
chmod +x config/includes.chroot/usr/local/sbin/safeos-update
cp "$ROOT_DIR/system/registry_editor.py" config/includes.chroot/usr/local/bin/safeos-settings
chmod +x config/includes.chroot/usr/local/bin/safeos-settings
cp "$ROOT_DIR/safenotify/notify.py" config/includes.chroot/usr/share/safeos/safenotify/notify.py
cat > config/includes.chroot/usr/local/bin/safeos-notify <<'EOF'
#!/bin/sh
exec /usr/bin/python3 /usr/share/safeos/safenotify/notify.py "$@"
EOF
chmod +x config/includes.chroot/usr/local/bin/safeos-notify

cp "$ROOT_DIR/postinstall/first_boot.py" \
  config/includes.chroot/usr/local/lib/safeos/first_boot.py
chmod 0755 config/includes.chroot/usr/local/lib/safeos/first_boot.py
cp "$ROOT_DIR/wallpapers/safeos-dark.png" \
  config/includes.chroot/usr/share/safeos/setup-wallpaper.png
cp "$ROOT_DIR/postinstall/setup_wizard.sh" \
  config/includes.chroot/usr/local/bin/safeos-setup
chmod 0755 config/includes.chroot/usr/local/bin/safeos-setup
cat > config/includes.chroot/etc/xdg/autostart/safeos-setup.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=SafeOS First-Run Setup
Exec=/usr/local/bin/safeos-setup
OnlyShowIn=XFCE;
NoDisplay=true
X-GNOME-Autostart-enabled=true
EOF

cat > config/includes.chroot/etc/apt/sources.list <<'EOF'
deb https://deb.debian.org/debian bookworm main non-free-firmware
deb https://deb.debian.org/debian bookworm-updates main non-free-firmware
deb https://security.debian.org/debian-security bookworm-security main non-free-firmware
EOF

echo "Prepared live-build configuration for SafeOS"
[[ -f config/package-lists/safeos.list.chroot ]]
[[ -d config/includes.chroot/usr/share/applications ]]
printf '%s\n' 'SafeOS image staging is ready'
