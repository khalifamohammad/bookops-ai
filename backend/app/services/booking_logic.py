from __future__ import annotations

from datetime import date, datetime, time, timedelta
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models import Booking, BookingStatus, BusinessSettings, Service

ACTIVE_STATUSES = [BookingStatus.PENDING, BookingStatus.CONFIRMED]


def combine(day: date, value: time) -> datetime:
    return datetime.combine(day, value)


def end_time_for(day: date, start: time, duration_minutes: int) -> time:
    return (combine(day, start) + timedelta(minutes=duration_minutes)).time().replace(second=0, microsecond=0)


def find_conflict(
    db: Session,
    booking_date: date,
    start_time: time,
    end_time: time,
    exclude_booking_id: int | None = None,
) -> Booking | None:
    stmt = select(Booking).where(
        Booking.booking_date == booking_date,
        Booking.status.in_(ACTIVE_STATUSES),
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )
    if exclude_booking_id is not None:
        stmt = stmt.where(Booking.id != exclude_booking_id)
    return db.scalar(stmt.limit(1))


def available_slots(db: Session, service: Service, day: date) -> list[time]:
    settings = db.scalar(select(BusinessSettings).limit(1))
    opening = settings.opening_hour if settings else time(9, 0)
    closing = settings.closing_hour if settings else time(18, 0)
    interval = settings.booking_interval_minutes if settings else 30

    cursor = combine(day, opening)
    end_of_day = combine(day, closing)
    slots: list[time] = []
    while cursor + timedelta(minutes=service.duration_minutes) <= end_of_day:
        start = cursor.time().replace(second=0, microsecond=0)
        end = (cursor + timedelta(minutes=service.duration_minutes)).time().replace(second=0, microsecond=0)
        if not find_conflict(db, day, start, end):
            slots.append(start)
        cursor += timedelta(minutes=interval)
    return slots
