import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.registration import Registration, RegistrationStatus, RiskLevel
from app.models.event import Event, EventStatus
from app.models.user import User
from app.models.fraud_log import FraudLog
from app.schemas.registration import (
    RegistrationCreate, 
    RegistrationRead, 
    RegistrationCheck, 
    RegistrationCheckResponse
)
from app.schemas.fraud import FraudCheckRequest
from app.services.fraud_detector import FraudDetector
from app.auth.deps import get_current_user, get_current_admin

router = APIRouter()

def generate_registration_code() -> str:
    # Example: EVT-2026-000123
    return f"EVT-2026-{str(uuid.uuid4().int)[:6]}"

@router.post("/check", response_model=RegistrationCheckResponse)
def check_availability(
    check_in: RegistrationCheck,
    db: Session = Depends(get_db)
) -> Any:
    """Check if an event has available seats."""
    event = db.query(Event).filter(Event.id == check_in.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    return {
        "event_id": event.id,
        "available_seats": event.available_seats,
        "is_available": event.available_seats > 0 and event.status == EventStatus.PUBLISHED
    }

@router.post("", response_model=RegistrationRead, status_code=status.HTTP_201_CREATED)
def create_registration(
    reg_in: RegistrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Register for an event."""
    
    # 1. Ensure user is not already registered (avoid duplicate)
    existing_reg = db.query(Registration).filter(
        Registration.event_id == reg_in.event_id,
        Registration.user_id == current_user.id,
        Registration.status != RegistrationStatus.CANCELLED,
        Registration.status != RegistrationStatus.FAILED
    ).first()
    
    if existing_reg:
        raise HTTPException(
            status_code=400, 
            detail="You are already registered or have a pending registration for this event."
        )

    # 2. Check seat availability with locking
    # We lock the event row to prevent concurrent overbooking
    event = db.query(Event).filter(Event.id == reg_in.event_id).with_for_update().first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    if event.status != EventStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Event is not open for registration")
        
    if event.available_seats <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Event Full / Registration Closed"
        )
        
    # Fraud Check
    detector = FraudDetector(db)
    fraud_request = FraudCheckRequest(
        user_id=current_user.id,
        event_id=event.id,
        email=current_user.email,
        phone=current_user.phone
    )
    fraud_result = detector.evaluate(fraud_request)
    
    reg_code = generate_registration_code()
    
    if fraud_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
        # Block the registration
        registration = Registration(
            registration_code=reg_code,
            user_id=current_user.id,
            event_id=event.id,
            status=RegistrationStatus.BLOCKED,
            risk_score=fraud_result.risk_score,
            risk_level=fraud_result.risk_level
        )
        db.add(registration)
        db.flush() # To get registration.id
        
        fraud_log = FraudLog(
            registration_id=registration.id,
            email=current_user.email,
            phone=current_user.phone,
            risk_score=fraud_result.risk_score,
            risk_level=fraud_result.risk_level,
            reasons=fraud_result.reasons
        )
        db.add(fraud_log)
        db.commit()
        db.refresh(registration)
        # We can either return the blocked registration, or throw an error. 
        # The prompt says: "If risk is HIGH or CRITICAL: Show animated fraud-blocking state... terminate the registration flow."
        # We return the registration object, and frontend checks the status.
        return registration
    
    # Otherwise, it's safe to create as PENDING
    registration = Registration(
        registration_code=reg_code,
        user_id=current_user.id,
        event_id=event.id,
        status=RegistrationStatus.PENDING,
        risk_score=fraud_result.risk_score,
        risk_level=fraud_result.risk_level
    )
    
    db.add(registration)
    
    # Temporarily decrement seat while payment is pending. 
    # If payment fails/cancels, we should restore it.
    event.available_seats -= 1
    
    db.commit()
    db.refresh(registration)
    
    return registration

@router.get("/my-registrations", response_model=List[RegistrationRead])
def get_my_registrations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get all registrations for the current user."""
    registrations = db.query(Registration).filter(
        Registration.user_id == current_user.id
    ).all()
    return registrations

@router.get("/admin/all", response_model=List[RegistrationRead])
def get_all_registrations(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> Any:
    """Admin only: Get all registrations globally."""
    registrations = db.query(Registration).order_by(Registration.created_at.desc()).all()
    return registrations

@router.get("/{registration_id}", response_model=RegistrationRead)
def get_registration(
    registration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get details of a specific registration."""
    registration = db.query(Registration).filter(Registration.id == registration_id).first()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
        
    if registration.user_id != current_user.id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return registration
