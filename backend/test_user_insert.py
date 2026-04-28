from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()

try:
    user = User(
        email="test@example.com",
        name="Test User",
        google_sub="google-test-123"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    print("✅ User inserted")
    print("ID:", user.id)
    print("Email:", user.email)

except Exception as e:
    db.rollback()
    print("❌ Error:", e)

finally:
    db.close()