#!/usr/bin/env python3
"""JiraffeScript is not implemented in this release."""


def run_script(script_path: str) -> None:
    raise RuntimeError(
        f'JiraffeScript is unavailable; {script_path!r} was not parsed or executed.'
    )


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit('Usage: jiraffescript.py <script.jf>')
    try:
        run_script(sys.argv[1])
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(69)
