# SafeCloud backend architecture

## Service components
- **Auth service**: classroom account, token management, MFA, and role-based permissions
- **Classroom service**: student roster, assignment sync, remote monitoring
- **Policy engine**: blocking, restrictions, and audit logging
- **Messaging service**: teacher and student notifications
- **Storage service**: file sync, backups, and content sharing
- **AI moderation service**: safe browsing, spam filtering, and content policy checks

## Deployment modes
- Hosted cloud
- School district private cloud
- Air-gapped classroom mode

## API examples
- `POST /api/v1/policies/apply`
- `POST /api/v1/classroom/monitor`
- `POST /api/v1/assignments/sync`
- `POST /api/v1/alerts/teacher`
