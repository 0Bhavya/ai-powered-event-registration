from datetime import datetime, date, time, timezone
from typing import Optional
from sqlalchemy import String, Integer, Text, Date, Time, Numeric, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
import enum

class EventStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    FULL = "FULL"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    venue: Mapped[str] = mapped_column(String(255))
    event_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    
    capacity: Mapped[int] = mapped_column(Integer)
    available_seats: Mapped[int] = mapped_column(Integer)
    ticket_price: Mapped[float] = mapped_column(Numeric(10, 2), default=0.0)
    
    status: Mapped[EventStatus] = mapped_column(String(50), default=EventStatus.DRAFT)
    banner_image: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    registrations = relationship("Registration", back_populates="event")
