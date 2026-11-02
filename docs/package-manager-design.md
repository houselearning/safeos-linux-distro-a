# Package and update policy

## Goals
- Use Debian Bookworm APT repositories only in this release.
- Retain APT signature and package-hash verification.
- Do not install arbitrary downloaded binaries or `.exe` files.
- No SafeStore catalog, group rollout, custom signing key, or multi-architecture promise exists.

## Available tools

The image uses standard Debian `apt`/`apt-get` and `dpkg`. There is no `safepkg` command. `sudo safeos-update check` refreshes signed APT metadata and simulates upgrades; `sudo safeos-update apply` installs Debian full upgrades after explicit user action. There is no unattended update service or rollback. The live session's package database is ephemeral; installed systems use the configured Debian repositories.

`safeos-settings set desktop.theme <value>` and `safeos-settings get desktop.theme` store user-local preferences for `desktop.theme`, `desktop.wallpaper`, and `desktop.sound`. They do not apply XFCE themes, change administrator policy, or write raw storage sectors.

## Trust and provenance

APT verifies signed Release metadata with Debian archive keys and checks downloaded package hashes against the signed indexes. No custom SafeOS package repository or signing key is configured. Application wrappers invoke packaged programs; they do not download code.
