from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.email_message import EmailMessage
from app.schemas.email_message import EmailMessageCreate, EmailMessageResponse

router = APIRouter(prefix="/emails", tags=["Emails"])


@router.post("/", response_model=EmailMessageResponse)
def create_email(data: EmailMessageCreate, db: Session = Depends(get_db)):
    email = EmailMessage(
        user_id=data.user_id,
        gmail_message_id=data.gmail_message_id,
        gmail_thread_id=data.gmail_thread_id,
        sender_email=data.sender_email,
        subject=data.subject,
        body_text=data.body_text
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return email


@router.get("/", response_model=list[EmailMessageResponse])
def get_emails(db: Session = Depends(get_db)):
    return db.query(EmailMessage).all()