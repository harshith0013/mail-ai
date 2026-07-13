from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from app.services.semantic_search_service import index_email

from app.core.database import SessionLocal
from app.models.gmail_account import GmailAccount
from app.models.email_message import EmailMessage
from app.models.classification_result import ClassificationResult

from app.services.gmail_service import GmailService
from app.services.classifier_service import classify_email
from app.services.rule_engine_service import decide_action
from app.services.notification_service import create_notification


router = APIRouter(prefix="/api/v1/gmail", tags=["Gmail Sync"])


def extract_header(headers, name):
    for h in headers:
        if h["name"].lower() == name.lower():
            return h["value"]
    return None


@router.get("/sync/{gmail_account_id}")
def sync_gmail_messages(gmail_account_id: UUID):
    db: Session = SessionLocal()

    try:
        gmail_account = (
            db.query(GmailAccount)
            .filter(GmailAccount.id == gmail_account_id)
            .first()
        )

        if not gmail_account:
            raise HTTPException(status_code=404, detail="Gmail account not found")

        gmail_service = GmailService(
            access_token=gmail_account.access_token_encrypted,
            refresh_token=gmail_account.refresh_token_encrypted,
        )

        messages = gmail_service.list_messages(max_results=10)
        saved_count = 0
        classified_count = 0
        notification_count = 0
        archived_count = 0

        for msg in messages:
            full_msg = gmail_service.get_message(msg["id"])

            existing = (
                db.query(EmailMessage)
                .filter(EmailMessage.gmail_message_id == full_msg["id"])
                .first()
            )

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
            db.commit()
            db.refresh(email_row)

            saved_count += 1
            try:
                index_email(
                    email_id=str(email_row.id),
                    subject=email_row.subject or "",
                    sender=email_row.sender_email or "",
                    snippet=email_row.snippet or "",
                )
            except Exception as e:
                print("Semantic indexing failed:", e)

            try:
                result = classify_email(email_row)

                classification = ClassificationResult(
                    email_message_id=email_row.id,
                    category=result["category"],
                    importance=result["importance"],
                    suggested_action=result["suggested_action"],
                    confidence=result["confidence"],
                    needs_confirmation=result["needs_confirmation"],
                    reason=result["reason"],
                )

                db.add(classification)
                db.commit()
                db.refresh(classification)

                classified_count += 1

                final_action = decide_action(result)

                if final_action == "notify_user":
                    create_notification(
                        db=db,
                        user_id=email_row.user_id,
                        email_message_id=email_row.id,
                        notif_type="action_required",
                        title=f"Attention needed: {email_row.subject or 'Untitled email'}",
                        message=result["reason"],
                    )
                    notification_count += 1

                if final_action == "archive":
                    email_row.is_archived = True
                    db.commit()
                    archived_count += 1

            except Exception as e:
                print("Classification failed:", e)

        return {
            "message": "Gmail sync completed",
            "saved_count": saved_count,
            "classified_count": classified_count,
            "notification_count": notification_count,
            "archived_count": archived_count,
            "fetched_count": len(messages),
        }

    finally:
        db.close()