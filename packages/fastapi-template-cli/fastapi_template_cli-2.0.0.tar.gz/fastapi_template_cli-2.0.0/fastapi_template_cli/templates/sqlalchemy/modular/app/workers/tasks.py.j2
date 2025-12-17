"""Celery tasks for background processing."""

import time
from typing import Any, Dict

from celery import shared_task

from app.database.session import get_db
from app.models.users import User


@shared_task(bind=True)
def debug_task(self) -> Dict[str, Any]:
    """A simple debug task that prints request information."""
    print(f"Request: {self.request!r}")
    return {"status": "success", "result": "debug task completed"}


@shared_task
def send_email_task(to_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Send email in background."""
    # TODO: Implement actual email sending
    print(f"Sending email to {to_email}: {subject}")
    return {"status": "success", "message": f"Email sent to {to_email}"}


@shared_task
def process_user_registration(user_id: int) -> Dict[str, Any]:
    """Process user registration tasks."""
    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Simulate some processing
            time.sleep(2)
            print(f"Processed registration for user {user.email}")
            return {"status": "success", "user_id": user_id}
        return {"status": "error", "message": "User not found"}
    finally:
        db.close()


@shared_task
def cleanup_expired_tokens() -> Dict[str, Any]:
    """Clean up expired tokens and sessions."""
    # TODO: Implement token cleanup
    print("Cleaning up expired tokens...")
    return {"status": "success", "message": "Token cleanup completed"}


@shared_task
def generate_report(report_type: str) -> Dict[str, Any]:
    """Generate various reports."""
    print(f"Generating {report_type} report...")
    # Simulate report generation
    time.sleep(5)
    return {
        "status": "success",
        "report_type": report_type,
        "generated_at": time.time(),
    }
