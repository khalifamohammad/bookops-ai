# Database Schema

Main entities:

- `users`: owner authentication and role.
- `business_settings`: hours, timezone, interval and reminder configuration.
- `services`: name, duration, price and active state.
- `customers`: customer contact information and internal notes.
- `bookings`: appointment time, lifecycle status, income, cancellation reason and AI analysis.
- `booking_notes`: internal notes attached to bookings.
- `ai_summaries`: generated daily summaries and recommendations.
- `activity_logs`: owner actions for auditability.

Booking lifecycle:

```text
PENDING -> CONFIRMED -> DONE
                    -> CANCELLED
                    -> NO_SHOW
```

The current MVP creates tables automatically on startup. For a long-lived production deployment, add Alembic migrations before changing the schema.
