from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import BusinessSettings, Service, User

settings = get_settings()

DEFAULT_SERVICES = [
    {"name": "Classic Haircut", "description": "Consultation, cut and finish", "duration_minutes": 45, "price": 120},
    {"name": "Haircut + Dye", "description": "Cut, color and styling", "duration_minutes": 90, "price": 280},
    {"name": "Facial Treatment", "description": "Cleanse, exfoliate and hydrate", "duration_minutes": 60, "price": 180},
]


def seed() -> None:
    with SessionLocal() as db:
        if not db.scalar(select(User).where(User.email == settings.admin_email.lower())):
            db.add(User(
                email=settings.admin_email.lower(),
                password_hash=hash_password(settings.admin_password),
                full_name="Business Owner",
                role="OWNER",
            ))
        if not db.scalar(select(BusinessSettings).limit(1)):
            db.add(BusinessSettings(
                business_name=settings.business_name,
                timezone=settings.business_timezone,
                reminder_minutes=settings.reminder_minutes,
            ))
        for payload in DEFAULT_SERVICES:
            if not db.scalar(select(Service).where(Service.name == payload["name"])):
                db.add(Service(**payload))
        db.commit()
