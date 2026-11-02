# Virtualization status

The image targets Debian `amd64` and is intended to be smoke-tested in QEMU. VMware, VirtualBox, Chromebook-specific tools, and cloud classroom VM profiles have not been validated.

## VirtualCloud

The `apps/virtualcloud` directory is a scaffold. No hosted VM, shared classroom desktop, account integration, or storage service is deployed.

## VM test scope

QEMU BIOS and EFI boot plus disposable installation smoke tests are the virtual acceptance gates. A VM boot does not certify physical Wi-Fi, graphics, sound, touch, camera, Thunderbolt, or Chromebook compatibility.
