from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    checked_in_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    checked_in_by: Mapped[int] = mapped_column(ForeignKey("users.id")) # Staff or admin ID
    status: Mapped[str] = mapped_column(String(50), default="PRESENT")
    
    ticket = relationship("Ticket", back_populates="attendance_records")
    checker = relationship("User", foreign_keys=[checked_in_by])
