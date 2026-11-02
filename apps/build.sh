#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAFEOS_BUILD_ROOT="${SAFEOS_BUILD_ROOT:-/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a}"
OUTPUT_DIR="${1:?Usage: apps/build.sh <external-build-output-directory>}"
APP_NAMES=(calculator fileexplorer safebrowser safedeck safewriter spreadsheet mediaplayer camera settings jiraffeterminal orbitalcode)

case "$SAFEOS_BUILD_ROOT" in
  "/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a"|"/safeos/SafeOS-build/safeos-linux-distro-a"|"/var/lib/safeos-build/safeos-linux-distro-a") ;;
  *) echo "Refusing build root outside the external SafeOS workspace: $SAFEOS_BUILD_ROOT" >&2; exit 1 ;;
esac
case "$OUTPUT_DIR" in
  "$SAFEOS_BUILD_ROOT"/*) ;;
  *) echo "Refusing app output outside $SAFEOS_BUILD_ROOT: $OUTPUT_DIR" >&2; exit 1 ;;
esac

if [[ -L "$OUTPUT_DIR" ]]; then
  echo "Refusing symlinked app output directory: $OUTPUT_DIR" >&2
  exit 1
fi
mkdir -p "$OUTPUT_DIR"
OUTPUT_REAL="$(cd "$OUTPUT_DIR" && pwd -P)"
case "$OUTPUT_REAL" in
  "$SAFEOS_BUILD_ROOT"/*) ;;
  *) echo "Refusing app output outside $SAFEOS_BUILD_ROOT: $OUTPUT_REAL" >&2; exit 1 ;;
esac
CC="${CC:-cc}"
if ! command -v "$CC" >/dev/null 2>&1; then
  echo "C compiler not found: $CC" >&2
  exit 1
fi

for app_name in "${APP_NAMES[@]}"; do
  app_dir="$ROOT_DIR/apps/$app_name"
  if [[ ! -f "$app_dir/main.c" ]]; then
    echo "Missing source for allowlisted app '$app_name'" >&2
    exit 1
  fi
  "$CC" -std=c11 -D_POSIX_C_SOURCE=200809L -O2 -Wall -Wextra -Werror \
    "$app_dir/main.c" "$ROOT_DIR/apps/common/safeos_app.c" \
    -o "$OUTPUT_DIR/$app_name"
done