from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class GmailAccountCreate(BaseModel):
    user_id: UUID
    gmail_email: str


class GmailAccountResponse(BaseModel):
    id: UUID
    user_id: UUID
    gmail_email: str
    created_at: datetime

    class Config:
        from_attributes = True