# BookOps AI Architecture

## Overview

BookOps AI is a full-stack booking and business-management platform built for a salon, clinic, or small business.

The production system consists of:

- React/Vite frontend
- FastAPI backend
- PostgreSQL database
- LangChain + LangGraph AI workflows
- Background worker
- Telegram notifications
- Docker Compose
- Nginx reverse proxy
- HTTPS
- Uptime Kuma monitoring
- GitHub Actions CI/CD
- GitHub Container Registry
- Ubuntu VPS

---

# High-Level Architecture

```text
Customer / Owner Browser
          |
          | HTTPS
          v
        Nginx
          |
          v
  React Frontend
  127.0.0.1:8080
          |
          | /api
          v
      FastAPI
  127.0.0.1:8000
          |
          +-------------------+
          |                   |
          v                   v
      PostgreSQL         LangGraph
                         LangChain
          |                   |
          |                   v
          |             Booking Analysis
          |             Daily Summaries
          |
          v
 Background Worker
 Reminders / Summaries
          |
          v
      Telegram
