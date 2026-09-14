from typing import Optional, List

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

from app.core.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
)


class GmailService:
    def __init__(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
    ):
        self.access_token = access_token
        self.refresh_token = refresh_token

        self.creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
        )

        self.service = build(
            "gmail",
            "v1",
            credentials=self.creds,
        )

    def list_messages(self, max_results: int = 10):
        result = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                maxResults=max_results,
            )
            .execute()
        )

        return result.get("messages", [])

    def get_message(self, message_id: str):
        return (
            self.service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
            .execute()
        )

    def list_labels(self):
        result = (
            self.service.users()
            .labels()
            .list(userId="me")
            .execute()
        )

        return result.get("labels", [])

    def modify_labels(
        self,
        message_id: str,
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ):
        body = {
            "addLabelIds": add_labels or [],
            "removeLabelIds": remove_labels or [],
        }

        return (
            self.service.users()
            .messages()
            .modify(
                userId="me",
                id=message_id,
                body=body,
            )
            .execute()
        )

    def archive_message(self, message_id: str):
        return self.modify_labels(
            message_id=message_id,
            remove_labels=["INBOX"],
        )

    def mark_as_read(self, message_id: str):
        return self.modify_labels(
            message_id=message_id,
            remove_labels=["UNREAD"],
        )

    def mark_as_unread(self, message_id: str):
        return self.modify_labels(
            message_id=message_id,
            add_labels=["UNREAD"],
        )