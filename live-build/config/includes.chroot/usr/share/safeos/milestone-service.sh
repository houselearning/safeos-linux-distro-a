#!/usr/bin/env bash
set -euo pipefail

if command -v python3 >/dev/null 2>&1 && [[ -f "/usr/share/safeos/milestone_service.py" ]]; then
  python3 /usr/share/safeos/milestone_service.py --event boot --hidden >/dev/null 2>&1 &
fi
