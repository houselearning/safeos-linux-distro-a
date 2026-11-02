#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAFEOS_BUILD_ROOT="${SAFEOS_BUILD_ROOT:-/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a}"
cd "$ROOT_DIR"
export SAFEOS_BUILD_ROOT

case "$SAFEOS_BUILD_ROOT" in
  "/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a"|"/safeos/SafeOS-build/safeos-linux-distro-a"|"/var/lib/safeos-build/safeos-linux-distro-a") ;;
  *) echo "Refusing test output outside the external SafeOS workspace: $SAFEOS_BUILD_ROOT" >&2; exit 1 ;;
esac

mkdir -p "$SAFEOS_BUILD_ROOT/tests"

while IFS= read -r -d '' script; do
  bash -n "$script"
done < <(find "$ROOT_DIR" -type f -name '*.sh' -print0)

PYTHONDONTWRITEBYTECODE=1 python3 - "$ROOT_DIR" <<'PY'
import ast
import sys
from pathlib import Path

root = Path(sys.argv[1])
for path in root.rglob('*.py'):
    if '.git' not in path.parts:
        ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
PY

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "$ROOT_DIR/tests" -v
bash "$ROOT_DIR/tests/test_update_manager.sh"

LAUNCH_TEST_DIR="$(mktemp -d "$SAFEOS_BUILD_ROOT/tests/launch.XXXXXX")"
mkdir -p "$LAUNCH_TEST_DIR/bin"
cat > "$LAUNCH_TEST_DIR/bin/firefox-esr" <<'EOF'
#!/bin/sh
exit 42
EOF
chmod +x "$LAUNCH_TEST_DIR/bin/firefox-esr"
"${CC:-cc}" -std=c11 -D_POSIX_C_SOURCE=200809L -O2 -Wall -Wextra -Werror \
  "$ROOT_DIR/apps/common/safeos_app.c" "$ROOT_DIR/tests/test_safeos_app.c" \
  -o "$LAUNCH_TEST_DIR/test-safeos-app"
PATH="$LAUNCH_TEST_DIR/bin:$PATH" "$LAUNCH_TEST_DIR/test-safeos-app"

APP_TEST_DIR="$(mktemp -d "$SAFEOS_BUILD_ROOT/tests/apps.XXXXXX")"
bash "$ROOT_DIR/apps/build.sh" "$APP_TEST_DIR"
python3 - "$APP_TEST_DIR" <<'PY'
import sys
from pathlib import Path

expected = {
  'calculator', 'camera', 'fileexplorer', 'jiraffeterminal', 'mediaplayer',
  'orbitalcode', 'safebrowser', 'safedeck', 'safewriter', 'settings',
  'spreadsheet',
}
actual = {path.name for path in Path(sys.argv[1]).iterdir() if path.is_file()}
if actual != expected:
  raise SystemExit(f'Unexpected app binaries: missing={expected - actual}, extra={actual - expected}')
PY

echo "SafeOS source and configuration checks passed"