from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.payment import Payment, PaymentStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.event import Event
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus
from app.schemas.payment import PaymentCreateOrder, PaymentOrderResponse, PaymentVerify, PaymentRead
from app.services.payment_service import PaymentService
from app.services.qr_service import QRService
from app.auth.deps import get_current_user
from app.config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/create-order", response_model=PaymentOrderResponse)
def create_order(
    request: PaymentCreateOrder,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Create a payment order for a registration."""
    # Find registration
    registration = db.query(Registration).filter(
        Registration.id == request.registration_id,
        Registration.user_id == current_user.id
    ).first()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
        
    if registration.status != RegistrationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Registration is not in a valid state for payment")
        
    # Get associated event for price
    event = db.query(Event).filter(Event.id == registration.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    amount = float(event.ticket_price)
    
    # If event is free, skip payment (in a real app, auto-confirm)
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Event is free. No payment required.")
        
    # Create order via Payment Service
    payment_service = PaymentService()
    receipt = str(registration.registration_code)
    
    try:
        order_data = payment_service.create_order(amount, receipt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment gateway error: {str(e)}")
        
    # Store payment record as PENDING
    payment = Payment(
        registration_id=registration.id,
        order_id=order_data["id"],
        amount=amount,
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return {
        "order_id": order_data["id"],
        "amount": amount,
        "currency": "INR",
        "key_id": settings.razorpay_key_id if not order_data["demo_mode"] else "demo_key",
        "demo_mode": order_data["demo_mode"]
    }

@router.post("/verify")
def verify_payment(
    verify_data: PaymentVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Verify a completed payment signature."""
    # Find payment record
    payment = db.query(Payment).join(Registration).filter(
        Payment.order_id == verify_data.razorpay_order_id,
        Registration.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
        
    if payment.status == PaymentStatus.SUCCESS:
        return {"message": "Payment already verified", "payment_id": payment.id}
        
    payment_service = PaymentService()
    is_valid = payment_service.verify_signature(
        verify_data.razorpay_order_id, 
        verify_data.razorpay_payment_id, 
        verify_data.razorpay_signature
    )
    
    if not is_valid:
        # Mark payment as failed if signature is invalid
        payment.status = PaymentStatus.FAILED
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid payment signature")
        
    # Payment is successful
    payment.status = PaymentStatus.SUCCESS
    payment.payment_id = verify_data.razorpay_payment_id
    payment.signature = verify_data.razorpay_signature
    
    # Update Registration Status
    registration = payment.registration
    registration.status = RegistrationStatus.CONFIRMED
    
    # Phase 8: Generate Ticket and QR Code
    import uuid
    ticket_code = f"TKT-{registration.registration_code}-{str(uuid.uuid4().hex[:6]).upper()}"
    qr_token = str(uuid.uuid4())
    
    qr_service = QRService()
    qr_path = qr_service.generate_qr_code(qr_token, ticket_code)
    
    ticket = Ticket(
        registration_id=registration.id,
        ticket_code=ticket_code,
        qr_token=qr_token,
        qr_image_path=qr_path,
        status=TicketStatus.VALID
    )
    db.add(ticket)
    
    db.commit()
    db.refresh(ticket)
    
    return {"message": "Payment verified successfully", "registration_id": registration.id, "ticket_id": ticket.id}

@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    payment = db.query(Payment).join(Registration).filter(
        Payment.id == payment_id,
        Registration.user_id == current_user.id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
        
    return payment
