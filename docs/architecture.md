# Architecture

```text
Customer / Owner Browser
        |
  Cloudflare + TLS
        |
      Caddy
        |
  -----------------
  |               |
Frontend/Nginx   FastAPI
                    |
        -------------------------
        |            |          |
   PostgreSQL     Worker     Rule Agent
                     |
             Telegram / SMTP
```

## Booking flow

1. The customer loads active services from `GET /api/services`.
2. The frontend requests available slots from `GET /api/availability`.
3. The backend calculates duration and checks interval overlap against pending or confirmed bookings.
4. The booking and customer are stored in one database transaction.
5. A configured Telegram or email notification is sent; otherwise the message is logged.
6. The owner manages the booking in the protected dashboard.
7. The agent produces structured booking analysis and daily summaries.
8. The worker sends reminders and creates the evening report.

## Important design decision

Time conflicts are determined by backend/database rules, not by a language model. The AI layer explains and summarizes reliable system data.
