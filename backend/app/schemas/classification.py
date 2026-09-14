from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ClassificationEntities(BaseModel):
    sender_type: Literal["human", "automated", "unknown"]
    topics: List[str]
    contains_financial_info: bool
    contains_calendar_request: bool


class ClassificationOutput(BaseModel):
    category: Literal[
        "important",
        "needs_confirmation",
        "work",
        "finance",
        "personal",
        "promotions",
        "newsletter",
        "low_priority",
        "spam_like",
        "archive_reference",
        "uncertain",
    ]

    importance: Literal["high", "medium", "low"]

    suggested_action: Literal[
        "keep_inbox",
        "label_only",
        "archive",
        "notify_user",
        "hold_for_review",
        "ignore",
    ]

    confidence: float = Field(ge=0.0, le=1.0)

    needs_confirmation: bool

    deadline_at: Optional[str] = None

    reason: str

    entities: ClassificationEntities