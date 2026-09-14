import json

from google import genai

from app.core.config import GEMINI_API_KEY


def generate_email_summary(subject: str, sender: str, snippet: str):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are an AI email assistant.

Analyze the email below and return ONLY valid JSON.

Required JSON format:
{{
  "summary": "short 2-3 sentence summary",
  "priority": "Low | Medium | High",
  "needs_reply": true,
  "action_items": ["item 1", "item 2"]
}}

Rules:
- summary must be concise and factual.
- priority must be exactly Low, Medium, or High.
- needs_reply must be a boolean.
- action_items must be a JSON array of strings.
- If there are no action items, return an empty array.
- Do not include Markdown.
- Do not include ```json fences.

Email:
Subject: {subject or ""}
Sender: {sender or ""}
Snippet: {snippet or ""}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["Low", "Medium", "High"]
                    },
                    "needs_reply": {
                        "type": "boolean"
                    },
                    "action_items": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": [
                    "summary",
                    "priority",
                    "needs_reply",
                    "action_items"
                ]
            }
        }
    )

    raw_text = response.text.strip()

    if not raw_text:
        raise ValueError("Gemini returned an empty response")

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {raw_text}"
        ) from exc