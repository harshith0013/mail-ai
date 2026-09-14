from google import genai
from google.genai import types

from app.core.config import GEMINI_API_KEY


def generate_embedding(
    text: str,
    task_type: str = "RETRIEVAL_DOCUMENT",
):
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing")

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    client = genai.Client(api_key=GEMINI_API_KEY)

    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config=types.EmbedContentConfig(
            task_type=task_type,
            output_dimensionality=768,
        ),
    )

    if not result.embeddings:
        raise ValueError("Gemini returned no embeddings")

    embedding = result.embeddings[0].values

    if not embedding:
        raise ValueError("Gemini returned an empty embedding")

    return embedding