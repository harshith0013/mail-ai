import google.generativeai as genai

from app.core.config import GEMINI_API_KEY


def generate_ai_reply(subject: str, sender: str, snippet: str):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-2.5-flash")

    prompt = f"""
You are an AI email assistant.

Write a professional, concise reply to the email below.

Tone:
- polite
- clear
- human
- not too long

Email:
Subject: {subject}
Sender: {sender}
Snippet: {snippet}

Return only the reply text.
"""

    response = model.generate_content(prompt)

    return response.text.strip()