import uuid
import hmac
import hashlib
import razorpay
from typing import Dict, Any

from app.config import get_settings

settings = get_settings()

class PaymentService:
    def __init__(self):
        self.demo_mode = settings.demo_payment_mode
        self.key_id = settings.razorpay_key_id
        self.key_secret = settings.razorpay_key_secret
        
        if not self.demo_mode and (not self.key_id or not self.key_secret):
            # Fallback to demo mode if credentials are missing
            self.demo_mode = True
            
        if not self.demo_mode:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
            
    def create_order(self, amount: float, receipt: str) -> Dict[str, Any]:
        """Creates a Razorpay order. amount is in regular currency (INR), Razorpay expects paise."""
        amount_in_paise = int(amount * 100)
        
        if self.demo_mode:
            # Simulate Razorpay order response
            return {
                "id": f"order_demo_{uuid.uuid4().hex[:10]}",
                "entity": "order",
                "amount": amount_in_paise,
                "amount_paid": 0,
                "amount_due": amount_in_paise,
                "currency": "INR",
                "receipt": receipt,
                "status": "created",
                "attempts": 0,
                "notes": [],
                "created_at": 1600000000,
                "demo_mode": True
            }
            
        order_data = {
            "amount": amount_in_paise,
            "currency": "INR",
            "receipt": receipt,
            "payment_capture": 1 # Auto capture
        }
        order = self.client.order.create(data=order_data)
        order["demo_mode"] = False
        return order
        
    def verify_signature(self, order_id: str, payment_id: str, signature: str) -> bool:
        """Verifies the Razorpay payment signature."""
        if self.demo_mode:
            # In demo mode, any signature starting with 'demo_sig_' is considered valid
            return signature.startswith("demo_sig_")
            
        try:
            # razorpay utility method verify_payment_signature can also be used, 
            # but doing it manually is straightforward
            msg = f"{order_id}|{payment_id}"
            generated_signature = hmac.new(
                self.key_secret.encode(), 
                msg.encode(), 
                hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(generated_signature, signature)
        except Exception:
            return False
