import google.generativeai as genai

from app.core.config import GEMINI_API_KEY


def generate_embedding(text: str):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    genai.configure(api_key=GEMINI_API_KEY)

    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document",
    )

    return result["embedding"]
