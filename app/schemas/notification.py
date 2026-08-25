from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class NotificationRead(BaseModel):
    id: int
    user_id: int
    registration_id: Optional[int]
    type: str
    recipient: str
    status: str
    provider_id: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
