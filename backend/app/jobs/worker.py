from __future__ import annotations

import logging
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select

from app.ai.agent import generate_daily_summary
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models import Booking, BookingStatus
from app.services.notifications import send_notification

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bookops.worker")
settings = get_settings()


def run_once() -> None:
    now = datetime.now(ZoneInfo(settings.business_timezone))
    with SessionLocal() as db:
        upcoming_limit = now + timedelta(minutes=settings.reminder_minutes)
        bookings = db.scalars(
            select(Booking).where(
                Booking.booking_date == now.date(),
                Booking.status == BookingStatus.CONFIRMED,
                Booking.reminder_sent_at.is_(None),
            )
        ).all()
        for booking in bookings:
            start = datetime.combine(booking.booking_date, booking.start_time, tzinfo=now.tzinfo)
            if now <= start <= upcoming_limit:
                send_notification(
                    "Appointment reminder",
                    f"{booking.customer.name}: {booking.service.name} at {booking.start_time.strftime('%H:%M')}",
                )
                booking.reminder_sent_at = now
        db.commit()

        if now.hour == settings.daily_summary_hour:
            generate_daily_summary(db, now.date())


if __name__ == "__main__":
    logger.info("BookOps worker started")
    while True:
        try:
            run_once()
        except Exception:
            logger.exception("Worker iteration failed")
        time.sleep(60)
