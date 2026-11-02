#!/usr/bin/env python3
"""User-local SafeOS preference storage; this is not a system registry."""

import argparse
import json
import os
import tempfile
from pathlib import Path

ALLOWED_KEYS = frozenset({
    'desktop.theme',
    'desktop.wallpaper',
    'desktop.sound',
})

def settings_path() -> Path:
    override = os.environ.get('SAFEOS_SETTINGS_FILE')
    if override:
        return Path(override)
    config_home = Path(os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config'))
    return config_home / 'safeos' / 'settings.json'


def _read_settings(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    settings = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(settings, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in settings.items()
    ):
        raise ValueError('SafeOS settings file must contain a string-to-string object')
    return settings


def set_value(key: str, value: str) -> None:
    if key not in ALLOWED_KEYS:
        raise ValueError(f'unsupported SafeOS preference: {key}')
    if len(value) > 1024 or any(ord(character) < 32 for character in value):
        raise ValueError('preference value is too long or contains control characters')

    path = settings_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    settings = _read_settings(path)
    settings[key] = value

    descriptor, temporary_name = tempfile.mkstemp(prefix='.settings-', dir=path.parent)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump(settings, output, indent=2, sort_keys=True)
            output.write('\n')
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary_name, path)
    except Exception:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def get_value(key: str) -> str | None:
    if key not in ALLOWED_KEYS:
        raise ValueError(f'unsupported SafeOS preference: {key}')
    return _read_settings(settings_path()).get(key)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read or set local SafeOS preferences')
    commands = parser.add_subparsers(dest='operation', required=True)
    setter = commands.add_parser('set')
    setter.add_argument('key')
    setter.add_argument('value')
    getter = commands.add_parser('get')
    getter.add_argument('key')
    arguments = parser.parse_args()

    if arguments.operation == 'set':
        set_value(arguments.key, arguments.value)
    else:
        value = get_value(arguments.key)
        if value is not None:
            print(value)
