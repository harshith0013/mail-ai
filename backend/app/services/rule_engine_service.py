def decide_action(classification: dict):
    if classification["needs_confirmation"]:
        return "notify_user"

    if classification["category"] == "important":
        return "notify_user"

    if classification["category"] in ["promotions", "newsletter"] and classification["confidence"] >= 0.85:
        return "archive"

    if classification["category"] == "archive_reference" and classification["confidence"] >= 0.85:
        return "archive"

    if classification["category"] == "uncertain" or classification["confidence"] < 0.75:
        return "hold_for_review"

    return "label_only"