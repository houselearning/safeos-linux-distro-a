#!/usr/bin/env bash
set -euo pipefail

notify-send "SafeOS" "Desktop session initialized" || true
python3 /usr/share/safeos/safenotify/notify.py --event startup || true
if command -v python3 >/dev/null 2>&1 && [[ -f "/usr/share/safeos/milestone_service.py" ]]; then
  python3 /usr/share/safeos/milestone_service.py --event startup --hidden >/dev/null 2>&1 &
fi
