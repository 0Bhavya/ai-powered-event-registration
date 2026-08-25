from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.registration import RiskLevel

class FraudCheckRequest(BaseModel):
    user_id: int
    event_id: int
    email: str
    phone: Optional[str] = None
    ip_hash: Optional[str] = None

class FraudCheckResponse(BaseModel):
    risk_score: int
    risk_level: RiskLevel
    reasons: List[str]

class FraudLogRead(BaseModel):
    id: int
    registration_id: Optional[int]
    email: Optional[str]
    phone: Optional[str]
    risk_score: int
    risk_level: str
    reasons: List[str]
    ip_hash: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
