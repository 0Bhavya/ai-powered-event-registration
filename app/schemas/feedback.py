from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class FeedbackCreate(BaseModel):
    registration_id: int
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    comment: Optional[str] = Field(None, max_length=1000)

class FeedbackRead(BaseModel):
    id: int
    registration_id: int
    rating: int
    comment: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
