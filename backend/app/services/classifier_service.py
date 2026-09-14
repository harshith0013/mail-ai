import logging
from typing import List, Literal, Optional

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import GEMINI_API_KEY


logger = logging.getLogger(__name__)


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

    importance: Literal[
        "high",
        "medium",
        "low",
    ]

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


def mock_classify_email(email_row):
    subject = (email_row.subject or "").lower()
    body = (email_row.body_text or "").lower()
    snippet = (email_row.snippet or "").lower()

    text = f"{subject} {snippet} {body}"

    if "interview" in text or "invitation" in text:
        return {
            "category": "important",
            "importance": "high",
            "suggested_action": "notify_user",
            "confidence": 0.92,
            "needs_confirmation": True,
            "deadline_at": None,
            "reason": "This looks like an interview-related email that needs attention.",
            "entities": {
                "sender_type": "human",
                "topics": ["job", "interview"],
                "contains_financial_info": False,
                "contains_calendar_request": True,
            },
        }

    if (
        "invoice" in text
        or "payment" in text
        or "receipt" in text
    ):
        return {
            "category": "finance",
            "importance": "medium",
            "suggested_action": "label_only",
            "confidence": 0.88,
            "needs_confirmation": False,
            "deadline_at": None,
            "reason": "This looks like a finance-related email.",
            "entities": {
                "sender_type": "automated",
                "topics": ["finance"],
                "contains_financial_info": True,
                "contains_calendar_request": False,
            },
        }

    if (
        "netflix" in text
        or "offer" in text
        or "sale" in text
        or "discount" in text
        or "free trial" in text
        or "subscribe" in text
    ):
        return {
            "category": "promotions",
            "importance": "low",
            "suggested_action": "archive",
            "confidence": 0.90,
            "needs_confirmation": False,
            "deadline_at": None,
            "reason": "This appears to be a promotional or marketing email.",
            "entities": {
                "sender_type": "automated",
                "topics": ["promotion", "marketing"],
                "contains_financial_info": False,
                "contains_calendar_request": False,
            },
        }

    return {
        "category": "uncertain",
        "importance": "low",
        "suggested_action": "hold_for_review",
        "confidence": 0.6,
        "needs_confirmation": False,
        "deadline_at": None,
        "reason": "Could not confidently classify the email.",
        "entities": {
            "sender_type": "unknown",
            "topics": [],
            "contains_financial_info": False,
            "contains_calendar_request": False,
        },
    }


def classify_email(email_row):
    if not GEMINI_API_KEY:
        logger.warning(
            "GEMINI_API_KEY is missing. Using fallback classifier."
        )
        return mock_classify_email(email_row)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""
You are an intelligent email triage classifier.

Analyze the email and classify it accurately.

Rules:

1. Promotions
Marketing emails, sales, subscriptions, streaming offers,
discounts, free trials, advertisements, or commercial offers.

2. Newsletter
Recurring informational content or news updates.

3. Important
Security alerts, interviews, urgent requests, approvals,
deadlines, account warnings, or time-sensitive messages.

4. Finance
Invoices, receipts, payments, bills, transactions,
financial notices, or payment confirmations.

5. Personal
Normal communication from individuals.

6. Work
Professional communication, tasks, meetings,
projects, assignments, requests, or business-related messages.

7. Needs Confirmation
Emails requiring explicit user approval or confirmation.

8. Archive Reference
Useful informational emails that do not need immediate attention.

9. Low Priority
Legitimate messages that are neither urgent nor important.

10. Spam Like
Suspicious, deceptive, or unsolicited messages.

11. Uncertain
Only use this when the email genuinely cannot be classified.

Suggested action rules:

- Important/time-sensitive:
  notify_user

- Promotional/low-priority:
  archive

- Useful informational:
  label_only

- Requires human decision:
  hold_for_review

- Normal important inbox message:
  keep_inbox

Confidence must be between 0 and 1.

deadline_at:
Return an ISO-8601 datetime only if an explicit deadline exists.
Otherwise return null.

Email:

Sender:
{email_row.sender_email or "Unknown"}

Subject:
{email_row.subject or "No subject"}

Snippet:
{email_row.snippet or ""}

Body:
{email_row.body_text or ""}
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ClassificationOutput,
            ),
        )

        if not response.text:
            raise ValueError(
                "Gemini returned an empty classification response."
            )

        parsed = ClassificationOutput.model_validate_json(
            response.text
        )

        result = parsed.model_dump()

        logger.info(
            "Gemini classification successful for email %s",
            email_row.id,
        )

        print("GEMINI CLASSIFICATION RESULT:")
        print(result)

        return result

    except Exception as exc:
        logger.exception(
            "Gemini classification failed for email %s: %s",
            email_row.id,
            exc,
        )

        print("GEMINI CLASSIFICATION FAILED:")
        print(type(exc).__name__)
        print(str(exc))

        return mock_classify_email(email_row)