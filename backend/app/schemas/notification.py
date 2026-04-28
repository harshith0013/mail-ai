from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    email_message_id: UUID
    type: str
    title: str
    message: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True