from datetime import date, datetime
from pydantic import BaseModel


class BookingAnalysisOut(BaseModel):
    priority: str
    estimated_duration_minutes: int
    has_conflict: bool
    conflict_details: str | None
    confirmation_reply: str
    upsell_suggestion: str | None


class DailySummaryOut(BaseModel):
    id: int
    summary_date: date
    summary_type: str
    content: str
    recommendations: list[str] | None
    model_name: str
    created_at: datetime
    model_config = {"from_attributes": True}
