from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.registration import RegistrationStatus, RiskLevel

class RegistrationBase(BaseModel):
    event_id: int

class RegistrationCreate(RegistrationBase):
    pass
    # Depending on frontend, they might send other things, but user data comes from JWT token 
    # and event_id is the primary requirement.

class RegistrationCheck(RegistrationBase):
    pass

class RegistrationCheckResponse(BaseModel):
    event_id: int
    available_seats: int
    is_available: bool

class RegistrationRead(RegistrationBase):
    id: int
    user_id: int
    registration_code: Optional[str]
    status: RegistrationStatus
    risk_score: Optional[int]
    risk_level: Optional[RiskLevel]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
