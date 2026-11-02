#!/usr/bin/env python3
"""Optional, local-only SafeOS milestones. Nothing is recorded without consent."""

import argparse
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

RETENTION_DAYS = 7
MILESTONES = {
    'boot': 'Boot sequence started',
    'startup': 'Desktop session started',
    'shutdown': 'Shutdown sequence started',
}


def log_path() -> Path:
    override = os.environ.get('SAFEOS_MILESTONE_LOG')
    if override:
        return Path(override)
    state_home = Path(os.environ.get('XDG_STATE_HOME', Path.home() / '.local/state'))
    return state_home / 'safeos' / 'milestones.log'


def _retained_records(lines: list[str], now: datetime) -> list[str]:
    cutoff = now - timedelta(days=RETENTION_DAYS)
    retained = []
    for line in lines:
        try:
            timestamp = datetime.fromisoformat(line.split('\t', 1)[0])
        except (ValueError, IndexError):
            continue
        if timestamp >= cutoff:
            retained.append(line)
    return retained


def record(event: str, consent: bool) -> None:
    if not consent:
        raise PermissionError('milestone recording requires explicit --consent')
    if event not in MILESTONES:
        raise ValueError(f'unsupported milestone event: {event}')

    path = log_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    lines = path.read_text(encoding='utf-8').splitlines() if path.exists() else []
    retained = _retained_records(lines, now)
    retained.append(f'{now.isoformat()}\t{event}\t{MILESTONES[event]}')
    path.write_text('\n'.join(retained) + '\n', encoding='utf-8')
    path.chmod(0o600)


def inspect() -> list[str]:
    path = log_path()
    if not path.exists():
        return []
    now = datetime.now(timezone.utc)
    lines = path.read_text(encoding='utf-8').splitlines()
    retained = _retained_records(lines, now)
    if retained != lines:
        if retained:
            path.write_text('\n'.join(retained) + '\n', encoding='utf-8')
            path.chmod(0o600)
        else:
            path.unlink()
    return retained


def clear() -> None:
    path = log_path()
    if path.exists():
        path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description='Optional local SafeOS milestones')
    commands = parser.add_subparsers(dest='command', required=True)

    record_parser = commands.add_parser('record')
    record_parser.add_argument('event', choices=sorted(MILESTONES))
    record_parser.add_argument('--consent', action='store_true')
    commands.add_parser('inspect')
    commands.add_parser('clear')
    args = parser.parse_args()

    if args.command == 'record':
        record(args.event, args.consent)
    elif args.command == 'inspect':
        for line in inspect():
            print(line)
    else:
        clear()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
