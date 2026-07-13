from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.services.ai_reply_service import generate_ai_reply

router = APIRouter(
    prefix="/email-reply",
    tags=["AI Reply"]
)


@router.post("/{email_id}")
def generate_email_reply(email_id: UUID):
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

        reply = generate_ai_reply(
            subject=email.subject or "No Subject",
            sender=email.sender_email or "Unknown Sender",
            snippet=email.snippet or "",
        )

        return {
            "email_id": str(email.id),
            "reply": reply,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()