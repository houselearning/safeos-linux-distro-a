#!/usr/bin/env python3
"""JiraffeScript is a lightweight command DSL for SafeOS."""

from pathlib import Path


def run_script(script_path: str):
    content = Path(script_path).read_text()
    commands = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith('#')]
    for command in commands:
        print(f"[jiraffescript] {command}")


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit('Usage: jiraffescript.py <script.jf>')
    run_script(sys.argv[1])
