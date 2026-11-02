# Hardware support and drivers

## Tested target

- Build architecture: Debian `amd64` (x86_64).
- Virtual target: QEMU emulated PC hardware; boot verification is required before release.
- Physical laptop, Chromebook, desktop, NVIDIA, Thunderbolt, touchscreen, webcam, audio, and Wi-Fi coverage has not been certified.

## Driver behavior

The image uses the kernel and firmware packages selected by Debian live-build. `drivers/*.yaml` are documentation manifests, not installable drivers. `system/driver_manager.py` does not inspect hardware. Do not rely on it for compatibility, repair, package signing, or device recommendations.
