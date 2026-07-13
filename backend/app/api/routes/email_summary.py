from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.services.ai_summary_service import generate_email_summary

router = APIRouter(
    prefix="/email-summary",
    tags=["Email Summary"]
)


@router.post("/{email_id}")
def summarize_email(email_id: UUID):
    db: Session = SessionLocal()

    try:
        email = db.query(EmailMessage).filter(
            EmailMessage.id == email_id
        ).first()

        if not email:
            raise HTTPException(
                status_code=404,
                detail="Email not found"
            )

        summary = generate_email_summary(
            subject=email.subject or "No subject",
            sender=email.sender_email or "Unknown sender",
            snippet=email.snippet or "",
        )

        return {
            "email_id": str(email.id),
            **summary,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()