#!/usr/bin/env python3
"""Notification center helper for SafeOS."""

import argparse
import shutil
import subprocess


def notify(event: str, message: str = "") -> None:
    if not event.strip():
        raise ValueError('notification event must not be empty')

    command = shutil.which('notify-send')
    if command is None:
        raise RuntimeError('desktop notification service is unavailable')

    subprocess.run(
        [command, '--app-name=SafeOS', event, message or 'System notification'],
        check=True,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', required=True)
    parser.add_argument('--message', default='')
    args = parser.parse_args()
    notify(args.event, args.message)
