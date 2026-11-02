#!/usr/bin/env python3
"""SafeCloud and VirtualCloud integration boundaries."""


class CloudServiceUnavailable(RuntimeError):
    pass


def teacher_dashboard() -> dict:
    raise CloudServiceUnavailable(
        'SafeCloud dashboard is unavailable: no backend or credentials are configured.'
    )


if __name__ == '__main__':
    teacher_dashboard()
