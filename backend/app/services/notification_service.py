from app.models.notification import Notification


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
    return notification