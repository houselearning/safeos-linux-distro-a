#!/usr/bin/env python3
"""Text preview of available app names; no custom desktop panel is installed."""

PINNED_APPS = [
    "SafeBrowser",
    "Files",
    "Calculator",
    "Spreadsheet",
    "Settings",
    "Terminal",
    "Media Player",
]


def render_action_bar():
    print("Action Bar")
    for app in PINNED_APPS:
        print(f"- {app}")


if __name__ == '__main__':
    render_action_bar()
