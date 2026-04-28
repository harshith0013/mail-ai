from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.gmail_account import GmailAccount
from app.schemas.gmail_account import GmailAccountCreate, GmailAccountResponse

router = APIRouter(prefix="/gmail-accounts", tags=["Gmail Accounts"])


@router.post("/", response_model=GmailAccountResponse)
def create_gmail_account(data: GmailAccountCreate, db: Session = Depends(get_db)):
    account = GmailAccount(
        user_id=data.user_id,
        gmail_email=data.gmail_email
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/", response_model=list[GmailAccountResponse])
def get_accounts(db: Session = Depends(get_db)):
    return db.query(GmailAccount).all()