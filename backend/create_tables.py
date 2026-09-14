from app.core.database import Base, engine

# Import every SQLAlchemy model so Base.metadata knows about all tables
from app.models.user import User
from app.models.gmail_account import GmailAccount
from app.models.email_message import EmailMessage
from app.models.classification_result import ClassificationResult
from app.models.notification import Notification


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ All database tables created successfully")


if __name__ == "__main__":
    create_tables()