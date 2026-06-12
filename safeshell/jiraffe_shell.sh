#!/usr/bin/env bash
set -euo pipefail

DEVICE_NAME="${SAFEOS_DEVICE_NAME:-safe-top}"
USER_NAME="${USER:-student}"

prompt() {
  printf "@safeos/%s/%s:> " "$DEVICE_NAME" "$USER_NAME"
}

while true; do
  prompt
  read -r command
  case "$command" in
    exit|quit) break ;;
    help) echo "SafeShell commands: safecloud, krow, vm, export, status" ;;
    safecloud) echo "SafeCloud: connected" ;;
    krow) echo "Krow Diagnostics: ready" ;;
    vm) echo "VirtualCloud: VM profile loaded" ;;
    export) echo "Exporting workspace metadata" ;;
    status) echo "SafeShell healthy" ;;
    *) echo "Unknown command: $command" ;;
  esac
done
