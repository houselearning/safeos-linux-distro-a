#!/usr/bin/env python3
"""Validate staged files before live-build incorporates them into the image."""

import configparser
import sys
from pathlib import Path


EXPECTED_LAUNCHERS = {
    'safeos-browser.desktop',
    'safeos-files.desktop',
    'safeos-calculator.desktop',
    'safeos-spreadsheet.desktop',
    'safeos-writer.desktop',
    'safeos-presentation.desktop',
    'safeos-media-player.desktop',
    'safeos-camera.desktop',
    'safeos-settings.desktop',
    'safeos-terminal.desktop',
    'safeos-code.desktop',
}
REQUIRED_FILES = {
    'usr/local/sbin/safeos-update',
    'usr/local/bin/safeos-settings',
    'usr/local/bin/safeos-notify',
    'usr/local/bin/safeos-setup',
    'usr/local/lib/safeos/first_boot.py',
    'usr/share/safeos/setup-wallpaper.png',
    'usr/share/safeos/safenotify/notify.py',
    'etc/xdg/autostart/safeos-setup.desktop',
}
FORBIDDEN_PATHS = {
    'etc/xdg/autostart/safeos-milestone.desktop',
    'etc/xdg/autostart/safeos-session.desktop',
    'usr/share/safeos/milestone_service.py',
    'usr/share/safeos/milestone-service.sh',
    'usr/share/safeos/safeos-session.sh',
}


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: check_image_tree.py <chroot-includes-directory>', file=sys.stderr)
        return 64

    root = Path(sys.argv[1])
    applications = root / 'usr/share/applications'
    actual_launchers = {path.name for path in applications.glob('*.desktop')}
    if actual_launchers != EXPECTED_LAUNCHERS:
        print(
            f'Unexpected desktop launchers: missing={sorted(EXPECTED_LAUNCHERS - actual_launchers)}, '
            f'extra={sorted(actual_launchers - EXPECTED_LAUNCHERS)}',
            file=sys.stderr,
        )
        return 1

    for launcher in sorted(actual_launchers):
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(applications / launcher, encoding='utf-8')
        executable = parser.get('Desktop Entry', 'Exec', fallback='').split()
        if not executable or not executable[0].startswith('/'):
            print(f'Invalid Exec target in {launcher}', file=sys.stderr)
            return 1
        target = root / executable[0].lstrip('/')
        if not target.is_file() or not target.stat().st_mode & 0o111:
            print(f'Launcher target is missing or not executable: {launcher}', file=sys.stderr)
            return 1

    for relative_path in sorted(REQUIRED_FILES):
        if not (root / relative_path).is_file():
            print(f'Missing required image utility: {relative_path}', file=sys.stderr)
            return 1

    setup_autostart = configparser.ConfigParser(interpolation=None)
    setup_autostart.read(root / 'etc/xdg/autostart/safeos-setup.desktop', encoding='utf-8')
    setup_command = setup_autostart.get('Desktop Entry', 'Exec', fallback='').split()
    if not setup_command or setup_command[0] != '/usr/local/bin/safeos-setup':
        print('First-run autostart does not target the installed SafeOS setup command', file=sys.stderr)
        return 1
    setup_executable = root / setup_command[0].lstrip('/')
    if not setup_executable.is_file() or not setup_executable.stat().st_mode & 0o111:
        print('SafeOS first-run command is missing or not executable', file=sys.stderr)
        return 1

    for relative_path in sorted(FORBIDDEN_PATHS):
        if (root / relative_path).exists():
            print(f'Forbidden hidden service staged in image: {relative_path}', file=sys.stderr)
            return 1

    print(f'Image staging passed ({len(actual_launchers)} launchers, no hidden services)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())