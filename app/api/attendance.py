from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database.session import get_db
from app.models.attendance import Attendance
from app.models.ticket import Ticket, TicketStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.event import Event
from app.models.user import User
from app.schemas.attendance import AttendanceScan, AttendanceResponse, AttendanceRead
from app.auth.deps import get_current_staff, get_current_admin

router = APIRouter()

@router.post("/scan", response_model=AttendanceResponse)
def scan_ticket(
    scan_in: AttendanceScan,
    db: Session = Depends(get_db),
    current_staff: User = Depends(get_current_staff)
) -> Any:
    """Scan a QR code token and mark attendance."""
    # Find ticket by qr_token
    ticket = db.query(Ticket).filter(Ticket.qr_token == scan_in.qr_token).first()
    
    if not ticket:
        return AttendanceResponse(
            success=False,
            message="Invalid Ticket: QR code not found in system."
        )
        
    registration = ticket.registration
    
    if not registration:
        return AttendanceResponse(
            success=False,
            message="Invalid Ticket: Registration missing."
        )
        
    user = registration.user
    event = registration.event
    
    if ticket.status == TicketStatus.USED:
        return AttendanceResponse(
            success=False,
            message="Already Checked In",
            attendee_name=user.name,
            event_title=event.title,
            registration_id=registration.id
        )
        
    if ticket.status != TicketStatus.VALID or registration.status != RegistrationStatus.CONFIRMED:
        return AttendanceResponse(
            success=False,
            message="Invalid Ticket: Ticket is not valid or registration is not confirmed."
        )
        
    # Mark as used and record attendance
    ticket.status = TicketStatus.USED
    
    attendance = Attendance(
        ticket_id=ticket.id,
        checked_in_by=current_staff.id,
        status="PRESENT"
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return AttendanceResponse(
        success=True,
        message="Check-in successful",
        attendee_name=user.name,
        event_title=event.title,
        registration_id=registration.id,
        scanned_at=attendance.checked_in_at
    )

@router.get("/admin/attendance", response_model=List[AttendanceRead])
def get_attendance_logs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """Get all attendance records. Admin only."""
    records = db.query(Attendance).order_by(Attendance.checked_in_at.desc()).offset(skip).limit(limit).all()
    return records
