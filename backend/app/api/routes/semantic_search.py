from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.services.semantic_search_service import search_emails

router = APIRouter(
    prefix="/semantic-search",
    tags=["Semantic Search"]
)


class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10


@router.post("/")
def semantic_search(data: SemanticSearchRequest):
    db: Session = SessionLocal()

    try:
        results = search_emails(data.query, data.limit)

        ids = results.get("ids", [[]])[0]

        emails = (
            db.query(EmailMessage)
            .filter(EmailMessage.id.in_(ids))
            .all()
        )

        email_map = {str(email.id): email for email in emails}

        ordered_results = []

        for email_id in ids:
            email = email_map.get(email_id)

            if email:
                ordered_results.append(
                    {
                        "id": str(email.id),
                        "subject": email.subject,
                        "sender_email": email.sender_email,
                        "snippet": email.snippet,
                        "created_at": email.created_at,
                        "is_read": email.is_read,
                        "is_archived": email.is_archived,
                    }
                )

        return ordered_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()