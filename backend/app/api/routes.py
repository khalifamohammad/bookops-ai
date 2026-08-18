from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.ai.agent import analyze_booking, generate_daily_summary
from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token, verify_password
from app.core.rate_limit import enforce_rate_limit
from app.models import ActivityLog, AISummary, Booking, BookingNote, BookingStatus, Customer, Service, User
from app.schemas.ai import BookingAnalysisOut, DailySummaryOut
from app.schemas.auth import LoginRequest, TokenResponse, UserOut
from app.schemas.booking import (
    AvailabilityOut,
    BookingNoteCreate,
    BookingOut,
    BookingStatusUpdate,
    BookingUpdate,
    PublicBookingCreate,
)
from app.schemas.common import Message
from app.schemas.customer import CustomerOut, CustomerUpdate
from app.schemas.service import ServiceCreate, ServiceOut, ServiceUpdate
from app.schemas.stats import BookingTrendPoint, OverviewStats
from app.services.booking_logic import available_slots, end_time_for, find_conflict
from app.services.notifications import send_notification

settings = get_settings()
router = APIRouter()
Db = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def booking_query():
    return select(Booking).options(
        selectinload(Booking.customer),
        selectinload(Booking.service),
        selectinload(Booking.notes),
    )


@router.get("/health")
def health(db: Db):
    db.execute(select(1))
    return {"status": "ok", "database": "ok", "ai": "ok", "service": settings.app_name}


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Db):
    enforce_rate_limit(request, "login", limit=10, window_seconds=300)
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(str(user.id)))


@router.get("/auth/me", response_model=UserOut)
def me(user: CurrentUser):
    return user


@router.get("/services", response_model=list[ServiceOut])
def public_services(db: Db):
    return list(db.scalars(select(Service).where(Service.is_active.is_(True)).order_by(Service.name)).all())


@router.get("/services/manage", response_model=list[ServiceOut])
def managed_services(db: Db, user: CurrentUser):
    return list(db.scalars(select(Service).order_by(Service.name)).all())


