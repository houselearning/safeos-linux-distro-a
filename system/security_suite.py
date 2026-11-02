#!/usr/bin/env python3
"""Security integration boundary; no scanner is configured in this release."""


class SecurityEngineUnavailable(RuntimeError):
    pass


def quarantine_site(site: str) -> None:
    raise SecurityEngineUnavailable(
        f'No security engine is configured; {site!r} was not scanned or quarantined.'
    )


if __name__ == '__main__':
    quarantine_site('calculator-cheat.example')
