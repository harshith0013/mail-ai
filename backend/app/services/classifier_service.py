import json
from openai import OpenAI

from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

CLASSIFICATION_SCHEMA = {
    "type": "json_schema",
    "name": "email_classification",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "category": {
                "type": "string",
                "enum": [
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
                    "uncertain"
                ]
            },
            "importance": {
                "type": "string",
                "enum": ["high", "medium", "low"]
            },
            "suggested_action": {
                "type": "string",
                "enum": [
                    "keep_inbox",
                    "label_only",
                    "archive",
                    "notify_user",
                    "hold_for_review",
                    "ignore"
                ]
            },
            "confidence": {
                "type": "number",
                "minimum": 0,
                "maximum": 1
            },
            "needs_confirmation": {"type": "boolean"},
            "deadline_at": {"type": ["string", "null"]},
            "reason": {"type": "string"},
            "entities": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "sender_type": {
                        "type": "string",
                        "enum": ["human", "automated", "unknown"]
                    },
                    "topics": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "contains_financial_info": {"type": "boolean"},
                    "contains_calendar_request": {"type": "boolean"}
                },
                "required": [
                    "sender_type",
                    "topics",
                    "contains_financial_info",
                    "contains_calendar_request"
                ]
            }
        },
        "required": [
            "category",
            "importance",
            "suggested_action",
            "confidence",
            "needs_confirmation",
            "deadline_at",
            "reason",
            "entities"
        ]
    }
}


def mock_classify_email(email_row):
    subject = (email_row.subject or "").lower()
    body = (email_row.body_text or "").lower()
    text = f"{subject} {body}"

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
                "contains_calendar_request": True
            }
        }

    if "invoice" in text or "payment" in text or "receipt" in text:
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
                "contains_calendar_request": False
            }
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
            "contains_calendar_request": False
        }
    }


def classify_email(email_row):
    if not OPENAI_API_KEY:
        return mock_classify_email(email_row)

    try:
        prompt = f"""
You are an email triage classifier for a production email assistant.

Classify conservatively.
If confidence is low, choose category='uncertain' and suggested_action='hold_for_review'.
Do not recommend destructive actions unless the email is clearly promotional or low-priority.
Mark needs_confirmation=true when the email asks for approval, verification, RSVP, or a time-sensitive reply.

Email:
Sender: {email_row.sender_email}
Subject: {email_row.subject}
Snippet: {email_row.snippet}
Body: {email_row.body_text}
"""

        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            text={"format": CLASSIFICATION_SCHEMA}
        )

        return json.loads(response.output_text)

    except Exception:
        return mock_classify_email(email_row)