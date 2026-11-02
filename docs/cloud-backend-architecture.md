# SafeCloud integration status

There is no SafeCloud server or client implementation in this repository. `system/cloud_manager.py` and `scripts/cloud_sync.py` fail explicitly because no endpoint or credentials are configured. The former hard-coded sample dashboard and “policies applied” output have been removed.

## Required before implementation

- An owner-provided endpoint and versioned API contract
- Authentication, authorization, consent, data-retention, deletion, and offline behavior
- Test credentials and a non-production staging service
- Security review and negative authorization tests

No screen monitoring, device takeover, hidden telemetry, student profiling, punitive lockout, or exam surveillance is in scope for the current release.
