from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AttendanceScan(BaseModel):
    qr_token: str

class AttendanceResponse(BaseModel):
    success: bool
    message: str
    attendee_name: Optional[str] = None
    event_title: Optional[str] = None
    registration_id: Optional[int] = None
    scanned_at: Optional[datetime] = None

class AttendanceRead(BaseModel):
    id: int
    ticket_id: int
    checked_in_at: datetime
    checked_in_by: int
    status: str
    
    model_config = ConfigDict(from_attributes=True)
