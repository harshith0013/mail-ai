from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class EmailMessageCreate(BaseModel):
    user_id: UUID
    gmail_message_id: str
    gmail_thread_id: str
    sender_email: Optional[str] = None
    subject: Optional[str] = None
    body_text: Optional[str] = None

class EmailMessageResponse(BaseModel):
    id: UUID
    user_id: UUID
    subject: Optional[str]
    sender_email: Optional[str]
    snippet: Optional[str] = None
    is_read: bool
    is_archived: bool
    created_at: datetime

    class Config:
        from_attributes = True