from datetime import date
from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_bookings: int
    pending: int
    confirmed: int
    done: int
    cancelled: int
    no_show: int
    new_customers: int
    expected_income: float
    completed_income: float
    most_requested_service: str | None


class BookingTrendPoint(BaseModel):
    date: date
    count: int
