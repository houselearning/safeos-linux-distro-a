# Security and privacy model

## Threat model
SafeOS is an experimental Debian-derived desktop. Its security properties are those of Debian packages and their default configuration. This repository does not implement a custom sandbox, malware scanner, policy engine, SafeCloud client, exam-control mechanism, or device-management agent.

## Implemented protections and limits

- Debian APT verifies signed repository metadata and package hashes against the Debian archive keyring.
- The release workflow records a SHA-256 checksum, but does not publish a SafeOS signing key or signed ISO. A checksum detects accidental changes; by itself it does not authenticate the publisher.
- App launch wrappers use a fixed command allowlist and call `execvp`; they do not pass command text through a shell.
- Unconfigured cloud and security modules return explicit unavailable errors rather than sample data or fake success.
- The desktop image does not autostart telemetry. No usage, screen, keystroke, browsing, or student-behavior data is collected by SafeOS code.
- Installing an OS can overwrite the selected disk. Users must back up data and confirm the target in Debian Installer.
- The live session is ephemeral unless the user configures persistence. Recovery, rollback, Secure Boot certification, and physical-device testing are not provided. Debian Installer may offer Debian's standard encryption options, but these have not been customized or validated for SafeOS.

## Excluded behavior

No hidden monitoring, screen viewing or takeover, keylogging, exam surveillance, adaptive student profiling, punitive lockout, or intentional vulnerability/advertising behavior is implemented. No security property should be inferred from scaffold names such as `security_suite.py`, `ZeroCheat`, or `Defendant`.

## Threat model

The current release assumes a trusted Debian archive and a user who selects packages from that archive. It does not defend against a compromised firmware, malicious physical administrator, hostile cloud service, untrusted third-party app, or theft of unencrypted user data. A future remote-support feature requires a separate threat model, visible consent, revocation, strict least privilege, and a verified service contract.
