#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RELEASE_DIR="${SAFEOS_RELEASE_DIR:-/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/releases}"
TEST_OUTPUT_DIR="${SAFEOS_TEST_OUTPUT_DIR:-$(dirname "$RELEASE_DIR")/tests}"

case "$RELEASE_DIR" in
  "/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/releases"|"/safeos/SafeOS-build/safeos-linux-distro-a/releases") ;;
  *) echo "Refusing release directory outside the external SafeOS workspace: $RELEASE_DIR" >&2; exit 1 ;;
esac

for tool in sha256sum python3 xorriso; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Required validation tool is missing: $tool" >&2
    exit 1
  fi
done

if [[ ! -d "$RELEASE_DIR" || -L "$RELEASE_DIR" ]]; then
  echo "Invalid release directory: $RELEASE_DIR" >&2
  exit 1
fi
case "$TEST_OUTPUT_DIR" in
  "/Volumes/Other Storage/SafeOS-build/safeos-linux-distro-a/tests"|"/safeos/SafeOS-build/safeos-linux-distro-a/tests") ;;
  *) echo "Refusing validation output outside the external SafeOS workspace: $TEST_OUTPUT_DIR" >&2; exit 1 ;;
esac
if [[ -L "$TEST_OUTPUT_DIR" ]]; then
  echo "Refusing symlinked validation output directory: $TEST_OUTPUT_DIR" >&2
  exit 1
fi
mkdir -p "$TEST_OUTPUT_DIR"

if [[ -n "${SAFEOS_RELEASE_ISO:-}" ]]; then
  iso_path="$SAFEOS_RELEASE_ISO"
  case "$iso_path" in
    "$RELEASE_DIR"/safeos-amd64-*.iso) ;;
    *) echo "Refusing ISO outside the release directory: $iso_path" >&2; exit 1 ;;
  esac
  if [[ ! -f "$iso_path" || -L "$iso_path" ]]; then
    echo "Invalid SafeOS ISO: $iso_path" >&2
    exit 1
  fi
else
  checksum_path="$(find "$RELEASE_DIR" -maxdepth 1 -type f -name 'safeos-amd64-*.iso.sha256' -printf '%T@ %p\n' | sort -nr | sed -n '1s/^[^ ]* //p')"
  if [[ -z "$checksum_path" ]]; then
    echo "No checksummed SafeOS ISO found in $RELEASE_DIR" >&2
    exit 1
  fi
  iso_path="${checksum_path%.sha256}"
fi

iso_name="$(basename "$iso_path")"
checksum_file="$iso_path.sha256"
package_manifest="$iso_path.packages.txt"
builder_manifest="$iso_path.builder-packages.txt"
for required_file in "$checksum_file" "$package_manifest" "$builder_manifest"; do
  if [[ ! -f "$required_file" ]]; then
    echo "Release companion file is missing: $required_file" >&2
    exit 1
  fi
done

(cd "$RELEASE_DIR" && sha256sum --check "$(basename "$checksum_file")")
python3 "$ROOT_DIR/scripts/check_image_manifest.py" "$package_manifest"

catalog_dir="$(mktemp -d "$TEST_OUTPUT_DIR/iso-validation.XXXXXX")"
catalog_file="$catalog_dir/boot-catalog.txt"
xorriso -indev "$iso_path" -report_el_torito plain > "$catalog_file" 2>&1
if ! grep -qi 'El Torito' "$catalog_file"; then
  echo "ISO has no readable El Torito boot catalog" >&2
  exit 1
fi

echo "SafeOS release validation passed: $iso_path"
echo "Package and builder manifests verified; BIOS/EFI boot still requires VM testing."
