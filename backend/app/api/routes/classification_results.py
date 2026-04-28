from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.classification_result import ClassificationResult
from app.schemas.classification_result import ClassificationResultResponse

router = APIRouter(prefix="/classification-results", tags=["Classification Results"])


@router.get("/", response_model=list[ClassificationResultResponse])
def get_classification_results():
    db: Session = SessionLocal()
    try:
        return db.query(ClassificationResult).all()
    finally:
        db.close()