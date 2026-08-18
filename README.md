# BookOps AI

A working MVP for a salon, clinic or small business: public booking, owner dashboard, customer and service management, booking lifecycle, statistics, reminders, notifications and a structured AI-style agent flow.

## What is included

- Public home, services, contact and booking pages
- Real-time available-slot calculation
- Customer creation/reuse by phone number
- Booking lifecycle: `PENDING`, `CONFIRMED`, `DONE`, `CANCELLED`, `NO_SHOW`
- Protected owner dashboard
- Booking, customer and service management
- Booking status changes and cancellation reasons
- Statistics cards and a 14-day line chart
- Booking analysis: priority, duration, conflict explanation, reply draft and upsell suggestion
- Daily summary with metrics and recommendations
- Installable PWA shell
- Telegram and SMTP notification adapters
- Background worker for reminders and daily summaries
- PostgreSQL, FastAPI, React/Vite and Docker Compose
- Caddy configuration, Uptime Kuma profile, backup/restore scripts and GitHub Actions

## Screens and routes

### Public

- `/` — landing page
- `/services` — active services
- `/book` — customer booking form
- `/contact` — contact details
- `/login` — owner sign-in

### Owner

- `/dashboard` — today and headline metrics
- `/dashboard/bookings`
- `/dashboard/customers`
- `/dashboard/services`
- `/dashboard/stats`
- `/dashboard/ai`

## Quick start with Docker

1. Copy the environment file:

```bash
cp .env.example .env
```

2. Change at least these values in `.env`:

```env
POSTGRES_PASSWORD=a-strong-database-password
JWT_SECRET=a-long-random-secret
ADMIN_EMAIL=your-owner-email@example.com
ADMIN_PASSWORD=a-strong-owner-password
```

3. Start the project:

```bash
docker compose up -d --build
```

4. Open:

- Public site and dashboard: `http://localhost:8080`
- Backend API docs: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/api/health`

The owner account is seeded from `ADMIN_EMAIL` and `ADMIN_PASSWORD` on the first startup.

## Local development without Docker

### Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

For a fast local setup, use SQLite:

```env
DATABASE_URL=sqlite:///./bookops.db
JWT_SECRET=local-development-secret
ADMIN_EMAIL=owner@bookops.local
ADMIN_PASSWORD=ChangeMe123!
```

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to `http://localhost:8000`.

## Test

```bash
cd backend
pytest -q
```

The test suite covers health, login, availability, public booking, AI analysis and booking status changes.

## AI agent design

The included agent is deliberately deterministic so the project works without a paid model key. It follows this flow:

```text
Read booking
   -> Check conflicts using backend rules
   -> Analyze notes and service
   -> Set priority and duration
   -> Draft a reply and upsell
   -> Save structured output
```

The daily report reads real booking and service records, calculates status counts and income, then creates recommendations. This can later be replaced or extended with LangGraph and a hosted language model while keeping the same endpoints and frontend.

## Notifications

### Telegram

Set:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### Email

Set:

```env
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
NOTIFICATION_EMAIL=owner@example.com
```

Without either configuration, notifications are written to backend logs so the booking still succeeds.

## Monitoring

Start Uptime Kuma:

```bash
docker compose --profile monitoring up -d uptime-kuma
```

Open `http://localhost:3001` and add checks for:

- `http://api:8000/api/health` from inside the Docker network, or the public health URL after deployment
- the frontend URL
- the status of the database through the API health result

## Production profile

Edit `infrastructure/caddy/Caddyfile` and replace the example domains and email, then run:

```bash
docker compose --profile production --profile monitoring up -d --build
```

Example domains:

- `booking.example.com`
- `api.booking.example.com`
- `status.booking.example.com`

## Backups

```bash
./infrastructure/scripts/backup.sh
```

Restore:

```bash
./infrastructure/scripts/restore.sh backups/bookops_YYYYMMDD_HHMMSS.sql.gz
```

Test the restore process before using the system for real customer data.

## Repository structure

```text
bookops-ai/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── core/
│   │   ├── jobs/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
├── frontend/
│   ├── public/
│   └── src/
├── infrastructure/
│   ├── caddy/
│   └── scripts/
├── docs/
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Security before real deployment

This repository is a strong internship MVP, not a finished regulated-business product. Before accepting real customer data:

- Replace every default secret and credential.
- Add Alembic migrations instead of relying on automatic table creation.
- Add application-level rate limiting to login and booking endpoints.
- Restrict CORS to the real frontend domains.
- Review privacy and retention requirements for customer records.
- Add CSRF protection if switching from bearer tokens to cookie sessions.
- Use a managed secret store or protected VPS environment file.
- Add automated backup verification and off-server backup storage.
- Add end-to-end and concurrency tests.
- Review time-zone and daylight-saving behavior for the target business.

## Suggested next upgrades

- LangGraph with model tool-calling
- Hebrew and Arabic translations with RTL switching
- Staff roles and per-staff calendars
- Multi-tenant businesses
- WhatsApp provider integration
- Calendar synchronization
- PDF confirmations or invoices
- Push notifications
- Alembic migrations and stronger audit logs

## LeadFlow-style VPS deployment path

The production workflow follows the same operational pattern used by the LeadFlow reference project: Docker Compose on an Ubuntu VPS, a non-root deploy user, host-level Nginx, Cloudflare/SSL, Uptime Kuma, backups, and GitHub Actions over SSH.

### 1. First server setup

Run once as root on a fresh Ubuntu VPS:

```bash
cd /opt/bookops-ai
sudo ./deploy/server-setup.sh
```

Then add your SSH public key to the `deploy` user's `authorized_keys` and use the non-root account for normal deployments.

### 2. Production environment

```bash
cd /opt/bookops-ai
cp .env.example .env
nano .env
```

Change at least `POSTGRES_PASSWORD`, `JWT_SECRET`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD`. Never commit `.env`.

### 3. Start the application

```bash
docker compose up -d --build
docker compose --profile monitoring up -d uptime-kuma
```

The application ports bind to localhost on the VPS. Nginx is the public entry point.

### 4. Nginx + HTTPS

```bash
sudo cp deploy/nginx.bookops.conf /etc/nginx/sites-available/bookops
sudo ln -s /etc/nginx/sites-available/bookops /etc/nginx/sites-enabled/bookops
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d booking.example.com -d status.booking.example.com
```

Replace the example domains in `deploy/nginx.bookops.conf` first. With Cloudflare, point the A records at the VPS and use Full (strict) SSL after the origin certificate is valid.

### 5. CI/CD

Create these GitHub repository secrets:

- `VPS_HOST`
- `VPS_USER` (recommended: `deploy`)
- `VPS_SSH_KEY`

Every push to `main` then executes `.github/workflows/deploy.yml`, which connects using the key and runs `deploy/deploy.sh`.

### 6. Backups

```bash
./deploy/backup-db.sh
```

The script stores compressed PostgreSQL dumps in `/opt/bookops-ai/backups` and prunes backups older than 14 days by default.
