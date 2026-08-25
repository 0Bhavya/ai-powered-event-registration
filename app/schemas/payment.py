from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.payment import PaymentStatus

class PaymentCreateOrder(BaseModel):
    registration_id: int

class PaymentOrderResponse(BaseModel):
    order_id: str
    amount: float
    currency: str
    key_id: Optional[str] = None # Frontend needs this to open Razorpay checkout
    demo_mode: bool = False

class PaymentVerify(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentRead(BaseModel):
    id: int
    registration_id: int
    provider: str
    order_id: Optional[str]
    payment_id: Optional[str]
    amount: float
    currency: str
    status: PaymentStatus
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