@router.post("/services", response_model=ServiceOut, status_code=201)
def create_service(payload: ServiceCreate, db: Db, user: CurrentUser):
    if db.scalar(select(Service).where(func.lower(Service.name) == payload.name.lower())):
        raise HTTPException(status_code=409, detail="Service name already exists")
    service = Service(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.put("/services/{service_id}", response_model=ServiceOut)
def update_service(service_id: int, payload: ServiceUpdate, db: Db, user: CurrentUser):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(service, key, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/services/{service_id}", response_model=Message)
def delete_service(service_id: int, db: Db, user: CurrentUser):
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.is_active = False
    db.commit()
    return Message(message="Service deactivated")


@router.get("/availability", response_model=AvailabilityOut)
def get_availability(service_id: int, day: date = Query(alias="date"), db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if not service or not service.is_active:
        raise HTTPException(status_code=404, detail="Service not found")
    if day < date.today():
        return AvailabilityOut(date=day, service_id=service_id, slots=[])
    return AvailabilityOut(date=day, service_id=service_id, slots=available_slots(db, service, day))


@router.post("/bookings/public", response_model=BookingOut, status_code=201)
def create_public_booking(payload: PublicBookingCreate, request: Request, db: Db):
    enforce_rate_limit(request, "public-booking", limit=20, window_seconds=3600)
    if payload.website:
        raise HTTPException(status_code=400, detail="Invalid booking submission")
    service = db.get(Service, payload.service_id)
    if not service or not service.is_active:
        raise HTTPException(status_code=404, detail="Service not found")
    if payload.booking_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot book in the past")
    end_time = end_time_for(payload.booking_date, payload.start_time, service.duration_minutes)
    if find_conflict(db, payload.booking_date, payload.start_time, end_time):
        raise HTTPException(status_code=409, detail="The selected time is no longer available")

    customer = db.scalar(select(Customer).where(Customer.phone == payload.customer_phone))
    if customer:
        customer.name = payload.customer_name
        customer.email = payload.customer_email or customer.email
    else:
        customer = Customer(name=payload.customer_name, phone=payload.customer_phone, email=payload.customer_email)
        db.add(customer)
        db.flush()

    booking = Booking(
        customer_id=customer.id,
        service_id=service.id,
        booking_date=payload.booking_date,
        start_time=payload.start_time,
        end_time=end_time,
        customer_notes=payload.customer_notes,
        expected_income=service.price,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    db.commit()
    booking = db.scalar(booking_query().where(Booking.id == booking.id))
    send_notification(
        "New booking",
        f"{customer.name} booked {service.name} on {booking.booking_date} at {booking.start_time.strftime('%H:%M')}.",
    )
    return booking


@router.post("/webhooks/external-booking", response_model=BookingOut, status_code=201)
def external_booking_webhook(payload: PublicBookingCreate, request: Request, db: Db):
    # Simulates an external system such as WhatsApp or a partner booking channel.
    return create_public_booking(payload, request, db)


@router.get("/bookings", response_model=list[BookingOut])
def list_bookings(
    db: Db,
    user: CurrentUser,
    day: date | None = None,
    status_filter: BookingStatus | None = Query(default=None, alias="status"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
):
    stmt = booking_query().order_by(Booking.booking_date.desc(), Booking.start_time.desc())
    if day:
        stmt = stmt.where(Booking.booking_date == day)
    if status_filter:
        stmt = stmt.where(Booking.status == status_filter)
    if from_date:
        stmt = stmt.where(Booking.booking_date >= from_date)
    if to_date:
        stmt = stmt.where(Booking.booking_date <= to_date)
    return list(db.scalars(stmt).all())


@router.get("/bookings/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Db, user: CurrentUser):
    booking = db.scalar(booking_query().where(Booking.id == booking_id))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.put("/bookings/{booking_id}", response_model=BookingOut)
def update_booking(booking_id: int, payload: BookingUpdate, db: Db, user: CurrentUser):
    booking = db.scalar(booking_query().where(Booking.id == booking_id))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    service = db.get(Service, payload.service_id or booking.service_id)
    booking_date = payload.booking_date or booking.booking_date
    start_time = payload.start_time or booking.start_time
    end_time = end_time_for(booking_date, start_time, service.duration_minutes)
    if find_conflict(db, booking_date, start_time, end_time, booking.id):
        raise HTTPException(status_code=409, detail="The selected time conflicts with another booking")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key not in {"service_id", "booking_date", "start_time"}:
            setattr(booking, key, value)
    booking.service_id = service.id
    booking.service = service
    booking.booking_date = booking_date
    booking.start_time = start_time
    booking.end_time = end_time
    booking.expected_income = service.price
    db.add(ActivityLog(user_id=user.id, action="UPDATE", entity_type="BOOKING", entity_id=booking.id))
    db.commit()
    return db.scalar(booking_query().where(Booking.id == booking.id))


@router.patch("/bookings/{booking_id}/status", response_model=BookingOut)
def update_booking_status(booking_id: int, payload: BookingStatusUpdate, db: Db, user: CurrentUser):
    booking = db.scalar(booking_query().where(Booking.id == booking_id))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = payload.status
    booking.cancellation_reason = payload.cancellation_reason
    db.add(ActivityLog(
        user_id=user.id,
        action="STATUS_CHANGE",
        entity_type="BOOKING",
        entity_id=booking.id,
        details={"status": payload.status.value},
    ))
    db.commit()
    return db.scalar(booking_query().where(Booking.id == booking.id))


@router.post("/bookings/{booking_id}/notes", response_model=BookingOut)
def add_booking_note(booking_id: int, payload: BookingNoteCreate, db: Db, user: CurrentUser):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    db.add(BookingNote(booking_id=booking_id, user_id=user.id, note=payload.note))
    db.commit()
    return db.scalar(booking_query().where(Booking.id == booking_id))


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(db: Db, user: CurrentUser, q: str | None = None):
    stmt = select(Customer).order_by(Customer.created_at.desc())
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where((Customer.name.ilike(pattern)) | (Customer.phone.ilike(pattern)))
    return list(db.scalars(stmt).all())


@router.put("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: int, payload: CustomerUpdate, db: Db, user: CurrentUser):
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    db.commit()
    db.refresh(customer)
    return customer


@router.post("/ai/analyze-booking/{booking_id}", response_model=BookingAnalysisOut)
def analyze_booking_endpoint(booking_id: int, db: Db, user: CurrentUser):
    booking = db.scalar(booking_query().where(Booking.id == booking_id))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return analyze_booking(db, booking)


@router.post("/ai/daily-summary", response_model=DailySummaryOut)
def create_daily_summary(db: Db, user: CurrentUser, day: date | None = None):
    return generate_daily_summary(db, day or date.today())


@router.get("/ai/summaries", response_model=list[DailySummaryOut])
def list_summaries(db: Db, user: CurrentUser):
    return list(db.scalars(select(AISummary).order_by(AISummary.summary_date.desc()).limit(30)).all())


@router.get("/stats/overview", response_model=OverviewStats)
def stats_overview(db: Db, user: CurrentUser, from_date: date | None = None, to_date: date | None = None):
    from_date = from_date or (date.today() - timedelta(days=30))
    to_date = to_date or date.today()
    bookings = list(db.scalars(select(Booking).where(Booking.booking_date.between(from_date, to_date)).options(selectinload(Booking.service))).all())
    status_counts = {status: sum(1 for b in bookings if b.status == status) for status in BookingStatus}
    customer_count = db.scalar(select(func.count(Customer.id)).where(func.date(Customer.created_at).between(from_date, to_date))) or 0
    service_counts: dict[str, int] = {}
    for booking in bookings:
        service_counts[booking.service.name] = service_counts.get(booking.service.name, 0) + 1
    top_service = max(service_counts, key=service_counts.get) if service_counts else None
    return OverviewStats(
        total_bookings=len(bookings),
        pending=status_counts[BookingStatus.PENDING],
        confirmed=status_counts[BookingStatus.CONFIRMED],
        done=status_counts[BookingStatus.DONE],
        cancelled=status_counts[BookingStatus.CANCELLED],
        no_show=status_counts[BookingStatus.NO_SHOW],
        new_customers=customer_count,
        expected_income=sum(b.expected_income for b in bookings if b.status not in {BookingStatus.CANCELLED, BookingStatus.NO_SHOW}),
        completed_income=sum(b.expected_income for b in bookings if b.status == BookingStatus.DONE),
        most_requested_service=top_service,
    )


@router.get("/stats/bookings", response_model=list[BookingTrendPoint])
def booking_trend(db: Db, user: CurrentUser, days: int = Query(default=14, ge=1, le=365)):
    start = date.today() - timedelta(days=days - 1)
    rows = db.execute(
        select(Booking.booking_date, func.count(Booking.id)).where(Booking.booking_date >= start).group_by(Booking.booking_date)
    ).all()
    counts = {row[0]: row[1] for row in rows}
    return [BookingTrendPoint(date=start + timedelta(days=i), count=counts.get(start + timedelta(days=i), 0)) for i in range(days)]
