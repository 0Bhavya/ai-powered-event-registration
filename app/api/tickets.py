from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path

from app.database.session import get_db
from app.models.ticket import Ticket
from app.models.registration import Registration
from app.models.user import User
from app.schemas.ticket import TicketRead
from app.auth.deps import get_current_user
from app.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/{ticket_id}", response_model=TicketRead)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get ticket details."""
    ticket = db.query(Ticket).join(Registration).filter(
        Ticket.id == ticket_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if ticket.registration.user_id != current_user.id and current_user.role not in ["STAFF", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
        
    return ticket

@router.get("/{ticket_id}/qr")
def get_ticket_qr(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Return the physical QR code image file."""
    ticket = db.query(Ticket).join(Registration).filter(
        Ticket.id == ticket_id
    ).first()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if ticket.registration.user_id != current_user.id and current_user.role not in ["STAFF", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this ticket")
        
    if not ticket.qr_image_path:
        raise HTTPException(status_code=404, detail="QR code image not found")
        
    # qr_image_path is usually like "/static/images/qr/..."
    # Convert to absolute path
    file_path = settings.static_dir.parent / ticket.qr_image_path.lstrip("/")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="QR file missing on disk")
        
    return FileResponse(path=file_path, media_type="image/png")
