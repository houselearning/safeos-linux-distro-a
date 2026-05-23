#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

required_dirs=(
  "$ROOT_DIR/iso"
  "$ROOT_DIR/live-build"
  "$ROOT_DIR/scripts"
  "$ROOT_DIR/branding"
  "$ROOT_DIR/icons"
  "$ROOT_DIR/themes"
  "$ROOT_DIR/wallpapers"
  "$ROOT_DIR/desktop"
  "$ROOT_DIR/safeshell"
  "$ROOT_DIR/safemenu"
  "$ROOT_DIR/safenotify"
  "$ROOT_DIR/apps"
  "$ROOT_DIR/system"
  "$ROOT_DIR/drivers"
  "$ROOT_DIR/postinstall"
  "$ROOT_DIR/docs"
)

for dir in "${required_dirs[@]}"; do
  if [[ ! -d "$dir" ]]; then
    echo "Missing required directory: $dir"
    exit 1
  fi
done

bash -n "$ROOT_DIR/scripts/build_iso.sh"
bash -n "$ROOT_DIR/scripts/prepare_live_build.sh"
bash -n "$ROOT_DIR/scripts/validate_safeos.sh"

python3 - <<'PY'
from pathlib import Path
root = Path('safeos')
required = [
    'README.md',
    'scripts/build_iso.sh',
    'scripts/prepare_live_build.sh',
    'scripts/validate_safeos.sh',
    'docs/architecture.md',
    'docs/installer-flow.md',
    'safeshell/jiraffe_shell.sh',
    'safemenu/actionbar.py',
    'safenotify/notify.py',
    'apps/common/safeos_app.c',
    'apps/common/safeos_app.h',
]
for item in required:
    path = root / item
    if not path.exists():
        raise SystemExit(f'Missing required file: {path}')
print('SafeOS scaffold validation passed')
PY
