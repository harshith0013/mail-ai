from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta

from app.core.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    FRONTEND_URL,
)
from app.core.database import SessionLocal
from app.models.user import User
from app.models.gmail_account import GmailAccount

router = APIRouter(prefix="/api/v1/auth/google", tags=["Google Auth"])

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


@router.get("/login")
def google_login():
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
    return RedirectResponse(url)


@router.get("/callback")
def google_callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"

    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get Google token")

    tokens = token_response.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")

    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if userinfo_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch Google user info")

    userinfo = userinfo_response.json()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == userinfo.get("email")).first()

        if not user:
            user = User(
                email=userinfo.get("email"),
                name=userinfo.get("name"),
                google_sub=userinfo.get("id"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        gmail_account = db.query(GmailAccount).filter(
            GmailAccount.gmail_email == userinfo.get("email")
        ).first()

        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        if not gmail_account:
            gmail_account = GmailAccount(
                user_id=user.id,
                gmail_email=userinfo.get("email"),
                access_token_encrypted=access_token,
                refresh_token_encrypted=refresh_token,
                token_expires_at=expires_at,
            )
            db.add(gmail_account)
        else:
            gmail_account.access_token_encrypted = access_token
            if refresh_token:
                gmail_account.refresh_token_encrypted = refresh_token
            gmail_account.token_expires_at = expires_at
            gmail_account.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(gmail_account)

        return RedirectResponse(
    url=f"{FRONTEND_URL.rstrip('/')}/settings?gmail_connected=true&gmail_account_id={gmail_account.id}"
)

    finally:
        db.close()
        