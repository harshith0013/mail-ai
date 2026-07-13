from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.models.classification_result import ClassificationResult

router = APIRouter(
    prefix="/email-details",
    tags=["Email Details"]
)


@router.get("/{email_id}")
def get_email_details(email_id: UUID):
    db: Session = SessionLocal()

    try:
        email = (
            db.query(EmailMessage)
            .filter(EmailMessage.id == email_id)
            .first()
        )

        if not email:
            raise HTTPException(
                status_code=404,
                detail="Email not found"
            )

        classification = (
            db.query(ClassificationResult)
            .filter(ClassificationResult.email_message_id == email.id)
            .order_by(ClassificationResult.created_at.desc())
            .first()
        )

        return {
            "email_id": str(email.id),
            "subject": email.subject,
            "sender_email": email.sender_email,
            "snippet": email.snippet,
            "body_text": getattr(email, "body_text", None),
            "is_read": email.is_read,
            "is_archived": email.is_archived,

            "classification": classification.category if classification else None,
            "confidence": classification.confidence if classification else None,
            "suggested_action": classification.suggested_action if classification else None,
            "reason": classification.reason if classification else None,

            "summary": getattr(email, "summary", None),
            "priority": getattr(email, "priority", None),
            "needs_reply": getattr(email, "needs_reply", None),
            "action_items": getattr(email, "action_items", None),
        }

    finally:
        db.close()