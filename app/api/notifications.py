from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationRead
from app.auth.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[NotificationRead])
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all notifications for the current user."""
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return notifications
