# SafeOS architecture

## Goals
SafeOS is a modular school-first distribution that emphasizes security, manageability, and low-resource performance.

## Core layers
1. **Boot and diagnostics**
   - Custom GRUB theme
   - Krow Diagnostics boot screen
   - Retro splash and startup sound
2. **Desktop environment**
   - KDE Plasma or XFCE with custom themes, icons, cursor themes, and Action Bar
   - Draggable desktop icons and window snapping
3. **SafeShell and system services**
   - Custom shell prompt and scripting language
   - Notification, cloud, and registry services
4. **Applications**
   - Browser, office suite, IDE, store, diagnostics, terminal, media, and cloud tools
5. **Cloud and management**
   - SafeCloud teacher dashboard
   - VirtualCloud classroom manager
   - ZeroCheat and policy enforcement

## Modular design
Each app lives in its own folder and exposes a common interface through `apps/common/`.

## Performance focus
- Lightweight desktop session
- Minimal startup services
- Driver detection and fallback profiles for old Chromebooks and school desktops
- Optional AI moderation, disabled by default for privacy
