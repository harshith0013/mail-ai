from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.models.classification_result import ClassificationResult
from app.services.classifier_service import classify_email
from app.services.rule_engine_service import decide_action
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/v1/classify", tags=["Classification"])


@router.post("/{email_id}")
def classify_one_email(email_id: str):
    db: Session = SessionLocal()

    try:
        email_row = db.query(EmailMessage).filter(EmailMessage.id == email_id).first()

        if not email_row:
            raise HTTPException(status_code=404, detail="Email not found")

        result = classify_email(email_row)

        deadline_value = result.get("deadline_at")
        deadline_dt = None
        if deadline_value:
            deadline_dt = datetime.fromisoformat(deadline_value.replace("Z", "+00:00"))

        classification = ClassificationResult(
            email_message_id=email_row.id,
            category=result["category"],
            importance=result["importance"],
            suggested_action=result["suggested_action"],
            confidence=result["confidence"],
            needs_confirmation=result["needs_confirmation"],
            deadline_at=deadline_dt,
            reason=result["reason"],
        )

        db.add(classification)
        db.commit()
        db.refresh(classification)

        final_action = decide_action(result)

        notification = None
        if final_action == "notify_user":
            notification = create_notification(
                db=db,
                user_id=email_row.user_id,
                email_message_id=email_row.id,
                notif_type="action_required",
                title=f"Attention needed: {email_row.subject or 'Untitled email'}",
                message=result["reason"],
            )

        if final_action == "archive":
            email_row.is_archived = True
            db.commit()

        return {
            "message": "Email classified successfully",
            "classification_id": str(classification.id),
            "final_action": final_action,
            "notification_id": str(notification.id) if notification else None,
            "result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()