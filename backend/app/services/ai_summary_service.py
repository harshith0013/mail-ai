import json
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY


def generate_email_summary(subject: str, sender: str, snippet: str):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are an AI email assistant.

Analyze the email and return ONLY valid JSON.

Required JSON format:
{{
  "summary": "short 2-3 sentence summary",
  "priority": "Low | Medium | High",
  "needs_reply": true,
  "action_items": ["item 1", "item 2"]
}}

Email:
Subject: {subject}
Sender: {sender}
Snippet: {snippet}
"""

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    if raw_text.startswith("```json"):
        raw_text = raw_text.replace("```json", "").replace("```", "").strip()
    elif raw_text.startswith("```"):
        raw_text = raw_text.replace("```", "").strip()

    return json.loads(raw_text)