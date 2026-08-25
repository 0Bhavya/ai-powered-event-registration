from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
import enum

class TicketStatus(str, enum.Enum):
    VALID = "VALID"
    USED = "USED"
    CANCELLED = "CANCELLED"
    INVALID = "INVALID"

class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id"))
    ticket_code: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    qr_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    qr_image_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    status: Mapped[TicketStatus] = mapped_column(String(50), default=TicketStatus.VALID)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    registration = relationship("Registration", back_populates="ticket")
    attendance_records = relationship("Attendance", back_populates="ticket")
