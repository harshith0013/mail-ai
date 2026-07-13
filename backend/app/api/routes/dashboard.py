from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.models.classification_result import ClassificationResult
from app.models.notification import Notification

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_dashboard_summary():
    db: Session = SessionLocal()

    try:
        total_emails = db.query(func.count(EmailMessage.id)).scalar() or 0
        total_classifications = db.query(func.count(ClassificationResult.id)).scalar() or 0
        total_notifications = db.query(func.count(Notification.id)).scalar() or 0

        archived_emails = (
            db.query(func.count(EmailMessage.id))
            .filter(EmailMessage.is_archived == True)
            .scalar()
            or 0
        )

        important_count = (
            db.query(func.count(ClassificationResult.id))
            .filter(ClassificationResult.category == "important")
            .scalar()
            or 0
        )

        uncertain_count = (
            db.query(func.count(ClassificationResult.id))
            .filter(ClassificationResult.category == "uncertain")
            .scalar()
            or 0
        )

        review_count = (
            db.query(func.count(ClassificationResult.id))
            .filter(
                (ClassificationResult.category == "uncertain")
                | (ClassificationResult.confidence < 0.75)
            )
            .scalar()
            or 0
        )

        unread_notifications = (
            db.query(func.count(Notification.id))
            .filter(Notification.status == "unread")
            .scalar()
            or 0
        )

        return {
            "total_emails": total_emails,
            "total_classifications": total_classifications,
            "total_notifications": total_notifications,
            "archived_emails": archived_emails,
            "important_count": important_count,
            "uncertain_count": uncertain_count,
            "review_count": review_count,
            "unread_notifications": unread_notifications,
        }

    finally:
        db.close()


@router.get("/category-distribution")
def get_category_distribution():
    db: Session = SessionLocal()

    try:
        rows = (
            db.query(
                ClassificationResult.category,
                func.count(ClassificationResult.id),
            )
            .group_by(ClassificationResult.category)
            .all()
        )

        return [
            {
                "category": category,
                "count": count,
            }
            for category, count in rows
        ]

    finally:
        db.close()