# API Overview

Interactive OpenAPI documentation is available at `/docs` when the backend is running.

## Public

- `GET /api/health`
- `GET /api/services`
- `GET /api/availability?service_id=1&date=2026-08-10`
- `POST /api/bookings/public`
- `POST /api/auth/login`

## Authenticated owner endpoints

- `GET /api/auth/me`
- `POST /api/services`
- `PUT /api/services/{id}`
- `DELETE /api/services/{id}`
- `GET /api/bookings`
- `GET /api/bookings/{id}`
- `PUT /api/bookings/{id}`
- `PATCH /api/bookings/{id}/status`
- `POST /api/bookings/{id}/notes`
- `GET /api/customers`
- `PUT /api/customers/{id}`
- `POST /api/ai/analyze-booking/{id}`
- `POST /api/ai/daily-summary`
- `GET /api/ai/summaries`
- `GET /api/stats/overview`
- `GET /api/stats/bookings`
