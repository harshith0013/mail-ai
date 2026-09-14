import json
import math
from pathlib import Path
from typing import List

from app.services.embedding_service import generate_embedding


STORE_PATH = Path("./embedding_store.json")


def _load_store() -> dict:
    if not STORE_PATH.exists():
        return {"items": {}}

    try:
        with STORE_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        return {"items": {}}


def _save_store(store: dict) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with STORE_PATH.open("w", encoding="utf-8") as file:
        json.dump(store, file)


def _cosine_similarity(
    a: List[float],
    b: List[float],
) -> float:
    if not a or not b:
        return 0.0

    # Prevent comparing embeddings generated with different dimensions/models.
    if len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))

    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def index_email(
    email_id: str,
    subject: str,
    sender: str,
    snippet: str,
):
    text = f"""
Subject: {subject or ""}
Sender: {sender or ""}
Snippet: {snippet or ""}
""".strip()

    # Emails are documents being retrieved.
    embedding = generate_embedding(
        text,
        task_type="RETRIEVAL_DOCUMENT",
    )

    store = _load_store()

    store.setdefault("items", {})[email_id] = {
        "embedding": embedding,
        "document": text,
        "metadata": {
            "email_id": email_id,
            "subject": subject or "",
            "sender": sender or "",
        },
    }

    _save_store(store)

    return {
        "email_id": email_id,
        "indexed": True,
    }


def search_emails(
    query: str,
    limit: int = 10,
):
    if not query or not query.strip():
        return {
            "ids": [[]],
            "scores": [[]],
        }

    # Search text is a retrieval query, not a document.
    query_embedding = generate_embedding(
        query.strip(),
        task_type="RETRIEVAL_QUERY",
    )

    store = _load_store()
    items = store.get("items", {})

    if not items:
        return {
            "ids": [[]],
            "scores": [[]],
        }

    scored = []

    for email_id, item in items.items():
        stored_embedding = item.get("embedding", [])

        score = _cosine_similarity(
            query_embedding,
            stored_embedding,
        )

        scored.append(
            (
                score,
                email_id,
            )
        )

    scored.sort(
        key=lambda pair: pair[0],
        reverse=True,
    )

    top_results = scored[:limit]

    ids = [
        email_id
        for score, email_id in top_results
    ]

    scores = [
        score
        for score, email_id in top_results
    ]

    return {
        "ids": [ids],
        "scores": [scores],
    }