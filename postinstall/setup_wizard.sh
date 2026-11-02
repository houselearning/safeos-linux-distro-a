#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f /usr/local/lib/safeos/first_boot.py ]]; then
	exec /usr/bin/python3 /usr/local/lib/safeos/first_boot.py "$@"
fi
exec /usr/bin/python3 "$SCRIPT_DIR/first_boot.py" "$@"
