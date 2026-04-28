from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import SessionLocal
from app.models.gmail_account import GmailAccount
from app.models.email_message import EmailMessage
from app.services.gmail_service import GmailService

router = APIRouter(prefix="/api/v1/gmail", tags=["Gmail Sync"])


def extract_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return None


from uuid import UUID

@router.get("/sync/{gmail_account_id}")
def sync_gmail_messages(gmail_account_id: UUID):
    db: Session = SessionLocal()

    try:
        gmail_account = db.query(GmailAccount).filter(
            GmailAccount.id == gmail_account_id
        ).first()

        if not gmail_account:
            raise HTTPException(status_code=404, detail="Gmail account not found")

        gmail_service = GmailService(
            access_token=gmail_account.access_token_encrypted,
            refresh_token=gmail_account.refresh_token_encrypted
        )

        messages = gmail_service.list_messages(max_results=10)
        saved_count = 0

        for msg in messages:
            full_msg = gmail_service.get_message(msg["id"])

            existing = db.query(EmailMessage).filter(
                EmailMessage.gmail_message_id == full_msg["id"]
            ).first()

            if existing:
                continue

            payload = full_msg.get("payload", {})
            headers = payload.get("headers", [])

            sender = extract_header(headers, "From")
            subject = extract_header(headers, "Subject")

            email_row = EmailMessage(
                user_id=gmail_account.user_id,
                gmail_message_id=full_msg["id"],
                gmail_thread_id=full_msg.get("threadId"),
                sender_email=sender,
                subject=subject,
                snippet=full_msg.get("snippet"),
                received_at=datetime.utcnow(),
                raw_labels=str(full_msg.get("labelIds", [])),
                is_read="UNREAD" not in full_msg.get("labelIds", []),
                is_archived="INBOX" not in full_msg.get("labelIds", []),
            )

            db.add(email_row)
            saved_count += 1

        db.commit()

        return {
            "message": "Gmail sync completed",
            "saved_count": saved_count,
            "fetched_count": len(messages),
        }

    finally:
        db.close()