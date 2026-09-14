from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.models.classification_result import ClassificationResult
from app.services.classifier_service import classify_email
from app.services.rule_engine_service import decide_action
from app.services.notification_service import create_notification


router = APIRouter(
    prefix="/api/v1/classify",
    tags=["Classification"],
)


@router.post("/{email_id}")
def classify_one_email(email_id: UUID):
    db: Session = SessionLocal()

    try:
        email_row = (
            db.query(EmailMessage)
            .filter(EmailMessage.id == email_id)
            .first()
        )

        if not email_row:
            raise HTTPException(
                status_code=404,
                detail="Email not found",
            )

        # Call AI classification service
        result = classify_email(email_row)

        # Parse deadline if AI returned one
        deadline_value = result.get("deadline_at")
        deadline_dt = None

        if deadline_value:
            try:
                deadline_dt = datetime.fromisoformat(
                    deadline_value.replace("Z", "+00:00")
                )
            except ValueError:
                deadline_dt = None

        # Save classification result
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

        # Apply rule engine
        final_action = decide_action(result)

        notification = None

        # Create notification if required
        if final_action == "notify_user":
            notification = create_notification(
                db=db,
                user_id=email_row.user_id,
                email_message_id=email_row.id,
                notif_type="action_required",
                title=f"Attention needed: {email_row.subject or 'Untitled email'}",
                message=result["reason"],
            )

        # Archive locally if rule engine says archive
        if final_action == "archive":
            email_row.is_archived = True
            db.commit()
            db.refresh(email_row)

        return {
            "message": "Email classified successfully",
            "email_id": str(email_row.id),
            "classification_id": str(classification.id),
            "final_action": final_action,
            "notification_id": (
                str(notification.id)
                if notification
                else None
            ),
            "result": result,
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        db.close()