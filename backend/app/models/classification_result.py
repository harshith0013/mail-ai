from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime


class ClassificationResult(Base):
    __tablename__ = "classification_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email_message_id = Column(UUID(as_uuid=True), ForeignKey("email_messages.id"), nullable=False)
    category = Column(String, nullable=False)
    importance = Column(String, nullable=False)
    suggested_action = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    needs_confirmation = Column(Boolean, default=False, nullable=False)
    deadline_at = Column(DateTime, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)