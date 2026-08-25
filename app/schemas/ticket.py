from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.ticket import TicketStatus

class TicketRead(BaseModel):
    id: int
    registration_id: int
    ticket_code: str
    qr_token: str
    qr_image_path: Optional[str]
    status: TicketStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
