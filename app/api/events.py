from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.event import Event, EventStatus
from app.models.user import User
from app.schemas.event import EventCreate, EventUpdate, EventRead
from app.auth.deps import get_current_admin

router = APIRouter()

@router.get("", response_model=List[EventRead])
def get_events(
    db: Session = Depends(get_db), 
    skip: int = 0, 
    limit: int = 100,
    include_drafts: bool = False
) -> Any:
    """Retrieve all events. Only PUBLISHED events are shown by default unless requested by admin."""
    query = db.query(Event)
    if not include_drafts:
        query = query.filter(Event.status == EventStatus.PUBLISHED)
    events = query.offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)) -> Any:
    """Get a specific event by ID."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> Any:
    """Create a new event. Admin only."""
    # Check if slug exists
    if db.query(Event).filter(Event.slug == event_in.slug).first():
        raise HTTPException(status_code=400, detail="Event slug already exists")
        
    event = Event(
        **event_in.model_dump(),
        available_seats=event_in.capacity # Initially available seats = total capacity
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.put("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> Any:
    """Update an event. Admin only."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    update_data = event_in.model_dump(exclude_unset=True)
    
    # If capacity is updated, we might need to recalculate available seats in a real app,
    # but for this simplicity, we'll just allow basic updates.
    if "capacity" in update_data:
        capacity_diff = update_data["capacity"] - event.capacity
        event.available_seats += capacity_diff
        
    for field, value in update_data.items():
        setattr(event, field, value)
        
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
) -> None:
    """Delete an event. Admin only."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # In a real app we might soft-delete or cancel it instead to preserve registrations.
    # We will delete it here.
    db.delete(event)
    db.commit()
