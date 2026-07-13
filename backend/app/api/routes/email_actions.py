from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage

router = APIRouter(
    prefix="/email-actions",
    tags=["Email Actions"]
)


@router.post("/{email_id}/archive")
def archive_email(email_id: UUID):
    db: Session = SessionLocal()

    try:
        email = (
            db.query(EmailMessage)
            .filter(EmailMessage.id == email_id)
            .first()
        )

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.is_archived = True
        db.commit()

        return {"message": "Email archived"}

    finally:
        db.close()


@router.post("/{email_id}/mark-read")
def mark_read(email_id: UUID):
    db: Session = SessionLocal()

    try:
        email = (
            db.query(EmailMessage)
            .filter(EmailMessage.id == email_id)
            .first()
        )

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.is_read = True
        db.commit()

        return {"message": "Email marked as read"}

    finally:
        db.close()


@router.post("/{email_id}/mark-unread")
def mark_unread(email_id: UUID):
    db: Session = SessionLocal()

    try:
        email = (
            db.query(EmailMessage)
            .filter(EmailMessage.id == email_id)
            .first()
        )

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        email.is_read = False
        db.commit()

        return {"message": "Email marked as unread"}

    finally:
        db.close()


@router.delete("/{email_id}")
def delete_email(email_id: UUID):
    db: Session = SessionLocal()

    try:
        email = (
            db.query(EmailMessage)
            .filter(EmailMessage.id == email_id)
            .first()
        )

        if not email:
            raise HTTPException(status_code=404, detail="Email not found")

        db.delete(email)
        db.commit()

        return {"message": "Email deleted"}

    finally:
        db.close()