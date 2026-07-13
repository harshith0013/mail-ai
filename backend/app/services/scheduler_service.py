from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.gmail_account import GmailAccount
from app.api.routes.gmail_sync import sync_gmail_messages

scheduler = BackgroundScheduler()


def auto_sync_gmail_accounts():
    db: Session = SessionLocal()

    try:
        accounts = db.query(GmailAccount).all()

        for account in accounts:
            try:
                print(f"Auto syncing Gmail account: {account.gmail_email}")
                sync_gmail_messages(account.id)
            except Exception as e:
                print(f"Auto sync failed for {account.gmail_email}: {e}")

    finally:
        db.close()


def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            auto_sync_gmail_accounts,
            "interval",
            minutes=5,
            id="gmail_auto_sync",
            replace_existing=True,
        )

        scheduler.start()
        print("Background Gmail auto-sync scheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("Background scheduler stopped.")