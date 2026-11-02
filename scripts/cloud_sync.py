#!/usr/bin/env python3
"""SafeCloud integration boundary; no backend is configured in this release."""

import sys


class CloudServiceUnavailable(RuntimeError):
    pass


def sync_classroom() -> None:
    raise CloudServiceUnavailable(
        'SafeCloud sync is unavailable: no service endpoint or authentication contract is configured.'
    )


if __name__ == '__main__':
    try:
        sync_classroom()
    except CloudServiceUnavailable as error:
        print(error, file=sys.stderr)
        raise SystemExit(2)
