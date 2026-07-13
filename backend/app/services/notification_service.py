import asyncio

from app.models.notification import Notification
from app.services.websocket_manager import manager


def _broadcast_notification(payload: dict) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(manager.broadcast(payload))
    else:
        loop.create_task(manager.broadcast(payload))


def create_notification(db, user_id, email_message_id, notif_type, title, message):
    notification = Notification(
        user_id=user_id,
        email_message_id=email_message_id,
        type=notif_type,
        title=title,
        message=message,
        status="unread",
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    _broadcast_notification(
        {
            "type": "new_notification",
            "notification_id": str(notification.id),
            "title": notification.title,
            "message": notification.message,
            "status": notification.status,
        }
    )

    return notification