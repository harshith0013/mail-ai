from uuid import UUID
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.email_message import EmailMessage
from app.models.classification_result import ClassificationResult
from app.models.gmail_account import GmailAccount
from app.services.gmail_service import GmailService


router = APIRouter(
    prefix="/api/v1/review",
    tags=["Review"],
)


class ReviewActionRequest(BaseModel):
    action: str


@router.post("/{email_id}")
def review_email(
    email_id: UUID,
    data: ReviewActionRequest,
):
    db: Session = SessionLocal()

    try:
        print("=" * 70)
        print("REVIEW ACTION STARTED")
        print("Email ID:", email_id)
        print("Action:", data.action)
        print("=" * 70)

        # --------------------------------------------------
        # Validate action
        # --------------------------------------------------
        if data.action not in ["keep", "archive"]:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid action. "
                    "Allowed actions: keep, archive"
                ),
            )

        # --------------------------------------------------
        # Find email
        # --------------------------------------------------
        email = (
            db.query(EmailMessage)
            .filter(EmailMessage.id == email_id)
            .first()
        )

        if not email:
            raise HTTPException(
                status_code=404,
                detail="Email not found",
            )

        print("Email found:", email.subject)
        print("Gmail message ID:", email.gmail_message_id)

        # --------------------------------------------------
        # Find latest classification
        # --------------------------------------------------
        classification = (
            db.query(ClassificationResult)
            .filter(
                ClassificationResult.email_message_id == email.id
            )
            .order_by(
                ClassificationResult.created_at.desc()
            )
            .first()
        )

        if not classification:
            raise HTTPException(
                status_code=404,
                detail="Classification not found",
            )

        print(
            "Classification found:",
            classification.id,
        )

        # ==================================================
        # KEEP IN INBOX
        # ==================================================
        if data.action == "keep":

            print("Processing KEEP action...")

            email.is_archived = False
            classification.suggested_action = "keep_inbox"
            classification.category = "important"

            # Save review decision to database
            db.commit()

            print("Review decision saved to database.")

            # --------------------------------------------------
            # Try to restore Gmail INBOX label
            # --------------------------------------------------
            try:
                gmail_account = (
                    db.query(GmailAccount)
                    .filter(
                        GmailAccount.user_id == email.user_id
                    )
                    .first()
                )

                if not gmail_account:
                    print(
                        "Gmail account not found. "
                        "Skipping Gmail update."
                    )

                elif not email.gmail_message_id:
                    print(
                        "Gmail message ID is missing. "
                        "Skipping Gmail update."
                    )

                else:
                    print(
                        "Restoring Gmail INBOX label..."
                    )

                    gmail_service = GmailService(
                        access_token=(
                            gmail_account.access_token_encrypted
                        ),
                        refresh_token=(
                            gmail_account.refresh_token_encrypted
                        ),
                    )

                    gmail_service.modify_labels(
                        message_id=email.gmail_message_id,
                        add_labels=["INBOX"],
                    )

                    print(
                        "Gmail INBOX label restored successfully."
                    )

            except Exception as gmail_error:
                print("=" * 70)
                print("GMAIL KEEP WARNING")
                print(
                    "Gmail update failed, but the review "
                    "decision was saved."
                )
                print(
                    "Error type:",
                    type(gmail_error).__name__,
                )
                print(
                    "Error:",
                    str(gmail_error),
                )
                traceback.print_exc()
                print("=" * 70)

            return {
                "message": "Email kept in inbox",
                "email_id": str(email.id),
                "action": "keep",
            }

        # ==================================================
        # ARCHIVE
        # ==================================================
        if data.action == "archive":

            print("Processing ARCHIVE action...")

            email.is_archived = True
            classification.suggested_action = "archive"
            classification.category = "archive_reference"

            # Save review decision to database
            db.commit()

            print("Review decision saved to database.")

            # --------------------------------------------------
            # Try to archive Gmail message
            # --------------------------------------------------
            try:
                gmail_account = (
                    db.query(GmailAccount)
                    .filter(
                        GmailAccount.user_id == email.user_id
                    )
                    .first()
                )

                if not gmail_account:
                    print(
                        "Gmail account not found. "
                        "Skipping Gmail archive."
                    )

                elif not email.gmail_message_id:
                    print(
                        "Gmail message ID is missing. "
                        "Skipping Gmail archive."
                    )

                else:
                    print(
                        "Archiving Gmail message..."
                    )

                    gmail_service = GmailService(
                        access_token=(
                            gmail_account.access_token_encrypted
                        ),
                        refresh_token=(
                            gmail_account.refresh_token_encrypted
                        ),
                    )

                    gmail_service.archive_message(
                        email.gmail_message_id
                    )

                    print(
                        "Gmail message archived successfully."
                    )

            except Exception as gmail_error:
                print("=" * 70)
                print("GMAIL ARCHIVE WARNING")
                print(
                    "Gmail archive failed, but the review "
                    "decision was saved."
                )
                print(
                    "Error type:",
                    type(gmail_error).__name__,
                )
                print(
                    "Error:",
                    str(gmail_error),
                )
                traceback.print_exc()
                print("=" * 70)

            return {
                "message": "Email archived",
                "email_id": str(email.id),
                "action": "archive",
            }

    # ======================================================
    # FastAPI HTTP errors
    # ======================================================
    except HTTPException:
        raise

    # ======================================================
    # Unexpected errors
    # ======================================================
    except Exception as e:

        db.rollback()

        print("=" * 70)
        print("REVIEW ACTION ERROR")
        print("Email ID:", email_id)
        print("Action:", data.action)
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
        print("=" * 70)

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        db.close()