#!/usr/bin/env python3
"""Registry editor prototype for SafeOS."""

import json


def set_value(key: str, value: str):
    print(json.dumps({'key': key, 'value': value}, indent=2))


if __name__ == '__main__':
    set_value('desktop.theme', 'safeos-retro-blue')
