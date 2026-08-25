from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.fraud_log import FraudLog
from app.models.user import User
from app.schemas.fraud import FraudCheckRequest, FraudCheckResponse, FraudLogRead
from app.services.fraud_detector import FraudDetector
from app.auth.deps import get_current_admin

router = APIRouter()

@router.post("/check", response_model=FraudCheckResponse)
def check_fraud(
    request: FraudCheckRequest,
    db: Session = Depends(get_db),
    # Internally could be used by another service, or tested directly by admin
) -> Any:
    """Manually test fraud detection rules."""
    detector = FraudDetector(db)
    result = detector.evaluate(request)
    return result

@router.get("/admin/fraud-logs", response_model=List[FraudLogRead])
def get_fraud_logs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Get all fraud logs. Admin only."""
    logs = db.query(FraudLog).order_by(FraudLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs
