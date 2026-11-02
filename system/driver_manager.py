#!/usr/bin/env python3
"""Hardware detection is not implemented in this release."""


class HardwareDetectionUnavailable(RuntimeError):
    pass


def detect_profile(device_name: str | None = None) -> list[str]:
    raise HardwareDetectionUnavailable(
        'SafeOS does not detect or select drivers; use Debian hardware tools.'
    )


if __name__ == '__main__':
    detect_profile()
