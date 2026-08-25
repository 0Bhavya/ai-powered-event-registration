from typing import Optional
from datetime import date, time, datetime
from pydantic import BaseModel, ConfigDict
from app.models.event import EventStatus

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    venue: str
    event_date: date
    start_time: time
    end_time: time
    capacity: int
    ticket_price: float = 0.0
    status: EventStatus = EventStatus.DRAFT
    banner_image: Optional[str] = None

class EventCreate(EventBase):
    slug: str

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    venue: Optional[str] = None
    event_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    capacity: Optional[int] = None
    ticket_price: Optional[float] = None
    status: Optional[EventStatus] = None
    banner_image: Optional[str] = None

class EventRead(EventBase):
    id: int
    slug: str
    available_seats: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
