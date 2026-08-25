from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
import enum

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    registration_id: Mapped[int] = mapped_column(ForeignKey("registrations.id"))
    provider: Mapped[str] = mapped_column(String(50), default="razorpay")
    order_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payment_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    status: Mapped[PaymentStatus] = mapped_column(String(50), default=PaymentStatus.PENDING)
    signature: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    registration = relationship("Registration", back_populates="payment")
