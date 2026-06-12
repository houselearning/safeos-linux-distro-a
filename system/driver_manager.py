#!/usr/bin/env python3
"""Driver manager for SafeOS."""


def detect_profile(device_name: str):
    profiles = {
        'chromebook': ['intel-graphics', 'wifi', 'touchscreen'],
        'optiplex': ['intel-graphics', 'ethernet', 'sound'],
        'refurbished-laptop': ['intel-graphics', 'wifi', 'webcam'],
    }
    return profiles.get(device_name, ['generic'])


if __name__ == '__main__':
    print(detect_profile('refurbished-laptop'))
