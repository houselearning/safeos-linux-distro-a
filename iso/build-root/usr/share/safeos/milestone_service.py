#!/usr/bin/env python3
"""Hidden milestone tracking service for SafeOS."""

import argparse
import os
import time
from pathlib import Path

LOG_DIR = Path(os.environ.get('SAFEOS_MILESTONE_LOG', '/var/log/safeos'))
LOG_FILE = LOG_DIR / 'milestone-service.log'

MILESTONES = {
    'boot': 'Boot sequence started',
    'post': 'Post-install and first-run tasks',
    'startup': 'Desktop session startup',
    'shutdown': 'Shutdown sequence triggered',
    'crash': 'Crash or unexpected termination',
}


def ensure_log_dir():
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        pass


def write_milestone(event: str, hidden: bool = False) -> None:
    ensure_log_dir()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    message = MILESTONES.get(event, f'Unknown milestone event: {event}')
    record = f'[{timestamp}] {event.upper()}: {message}\n'
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
            log_file.write(record)
    except PermissionError:
        pass
    if not hidden:
        print(record.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description='SafeOS milestone service')
    parser.add_argument('--event', type=str, choices=MILESTONES.keys(), default='boot')
    parser.add_argument('--hidden', action='store_true', help='Do not write visible output')
    args = parser.parse_args()

    write_milestone(args.event, args.hidden)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
