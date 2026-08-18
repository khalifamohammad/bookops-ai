from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    phone: str = Field(min_length=6, max_length=50)
    email: EmailStr | None = None
    notes: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, min_length=6, max_length=50)
    email: EmailStr | None = None
    notes: str | None = None


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    email: EmailStr | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
