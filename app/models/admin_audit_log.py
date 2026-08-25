from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(255))
    entity_type: Mapped[str] = mapped_column(String(100)) # User, Event, Registration
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True) # changed to metadata_info because metadata is reserved in Base
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
