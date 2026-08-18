from datetime import datetime
from pydantic import BaseModel, Field


class ServiceBase(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = None
    duration_minutes: int = Field(ge=10, le=600)
    price: float = Field(ge=0)
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = None
    duration_minutes: int | None = Field(default=None, ge=10, le=600)
    price: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ServiceOut(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
