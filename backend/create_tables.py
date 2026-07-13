from app.core.database import Base, engine
from app.models import User, GmailAccount, EmailMessage

Base.metadata.create_all(bind=engine)

print("✅ Tables created successfully")