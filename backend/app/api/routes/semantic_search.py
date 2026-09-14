from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.services.semantic_search_service import (
    index_email,
    search_emails,
)


router = APIRouter(
    prefix="/semantic-search",
    tags=["Semantic Search"],
)


class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10


@router.post("/reindex")
def reindex_emails():
    """
    Rebuild semantic-search embeddings for all emails
    currently stored in PostgreSQL.
    """

    db: Session = SessionLocal()

    try:
        emails = db.query(EmailMessage).all()

        indexed_count = 0
        failed_count = 0
        failures = []

        for email in emails:
            try:
                index_email(
                    email_id=str(email.id),
                    subject=email.subject or "",
                    sender=email.sender_email or "",
                    snippet=email.snippet or "",
                )

                indexed_count += 1

            except Exception as exc:
                failed_count += 1

                failures.append(
                    {
                        "email_id": str(email.id),
                        "error": str(exc),
                    }
                )

        return {
            "message": "Semantic search indexing completed",
            "total_emails": len(emails),
            "indexed_count": indexed_count,
            "failed_count": failed_count,
            "failures": failures,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:
        db.close()


@router.post("/")
def semantic_search(data: SemanticSearchRequest):
    db: Session = SessionLocal()

    try:
        if not data.query or not data.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty",
            )

        if data.limit < 1:
            raise HTTPException(
                status_code=400,
                detail="Limit must be at least 1",
            )

        if data.limit > 50:
            raise HTTPException(
                status_code=400,
                detail="Limit cannot exceed 50",
            )

        results = search_emails(
            data.query.strip(),
            data.limit,
        )

        ids = results.get("ids", [[]])[0]
        scores = results.get("scores", [[]])[0]

        if not ids:
            return []

        valid_uuid_ids = []

        for email_id in ids:
            try:
                valid_uuid_ids.append(UUID(email_id))
            except ValueError:
                continue

        if not valid_uuid_ids:
            return []

        emails = (
            db.query(EmailMessage)
            .filter(EmailMessage.id.in_(valid_uuid_ids))
            .all()
        )

        email_map = {
            str(email.id): email
            for email in emails
        }

        score_map = {}

        for index, email_id in enumerate(ids):
            if index < len(scores):
                score_map[email_id] = scores[index]

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
                        "semantic_score": score_map.get(
                            email_id,
                            0.0,
                        ),
                    }
                )

        return ordered_results

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    finally:
        db.close()