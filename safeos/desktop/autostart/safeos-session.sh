#!/usr/bin/env bash
set -euo pipefail

# SafeOS desktop startup helpers
export SAFEOS_DESKTOP_MODE="school"
notify-send "SafeOS" "Desktop session initialized" || true
python3 /usr/share/safeos/safenotify/notify.py --event startup || true
