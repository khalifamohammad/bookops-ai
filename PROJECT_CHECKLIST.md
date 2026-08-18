# Project brief implementation checklist

| Workstream | Included in this repository | Status |
|---|---|---|
| 01 Public booking website | Home, services, booking, contact, responsive layout and RTL direction toggle | Implemented |
| 02 Owner dashboard | Login, booking list, status changes, rescheduling, notes, customers, services, statistics | Implemented |
| 03 AI agent / agent flow | Conflict-aware booking analysis, priorities, reply drafts, upsells and daily recommendations | Implemented as deterministic agent flow |
| 04 Backend API | Authentication, CRUD-style operations, AI, statistics, daily report and health endpoints | Implemented |
| 05 Database | PostgreSQL-ready SQLAlchemy schema for required core tables | Implemented |
| 06 Owner app / PWA | Responsive owner dashboard, manifest, service worker, quick call and copy-phone actions | Implemented |
| 07 Automations / integration | New-booking notification, reminder worker, evening summary, cancellation reasons and webhook simulation | Implemented; external credentials required |
| 08 VPS / Linux | Deployment checklist and deploy script | Configuration/documentation included; not deployed |
| 09 Docker | Frontend, backend, PostgreSQL and worker in Compose | Implemented; not executed in generation environment |
| 10 DNS / Cloudflare | Example domains, Caddy TLS proxy and deployment instructions | Configuration/documentation included |
| 11 Monitoring / logging | Health API, application logs and optional Uptime Kuma service | Implemented/configured |
| 12 Security | PBKDF2 password hashing, JWT, protected routes, validation, basic rate limiting, spam honeypot, environment variables and backups | Implemented at MVP level |
| 13 CI/CD | GitHub Actions tests/build and deployment script | Implemented |
| 14 Documentation | README, architecture, API, database, deployment and build-status documents | Implemented |

## Deliberately left as later upgrades

- Multi-tenant businesses
- Full Hebrew/Arabic translations
- Staff roles
- Real WhatsApp provider
- Calendar synchronization
- PDF invoices
- Push notifications
- Alembic migration history
- Distributed rate limiting
- Hosted LLM/LangGraph integration
