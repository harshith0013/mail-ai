from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.models.gmail_account import GmailAccount

from app.services.gmail_service import GmailService

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.models.classification_result import ClassificationResult


router = APIRouter(prefix="/api/v1/review", tags=["Review"])


class ReviewActionRequest(BaseModel):
    action: str


@router.post("/{email_id}")
def review_email(email_id: str, data: ReviewActionRequest):
    db: Session = SessionLocal()

    try:
        email = db.query(EmailMessage).filter(EmailMessage.id == email_id).first()

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        classification = (
            db.query(ClassificationResult)
            .filter(ClassificationResult.email_message_id == email.id)
            .order_by(ClassificationResult.created_at.desc())
            .first()
        )

        if not classification:
            raise HTTPException(status_code=404, detail="Classification not found")

        if data.action == "archive":
            email.is_archived = True
            classification.suggested_action = "archive"
            classification.category = "archive_reference"
            gmail_account = db.query(GmailAccount).filter(
                GmailAccount.user_id == email.user_id
            ).first()

            if gmail_account:
                gmail_service = GmailService(
                    access_token=gmail_account.access_token_encrypted,
                    refresh_token=gmail_account.refresh_token_encrypted,
                )
                gmail_service.archive_message(email.gmail_message_id)

        elif data.action == "keep":
            email.is_archived = False
            classification.suggested_action = "keep_inbox"
            classification.category = "important"

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        db.commit()

        return {
            "message": "Review decision saved",
            "email_id": str(email.id),
            "action": data.action,
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()