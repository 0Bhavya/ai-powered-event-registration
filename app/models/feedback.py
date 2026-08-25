from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id"), unique=True)
    rating: Mapped[int] = mapped_column(Integer) # 1-5
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    sentiment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # POSITIVE, NEUTRAL, NEGATIVE
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    registration = relationship("Registration", back_populates="feedback")
