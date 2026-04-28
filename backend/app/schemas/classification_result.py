from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class ClassificationResultResponse(BaseModel):
    id: UUID
    email_message_id: UUID
    category: str
    importance: str
    suggested_action: str
    confidence: float
    needs_confirmation: bool
    deadline_at: Optional[datetime] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True