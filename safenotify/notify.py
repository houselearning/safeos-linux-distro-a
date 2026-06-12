#!/usr/bin/env python3
"""Notification center helper for SafeOS."""

import argparse


def notify(event: str, message: str = ""):
    label = "[SafeNotify]"
    print(f"{label} {event}: {message or 'system update'}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--event', required=True)
    parser.add_argument('--message', default='')
    args = parser.parse_args()
    notify(args.event, args.message)
