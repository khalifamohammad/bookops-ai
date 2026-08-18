# BookOps AI

BookOps AI is a full-stack booking and business-management platform for a salon, clinic, or small business.

The system includes a public booking website, owner dashboard, customer and service management, booking lifecycle management, statistics, notifications, reminders, monitoring, backups, and AI workflows powered by LangChain and LangGraph.

The project is deployed on a real Ubuntu VPS using Docker, Nginx, HTTPS, GitHub Actions CI/CD, GitHub Container Registry, PostgreSQL, and Uptime Kuma.

---

## Features

### Public website

- Home page
- Services page
- Booking page
- Contact page
- Public system status page
- Installable PWA
- RTL layout support
- Real-time appointment availability
- Customer name, phone, notes, service, date and time
- Booking confirmation

### Owner dashboard

- Secure owner login
- Today's bookings
- Booking management
- Customer management
- Service and price management
- Internal notes
- Booking rescheduling
- Booking status changes:
  - Pending
  - Confirmed
  - Done
  - Cancelled
  - No Show
- Cancellation reason tracking
- Statistics dashboard
- Booking-per-day line graph
- Expected and completed income
- Most requested services
- Customer statistics

### AI Agent

BookOps uses both LangChain and LangGraph.

Production versions currently include:

- LangChain 1.x
- LangGraph 1.x

The booking-analysis graph performs:

```text
Booking
   ↓
Assess priority
   ↓
Detect conflicts
   ↓
Recommend upsell
   ↓
Compose confirmation
   ↓
Persist analysis
