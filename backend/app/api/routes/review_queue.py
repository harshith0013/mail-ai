from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.classification_result import ClassificationResult
from app.models.email_message import EmailMessage

router = APIRouter(prefix="/review-queue", tags=["Review Queue"])


@router.get("/")
def get_review_queue():
    db: Session = SessionLocal()

    try:
        results = (
            db.query(ClassificationResult, EmailMessage)
            .join(EmailMessage, ClassificationResult.email_message_id == EmailMessage.id)
            .filter(
                (ClassificationResult.category == "uncertain") |
                (ClassificationResult.confidence < 0.75)
            )
            .all()
        )

        review_items = []
        for classification, email in results:
            review_items.append({
                "classification_id": str(classification.id),
                "email_id": str(email.id),
                "subject": email.subject,
                "sender_email": email.sender_email,
                "category": classification.category,
                "confidence": classification.confidence,
                "suggested_action": classification.suggested_action,
                "reason": classification.reason,
                "created_at": classification.created_at,
            })

        return review_items

    finally:
        db.close()