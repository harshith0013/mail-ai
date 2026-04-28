from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    google_sub: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str] = None
    google_sub: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True