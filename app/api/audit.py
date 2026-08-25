from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.admin_audit_log import AdminAuditLog
from app.auth.deps import get_current_admin
from app.models.user import User

router = APIRouter()

@router.get("")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    limit: int = 50
) -> Any:
    """Admin only: Get recent audit logs."""
    logs = db.query(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": log.id,
            "admin_id": log.admin_id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "metadata_info": log.metadata_info,
            "created_at": log.created_at.isoformat()
        } for log in logs
    ]
