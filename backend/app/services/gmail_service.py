from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class GmailService:
    def __init__(self, access_token: str, refresh_token: str | None = None):
        self.creds = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
        )
        self.service = build("gmail", "v1", credentials=self.creds)

    def list_messages(self, max_results: int = 10):
        result = self.service.users().messages().list(
            userId="me",
            maxResults=max_results
        ).execute()
        return result.get("messages", [])

    def get_message(self, message_id: str):
        return self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

    def list_labels(self):
        return self.service.users().labels().list(userId="me").execute()

    def modify_labels(self, message_id: str, add_labels=None, remove_labels=None):
        body = {
            "addLabelIds": add_labels or [],
            "removeLabelIds": remove_labels or []
        }
        return self.service.users().messages().modify(
            userId="me",
            id=message_id,
            body=body
        ).execute()