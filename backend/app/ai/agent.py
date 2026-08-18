from __future__ import annotations

from collections import Counter
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AISummary, Booking, BookingStatus
from app.services.booking_logic import find_conflict


URGENT_TERMS = {
    "urgent",
    "asap",
    "event",
    "wedding",
    "today",
    "emergency",
    "important",
}

UPSELLS = {
    "haircut": "Add a wash and styling finish",
    "dye": "Post-color hair care treatment",
    "facial": "Hydrating mask upgrade",
    "massage": "Aromatherapy add-on",
    "consultation": "Book a follow-up appointment",
}


def analyze_booking(db: Session, booking: Booking) -> dict:
    notes = (booking.customer_notes or "").lower()

    priority = (
        "high"
        if any(term in notes for term in URGENT_TERMS)
        else "normal"
    )

    conflict = find_conflict(
        db,
        booking.booking_date,
        booking.start_time,
        booking.end_time,
        booking.id,
    )

    service_name = booking.service.name.lower()

    upsell = next(
        (
            idea
            for keyword, idea in UPSELLS.items()
            if keyword in service_name
        ),
        None,
    )

    reply = (
        f"Booking received for {booking.service.name} "
        f"on {booking.booking_date.isoformat()} "
        f"at {booking.start_time.strftime('%H:%M')}. "
        f"Please arrive 10 minutes early."
    )

    if conflict:
        reply = (
            "The requested time conflicts with another appointment. "
            "Please choose another available slot."
        )

    result = {
        "priority": priority,
        "estimated_duration_minutes": booking.service.duration_minutes,
        "has_conflict": bool(conflict),
        "conflict_details": (
            f"Conflicts with booking #{conflict.id}"
            if conflict
            else None
        ),
        "confirmation_reply": reply,
        "upsell_suggestion": upsell,
    }

    booking.ai_analysis = result

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return result


def generate_daily_summary(
    db: Session,
    summary_date: date,
) -> AISummary:

    bookings = list(
        db.scalars(
            select(Booking).where(
                Booking.booking_date == summary_date
            )
        ).all()
    )

    status_counts = Counter(
        booking.status.value
        for booking in bookings
    )

    service_counts = Counter(
        booking.service.name
        for booking in bookings
    )

    completed_income = sum(
        b.expected_income
        for b in bookings
        if b.status == BookingStatus.DONE
    )

    expected_income = sum(
        b.expected_income
        for b in bookings
        if b.status
        not in {
            BookingStatus.CANCELLED,
            BookingStatus.NO_SHOW,
        }
    )

    top_service = (
        service_counts.most_common(1)[0][0]
        if service_counts
        else "None"
    )

    cancellation_reasons = [
        b.cancellation_reason
        for b in bookings
        if (
            b.status == BookingStatus.CANCELLED
            and b.cancellation_reason
        )
    ]

    cancellation_text = ""

    if cancellation_reasons:
        cancellation_text = (
            " Cancellation reasons: "
            + "; ".join(cancellation_reasons)
            + "."
        )

    content = (
        f"{summary_date.isoformat()} summary: "
        f"{len(bookings)} bookings; "
        f"{status_counts.get('DONE', 0)} completed, "
        f"{status_counts.get('CANCELLED', 0)} cancelled, "
        f"{status_counts.get('NO_SHOW', 0)} no-shows. "
        f"The most requested service was {top_service}. "
        f"Expected income: {expected_income:.2f}; "
        f"completed income: {completed_income:.2f}."
        f"{cancellation_text}"
    )

    recommendations: list[str] = []

    if status_counts.get("CANCELLED", 0):
        recommendations.append(
            "Review cancellation reasons and contact "
            "repeat cancellers before future appointments."
        )

    if status_counts.get("NO_SHOW", 0):
        recommendations.append(
            "Send an additional confirmation reminder "
            "to reduce no-shows."
        )

    if bookings and max(
        service_counts.values(),
        default=0,
    ) >= 2:
        recommendations.append(
            f"Promote {top_service}; it is currently "
            "the most requested service."
        )

    if not bookings:
        recommendations.append(
            "Run a promotion or contact existing customers "
            "to fill open appointment slots."
        )

    if not recommendations:
        recommendations.append(
            "Operations look stable; keep the current "
            "reminder and confirmation process."
        )

    existing = db.scalar(
        select(AISummary).where(
            AISummary.summary_date == summary_date,
            AISummary.summary_type == "DAILY",
        )
    )

    if existing:
        existing.content = content
        existing.recommendations = recommendations
        summary = existing
    else:
        summary = AISummary(
            summary_date=summary_date,
            summary_type="DAILY",
            content=content,
            recommendations=recommendations,
            model_name="BookOps Rule Agent",
        )

        db.add(summary)

    db.commit()
    db.refresh(summary)

    return summary
