from app.core.database import SessionLocal
from app.models.user import User
from app.models.gmail_account import GmailAccount

db = SessionLocal()

try:
    user = db.query(User).first()

    if not user:
        print("❌ No user found. Create a user first.")
    else:
        gmail_account = GmailAccount(
            user_id=user.id,
            gmail_email="samplegmailaccount@gmail.com",
            access_token_encrypted="dummy_access_token",
            refresh_token_encrypted="dummy_refresh_token"
        )
        db.add(gmail_account)
        db.commit()
        db.refresh(gmail_account)

        print("✅ Gmail account inserted")
        print("ID:", gmail_account.id)
        print("User ID:", gmail_account.user_id)
        print("Gmail:", gmail_account.gmail_email)

except Exception as e:
    db.rollback()
    print("❌ Error:", e)

finally:
    db.close()