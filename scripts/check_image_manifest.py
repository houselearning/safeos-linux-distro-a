#!/usr/bin/env python3
"""Validate the packages required by the SafeOS live/install image."""

import sys
from pathlib import Path


REQUIRED_PACKAGES = {
    'live-boot',
    'live-config',
    'linux-image-amd64',
    'debian-installer-launcher',
    'firefox-esr',
    'thunar',
    'galculator',
    'libreoffice-calc',
    'libreoffice-writer',
    'libreoffice-impress',
    'parole',
    'cheese',
    'xfce4-settings',
    'xfce4-terminal',
    'geany',
    'libnotify-bin',
}


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: check_image_manifest.py <binary.packages>', file=sys.stderr)
        return 64

    manifest_path = Path(sys.argv[1])
    if not manifest_path.is_file():
        print(f'Package manifest not found: {manifest_path}', file=sys.stderr)
        return 66

    installed = set()
    for line in manifest_path.read_text(encoding='utf-8').splitlines():
        fields = line.split()
        if fields:
            installed.add(fields[0].split(':', 1)[0])

    missing = sorted(REQUIRED_PACKAGES - installed)
    if missing:
        print(f'Missing required image packages: {", ".join(missing)}', file=sys.stderr)
        return 1

    print(f'Image package manifest passed ({len(installed)} packages, required set present)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())