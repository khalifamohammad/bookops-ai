from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any, TypedDict

from langchain.tools import tool
from langgraph.graph import END, START, StateGraph
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


# ============================================================
# LangChain tools
# ============================================================

@tool
def recommend_upsell(service_name: str) -> str:
    """Return an appropriate upsell suggestion for a BookOps service.

    Returns an empty string when no matching suggestion exists.
    """
    service_name = service_name.lower()

    for keyword, suggestion in UPSELLS.items():
        if keyword in service_name:
            return suggestion

    return ""


# ============================================================
# Booking analysis LangGraph
# ============================================================

class BookingAnalysisState(TypedDict, total=False):
    db: Session
    booking: Booking

    priority: str
    conflict: Booking | None
    upsell_suggestion: str | None
    confirmation_reply: str

    result: dict[str, Any]


def assess_priority(state: BookingAnalysisState) -> dict:
    booking = state["booking"]

    notes = (booking.customer_notes or "").lower()

    priority = (
        "high"
        if any(term in notes for term in URGENT_TERMS)
        else "normal"
    )

    return {"priority": priority}


def detect_conflict(state: BookingAnalysisState) -> dict:
    booking = state["booking"]
    db = state["db"]

    conflict = find_conflict(
        db,
        booking.booking_date,
        booking.start_time,
        booking.end_time,
        booking.id,
    )

    return {"conflict": conflict}


def create_upsell(state: BookingAnalysisState) -> dict:
    booking = state["booking"]

    suggestion = recommend_upsell.invoke(
        {"service_name": booking.service.name}
    )

    return {
        "upsell_suggestion": suggestion or None
    }


def compose_confirmation(state: BookingAnalysisState) -> dict:
    booking = state["booking"]
    conflict = state.get("conflict")

    if conflict:
        reply = (
            "The requested time conflicts with another appointment. "
            "Please choose another available slot."
        )
    else:
        reply = (
            f"Booking received for {booking.service.name} "
            f"on {booking.booking_date.isoformat()} "
            f"at {booking.start_time.strftime('%H:%M')}. "
            "Please arrive 10 minutes early."
        )

    return {"confirmation_reply": reply}


def persist_booking_analysis(state: BookingAnalysisState) -> dict:
    db = state["db"]
    booking = state["booking"]
    conflict = state.get("conflict")

    result = {
        "priority": state["priority"],
        "estimated_duration_minutes": booking.service.duration_minutes,
        "has_conflict": bool(conflict),
        "conflict_details": (
            f"Conflicts with booking #{conflict.id}"
            if conflict
            else None
        ),
        "confirmation_reply": state["confirmation_reply"],
        "upsell_suggestion": state.get("upsell_suggestion"),
    }

    booking.ai_analysis = result

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return {"result": result}


booking_builder = StateGraph(BookingAnalysisState)

booking_builder.add_node("assess_priority", assess_priority)
booking_builder.add_node("detect_conflict", detect_conflict)
booking_builder.add_node("recommend_upsell", create_upsell)
booking_builder.add_node("compose_confirmation", compose_confirmation)
booking_builder.add_node(
    "persist_booking_analysis",
    persist_booking_analysis,
)

booking_builder.add_edge(START, "assess_priority")
booking_builder.add_edge("assess_priority", "detect_conflict")
booking_builder.add_edge("detect_conflict", "recommend_upsell")
booking_builder.add_edge("recommend_upsell", "compose_confirmation")
booking_builder.add_edge(
    "compose_confirmation",
    "persist_booking_analysis",
)
booking_builder.add_edge("persist_booking_analysis", END)

booking_analysis_graph = booking_builder.compile()


def analyze_booking(db: Session, booking: Booking) -> dict:
    state = booking_analysis_graph.invoke(
        {
            "db": db,
            "booking": booking,
        }
    )

    return state["result"]


# ============================================================
# Daily-summary LangGraph
# ============================================================

class DailySummaryState(TypedDict, total=False):
    db: Session
    summary_date: date

    bookings: list[Booking]
    status_counts: dict[str, int]
    service_counts: dict[str, int]
    cancellation_reasons: dict[str, int]

    completed_income: float
    expected_income: float
    top_service: str

    content: str
    recommendations: list[str]

    summary: AISummary


