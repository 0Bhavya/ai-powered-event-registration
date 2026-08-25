from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.admin_audit_log import AdminAuditLog

class AuditService:
    @staticmethod
    def log_audit(
        db: Session,
        admin_id: int,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        metadata_info: Optional[Dict[str, Any]] = None
    ) -> AdminAuditLog:
        """
        Creates an audit log entry for administrative actions.
        """
        audit_log = AdminAuditLog(
            admin_id=admin_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_info=metadata_info
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log
