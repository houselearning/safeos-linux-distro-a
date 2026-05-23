# SafeOS

SafeOS is a lightweight, education-first Linux distribution designed for refurbished school hardware, classroom virtualization, and a polished retro-modern desktop experience.

## Goals
- Linux-based custom distro for low-end hardware
- Windows 95/XP-inspired UI with ChromeOS-like simplicity
- SafeCloud, SafeSuite, SafeStore, SafeAI, Krow Diagnostics, Jiraffe Terminal, Orbital Code, VirtualCloud, and ZeroCheat integrated into one ecosystem
- Buildable with Debian/Ubuntu live-build tooling

## Key folders
- `iso/` — output artifacts and release notes
- `live-build/` — live-build customization inputs
- `scripts/` — build and validation helpers
- `branding/` — logos, splash text, identity assets
- `icons/` — app and desktop icon manifest
- `themes/` — desktop themes and palette hints
- `wallpapers/` — backgrounds and custom wallpaper metadata
- `desktop/` — desktop environment and session configs
- `safeshell/` — SafeShell and JiraffeScript tooling
- `safemenu/` — Action Bar and start-menu logic
- `safenotify/` — notification center and filtering helpers
- `apps/` — modular built-in application stubs
- `system/` — drivers, updater, security, cloud, registry, and sync services
- `drivers/` — driver management manifests
- `postinstall/` — first-boot and setup workflows
- `docs/` — architecture, UX, boot, API, and build documentation

## Build approach
1. Prepare the live-build tree.
2. Generate branding and desktop configuration.
3. Assemble a Debian/Ubuntu-based ISO.
4. Run validation scripts and a first-boot smoke test.

## Asset references
- `default.jpg`
- `safeos-dark.png`
- `safeos-light.png`
- `Copilot_20260321_195502.png`
- `Copilot_20260321_195510.png`
- `Copilot_20260321_195618.png`
- `Copilot_20260321_195827.png`
- `Copilot_20260321_200101.png`
- `Copilot_20260321_200424.png`
- `Copilot_20260321_201544.png`
- `Copilot_20260321_201546.png`
- `Copilot_20260321_201548.png`