def collect_daily_metrics(state: DailySummaryState) -> dict:
    db = state["db"]
    summary_date = state["summary_date"]

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

    cancellation_reasons = Counter(
        (
            booking.cancellation_reason.strip()
            if booking.cancellation_reason
            else "No reason provided"
        )
        for booking in bookings
        if booking.status == BookingStatus.CANCELLED
    )

    completed_income = sum(
        booking.expected_income
        for booking in bookings
        if booking.status == BookingStatus.DONE
    )

    expected_income = sum(
        booking.expected_income
        for booking in bookings
        if booking.status not in {
            BookingStatus.CANCELLED,
            BookingStatus.NO_SHOW,
        }
    )

    top_service = (
        service_counts.most_common(1)[0][0]
        if service_counts
        else "None"
    )

    return {
        "bookings": bookings,
        "status_counts": dict(status_counts),
        "service_counts": dict(service_counts),
        "cancellation_reasons": dict(cancellation_reasons),
        "completed_income": completed_income,
        "expected_income": expected_income,
        "top_service": top_service,
    }


def compose_daily_summary(state: DailySummaryState) -> dict:
    summary_date = state["summary_date"]
    bookings = state["bookings"]
    status_counts = state["status_counts"]

    content = (
        f"{summary_date.isoformat()} summary: "
        f"{len(bookings)} bookings; "
        f"{status_counts.get('DONE', 0)} completed, "
        f"{status_counts.get('CANCELLED', 0)} cancelled, "
        f"{status_counts.get('NO_SHOW', 0)} no-shows. "
        f"The most requested service was {state['top_service']}. "
        f"Expected income: {state['expected_income']:.2f}; "
        f"completed income: {state['completed_income']:.2f}."
    )

    cancellation_reasons = state["cancellation_reasons"]

    if cancellation_reasons:
        reasons = ", ".join(
            f"{reason} ({count})"
            for reason, count in cancellation_reasons.items()
        )

        content += f" Cancellation reasons: {reasons}."

    return {"content": content}


def create_recommendations(state: DailySummaryState) -> dict:
    bookings = state["bookings"]
    status_counts = state["status_counts"]
    service_counts = state["service_counts"]
    top_service = state["top_service"]

    recommendations: list[str] = []

    if status_counts.get("CANCELLED", 0):
        recommendations.append(
            "Review cancellation reasons and contact repeat "
            "cancellers before future appointments."
        )

    if status_counts.get("NO_SHOW", 0):
        recommendations.append(
            "Send an additional confirmation reminder "
            "to reduce no-shows."
        )

    if bookings and max(service_counts.values(), default=0) >= 2:
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

    return {"recommendations": recommendations}


def persist_daily_summary(state: DailySummaryState) -> dict:
    db = state["db"]
    summary_date = state["summary_date"]

    existing = db.scalar(
        select(AISummary).where(
            AISummary.summary_date == summary_date,
            AISummary.summary_type == "DAILY",
        )
    )

    if existing:
        existing.content = state["content"]
        existing.recommendations = state["recommendations"]
        existing.model_name = "BookOps LangGraph Agent"

        summary = existing

    else:
        summary = AISummary(
            summary_date=summary_date,
            summary_type="DAILY",
            content=state["content"],
            recommendations=state["recommendations"],
            model_name="BookOps LangGraph Agent",
        )

        db.add(summary)

    db.commit()
    db.refresh(summary)

    return {"summary": summary}


summary_builder = StateGraph(DailySummaryState)

summary_builder.add_node(
    "collect_metrics",
    collect_daily_metrics,
)
summary_builder.add_node(
    "compose_summary",
    compose_daily_summary,
)
summary_builder.add_node(
    "create_recommendations",
    create_recommendations,
)
summary_builder.add_node(
    "persist_summary",
    persist_daily_summary,
)

summary_builder.add_edge(START, "collect_metrics")
summary_builder.add_edge("collect_metrics", "compose_summary")
summary_builder.add_edge(
    "compose_summary",
    "create_recommendations",
)
summary_builder.add_edge(
    "create_recommendations",
    "persist_summary",
)
summary_builder.add_edge("persist_summary", END)

daily_summary_graph = summary_builder.compile()


def generate_daily_summary(
    db: Session,
    summary_date: date,
) -> AISummary:
    state = daily_summary_graph.invoke(
        {
            "db": db,
            "summary_date": summary_date,
        }
    )

    return state["summary"]
