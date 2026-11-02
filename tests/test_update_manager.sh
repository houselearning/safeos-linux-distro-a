#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAFEOS_BUILD_ROOT="${SAFEOS_BUILD_ROOT:-/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a}"
TEST_DIR="$(mktemp -d "$SAFEOS_BUILD_ROOT/tests/update.XXXXXX")"
trap 'rm -rf -- "$TEST_DIR"' EXIT

mkdir -p "$TEST_DIR/bin"
cat > "$TEST_DIR/bin/apt-get" <<'EOF'
#!/bin/sh
printf '%s\n' "$*" >> "$SAFEOS_APT_LOG"
EOF
chmod +x "$TEST_DIR/bin/apt-get"

SAFEOS_APT_LOG="$TEST_DIR/apt.log" PATH="$TEST_DIR/bin:/usr/bin:/bin" \
  bash "$ROOT_DIR/system/update_manager.sh" check

expected=$(printf 'update\n--simulate upgrade')
actual="$(<"$TEST_DIR/apt.log")"
if [[ "$actual" != "$expected" ]]; then
  printf 'Unexpected safeos-update check calls:\n%s\n' "$actual" >&2
  exit 1
fi

echo "SafeOS update check uses signed APT metadata and simulation"