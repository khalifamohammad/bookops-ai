from datetime import date, datetime, time
from typing import Any
from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models import BookingStatus
from app.schemas.customer import CustomerOut
from app.schemas.service import ServiceOut


class PublicBookingCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=255)
    customer_phone: str = Field(min_length=6, max_length=50)
    customer_email: EmailStr | None = None
    service_id: int
    booking_date: date
    start_time: time
    customer_notes: str | None = Field(default=None, max_length=2000)
    website: str | None = Field(default=None, max_length=200)  # spam honeypot


class BookingUpdate(BaseModel):
    service_id: int | None = None
    booking_date: date | None = None
    start_time: time | None = None
    customer_notes: str | None = None
    cancellation_reason: str | None = None


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    cancellation_reason: str | None = None

    @model_validator(mode="after")
    def require_reason_for_cancel(self):
        if self.status == BookingStatus.CANCELLED and not self.cancellation_reason:
            raise ValueError("A cancellation reason is required")
        return self


class BookingNoteCreate(BaseModel):
    note: str = Field(min_length=1, max_length=3000)


class BookingNoteOut(BaseModel):
    id: int
    note: str
    created_at: datetime
    model_config = {"from_attributes": True}


class BookingOut(BaseModel):
    id: int
    customer_id: int
    service_id: int
    booking_date: date
    start_time: time
    end_time: time
    status: BookingStatus
    customer_notes: str | None
    cancellation_reason: str | None
    expected_income: float
    ai_analysis: dict[str, Any] | None
    reminder_sent_at: datetime | None
    customer: CustomerOut
    service: ServiceOut
    notes: list[BookingNoteOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class AvailabilityOut(BaseModel):
    date: date
    service_id: int
    slots: list[time]
