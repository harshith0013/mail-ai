from app.core.database import SessionLocal
from app.models.user import User
from app.models.email_message import EmailMessage
from datetime import datetime

db = SessionLocal()

try:
    user = db.query(User).first()

    if not user:
        print("❌ No user found. Create a user first.")
    else:
        email_message = EmailMessage(
            user_id=user.id,
            gmail_message_id="gmail-msg-001",
            gmail_thread_id="gmail-thread-001",
            sender_name="Recruiter",
            sender_email="recruiter@example.com",
            subject="Interview Invitation",
            snippet="We would like to invite you for an interview.",
            body_text="Hello Sai, we would like to schedule an interview with you.",
            body_html="<p>Hello Sai, we would like to schedule an interview with you.</p>",
            received_at=datetime.utcnow(),
            is_read=False,
            is_archived=False,
            has_attachments=False,
            raw_labels='["INBOX", "IMPORTANT"]'
        )
        db.add(email_message)
        db.commit()
        db.refresh(email_message)

        print("✅ Email message inserted")
        print("ID:", email_message.id)
        print("Subject:", email_message.subject)

except Exception as e:
    db.rollback()
    print("❌ Error:", e)

finally:
    db.close()