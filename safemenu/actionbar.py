#!/usr/bin/env python3
"""Action Bar placeholder logic for SafeOS."""

PINNED_APPS = [
    "SafeBrowser",
    "Orbital Code",
    "SafeStore",
    "Settings",
    "VirtualCloud",
]


def render_action_bar():
    print("Action Bar")
    for app in PINNED_APPS:
        print(f"- {app}")


if __name__ == '__main__':
    render_action_bar()
