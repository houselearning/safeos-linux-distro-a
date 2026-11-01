# SafeOS Completion Prompt

Use this prompt with an implementation-capable coding agent after attaching the intended SafeOS roadmap.

---

You are the lead Linux distribution engineer completing SafeOS in this repository. Implement every in-scope item in the attached roadmap end to end: code, integration, tests, documentation, and a boot-verified release artifact. Do not stop at a plan or TODO list.

## Repository and operating constraints

- Project: `/Volumes/Other Storage/GitHub Projects/safeos-linux-distro-a`
- All downloaded dependencies, package caches, container images, VM disks, temporary build trees, logs, test artifacts, and release images must remain on `/Volumes/Other Storage`. Do not install packages or write build artifacts to the internal disk.
- Host: macOS x86_64. `docker` and `qemu-system-x86_64` are available; `live-build` (`lb`) and `xorriso` are unavailable. SafeOS's current image scripts require Linux live-build tooling. Use an isolated Linux container or VM with persistent storage on `/Volumes/Other Storage`; do not run Debian live-build directly on macOS.
- Check `git status` before editing. Preserve all existing and unrelated user changes. Never reset, discard, commit, or push work.
- The attached roadmap is authoritative. If it is unavailable or does not define SafeOS requirements, stop before making product-scope decisions and ask for the correct roadmap. Do not substitute the general HouseLearning roadmap.

## Audit before implementation

Read the roadmap, repository instructions, README, architecture/security/installer/package/driver docs, build scripts, source modules, and tests. Create a traceability table mapping each roadmap item to current evidence, implementation tasks, acceptance tests, and status. Distinguish working behavior from documentation-only claims and stubs. Record unresolved product and security decisions rather than silently inventing answers.

Verify these known findings against the current source:

- `apps/common/safeos_app.c` only prints a launch message; it does not launch applications.
- `scripts/cloud_sync.py` is a stub and does not sync data or enforce policy.
- `scripts/prepare_live_build.sh` packages a basic Debian/XFCE desktop and milestone service, but does not integrate most modules in `apps/`, `system/`, `safeshell/`, `safemenu/`, `safenotify/`, `drivers/`, or `postinstall/`. The generated session script invokes a notification module that is not copied into the image.
- Debian Installer is disabled, while `docs/installer-flow.md` describes an installer and setup wizard not established by the current build recipe.
- `scripts/validate_safeos.sh` checks directories, a few files, shell syntax, and ISO/checksum existence. It does not test build reproducibility, image contents, boot, installation, application behavior, or security properties.
- `scripts/build_iso.sh` defaults its working directory to `/tmp`; `scripts/prepare_live_build.sh` removes `config`, `binary`, and `cache` from the configured build directory. Move build state to the external volume and guard cleanup against unsafe paths.
- The milestone service is labeled hidden and is autostarted in the desktop. Do not ship undisclosed telemetry or monitoring. Make collection transparent, minimal, consent-based, locally inspectable, and controllable; document retention and network behavior. Do not implement covert student surveillance or exam-control behavior.
- The neighboring `docs/roadmap/roadmap-2026.md` is a general HouseLearning roadmap, not a SafeOS plan; its only SafeOS-specific item is “Recognise SafeOS.” Do not treat it as the attached SafeOS roadmap.

## Definition of done

1. Implement every in-scope roadmap item in the appropriate existing modules. Replace stubs with tested behavior or explicitly mark items blocked by missing credentials, services, hardware, or decisions. Never claim an external deployment happened unless verified.
2. Deliver a genuinely usable, installable SafeOS image, not only a branded live session. Define and implement supported hardware/architecture, boot modes, installation and recovery paths, account setup, upgrades, and rollback according to the roadmap. Keep live mode if required; do not disable installation while claiming it is complete.
3. Integrate desktop and applications so menu entries, launchers, autostart services, dependencies, permissions, and configuration work in the built image. Remove placeholder launchers and fail-open scripts that hide broken integration.
4. Implement security and privacy features with documented threat models, least privilege, secure defaults, user-visible controls, and tests. Verify package signatures and update provenance. Do not claim sandboxing, malware protection, policy enforcement, or cloud security unless implemented and tested.
5. Add automated checks for source syntax/types, module behavior, image package/content manifests, installer paths, and security-sensitive configuration. Boot-test in QEMU for supported firmware modes where practical, and perform installation smoke tests in a disposable VM. Label hardware-specific checks that cannot be verified virtually.
6. Make builds reproducible and safe to rerun. Record dependency versions, verify downloaded artifacts, write all generated files and caches to `/Volumes/Other Storage`, and ensure cleanup only removes the dedicated SafeOS build workspace. Never overwrite or delete user data.
7. Update user/developer documentation with actual features, limitations, supported hardware, install and recovery instructions, privacy behavior, and exact build/test commands. Keep docs aligned with the resulting image.
8. Mark a roadmap item complete only after its acceptance test passes. Report evidence, test commands/results, unverified risks, and blockers. A scaffold check or preexisting ISO is not functional verification.

## Work method

- First produce the traceability table and a brief, evidence-based implementation plan.
- Work in small, testable changes. Run the narrowest relevant check after each change, then broader build and VM checks as integration progresses.
- Do not install dependencies until roadmap scope and build approach are confirmed. When needed, keep all dependency state and caches on `/Volumes/Other Storage`; verify paths before downloading or running installers.
- If a requirement is unsafe, impossible, or underspecified, explain the concrete issue and ask for a decision. Do not quietly omit it or invent a substitute.
- Finish with a roadmap checklist showing each item's implementation evidence, validation result, and remaining external or hardware verification.

---