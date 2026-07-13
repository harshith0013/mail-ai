from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.core.database import SessionLocal
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=list[NotificationResponse])
def get_notifications():
    db: Session = SessionLocal()
    try:
        return db.query(Notification).order_by(Notification.created_at.desc()).all()
    finally:
        db.close()


@router.post("/{notification_id}/read")
def mark_notification_read(notification_id: UUID):
    db: Session = SessionLocal()
    try:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        notification.status = "read"
        notification.updated_at = datetime.utcnow()

        db.commit()

        return {
            "message": "Notification marked as read",
            "notification_id": str(notification.id),
        }

    finally:
        db.close()


@router.post("/{notification_id}/dismiss")
def dismiss_notification(notification_id: UUID):
    db: Session = SessionLocal()
    try:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        notification.status = "dismissed"
        notification.updated_at = datetime.utcnow()

        db.commit()

        return {
            "message": "Notification dismissed",
            "notification_id": str(notification.id),
        }

    finally:
        db.close()