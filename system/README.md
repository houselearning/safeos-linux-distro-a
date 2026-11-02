# System module status

These modules are source interfaces, not background daemons. Only the manual Debian APT updater and user-local preference storage have functional behavior in this release.

## Modules
- `driver_manager.py` — explicitly unavailable; no hardware detection or driver installer
- `update_manager.sh` — `safeos-update check|apply`, root-gated and user-triggered
- `registry_editor.py` — allowlisted user-local preferences; no system registry or sector edits
- `cloud_manager.py` — explicit unavailable error until a SafeCloud backend exists
- `security_suite.py` — explicit unavailable error until a scanner is configured
