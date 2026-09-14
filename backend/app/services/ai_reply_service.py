from google import genai

from app.core.config import GEMINI_API_KEY


def generate_ai_reply(subject: str, sender: str, snippet: str):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
You are an AI email assistant.

Write a professional, concise reply to the email below.

Tone:
- polite
- clear
- human
- natural
- not too long
- do not invent information
- do not mention that you are an AI

Email:
Subject: {subject or ""}
Sender: {sender or ""}
Snippet: {snippet or ""}

Return only the reply text.
Do not use Markdown.
Do not add a subject line.
Do not add explanations before or after the reply.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    reply = response.text.strip()

    if not reply:
        raise ValueError("Gemini returned an empty reply")

    return reply