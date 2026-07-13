import json
import math
from pathlib import Path

from app.services.embedding_service import generate_embedding

STORE_PATH = Path("./embedding_store.json")


def _load_store() -> dict:
    if not STORE_PATH.exists():
        return {"items": {}}

    with STORE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def _save_store(store: dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with STORE_PATH.open("w", encoding="utf-8") as file:
        json.dump(store, file)


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def index_email(email_id: str, subject: str, sender: str, snippet: str):
    text = f"""
Subject: {subject}
Sender: {sender}
Snippet: {snippet}
"""

    embedding = generate_embedding(text)
    store = _load_store()
    store.setdefault("items", {})[email_id] = {
        "embedding": embedding,
        "document": text,
        "metadata": {
            "email_id": email_id,
            "subject": subject,
            "sender": sender,
        },
    }
    _save_store(store)


def search_emails(query: str, limit: int = 10):
    query_embedding = generate_embedding(query)
    store = _load_store()
    items = store.get("items", {})

    if not items:
        return {"ids": [[]]}

    scored = []

    for email_id, item in items.items():
        score = _cosine_similarity(query_embedding, item["embedding"])
        scored.append((score, email_id))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    ids = [email_id for _, email_id in scored[:limit]]

    return {"ids": [ids]}
