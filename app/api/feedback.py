from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from textblob import TextBlob

from app.database.session import get_db
from app.models.feedback import Feedback
from app.models.registration import Registration
from app.schemas.feedback import FeedbackCreate, FeedbackRead
from app.auth.deps import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter()

def analyze_sentiment(text: str) -> tuple[str, float]:
    """Returns (sentiment_label, score). Score is between -1 and 1."""
    if not text or not text.strip():
        return "NEUTRAL", 0.0
        
    blob = TextBlob(text)
    score = blob.sentiment.polarity
    
    if score > 0.1:
        label = "POSITIVE"
    elif score < -0.1:
        label = "NEGATIVE"
    else:
        label = "NEUTRAL"
        
    return label, score

@router.post("", response_model=FeedbackRead, status_code=status.HTTP_201_CREATED)
def submit_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Submit post-event feedback."""
    # Ensure registration belongs to user and exists
    registration = db.query(Registration).filter(
        Registration.id == feedback_in.registration_id,
        Registration.user_id == current_user.id
    ).first()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
        
    # Check if feedback already submitted
    existing = db.query(Feedback).filter(Feedback.registration_id == feedback_in.registration_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Feedback already submitted for this registration")
        
    # Analyze sentiment
    sentiment_label, sentiment_score = analyze_sentiment(feedback_in.comment)
    
    feedback = Feedback(
        registration_id=feedback_in.registration_id,
        rating=feedback_in.rating,
        comment=feedback_in.comment,
        sentiment=sentiment_label,
        sentiment_score=sentiment_score
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback

@router.get("/admin", response_model=List[FeedbackRead])
def get_all_feedback(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Admin only: Get all feedback."""
    return db.query(Feedback).order_by(Feedback.created_at.desc()).offset(skip).limit(limit).all()
