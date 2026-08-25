import sys
import os
import random
import string
from datetime import date, time

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.models.event import Event, EventStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.payment import Payment, PaymentStatus

client = TestClient(app)

def test_payments():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    user_email = f"user_pay_{suffix}@example.com"
    user_password = "securepassword123"
    
    db = SessionLocal()
    from app.auth.security import get_password_hash
    
    try:
        # 1. Setup DB Data
        test_user = User(
            name="Pay Test User",
            email=user_email,
            password_hash=get_password_hash(user_password),
            role="USER"
        )
        db.add(test_user)
        
        test_event = Event(
            title=f"Pay Event {suffix}",
            slug=f"pay-event-{suffix}",
            venue="Online",
            event_date=date(2026, 12, 1),
            start_time=time(10, 0),
            end_time=time(12, 0),
            capacity=10,
            available_seats=10,
            ticket_price=100.0,
            status=EventStatus.PUBLISHED
        )
        db.add(test_event)
        db.commit()
        db.refresh(test_user)
        db.refresh(test_event)
        
        # Manually create PENDING registration
        test_reg = Registration(
            registration_code=f"REG-{suffix}",
            user_id=test_user.id,
            event_id=test_event.id,
            status=RegistrationStatus.PENDING
        )
        db.add(test_reg)
        db.commit()
        db.refresh(test_reg)
        
        # 2. Login User
        response = client.post(
            "/api/auth/login",
            data={"username": user_email, "password": user_password}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create Order
        print("Testing Order Creation...")
        response = client.post(
            "/api/payments/create-order", 
            json={"registration_id": test_reg.id}, 
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Order creation failed: {response.text}")
            sys.exit(1)
            
        order_data = response.json()
        print(f"Order created successfully! Demo Mode: {order_data['demo_mode']}")
        
        if not order_data["demo_mode"]:
            print("Warning: Not in demo mode, but expected demo mode.")
            
        order_id = order_data["order_id"]
        
        # 4. Verify Payment (Simulate success in demo mode)
        print("Testing Payment Verification...")
        # In demo mode, signature must start with "demo_sig_"
        verify_payload = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": f"pay_demo_{suffix}",
            "razorpay_signature": f"demo_sig_valid_{suffix}"
        }
        
        response = client.post("/api/payments/verify", json=verify_payload, headers=headers)
        if response.status_code != 200:
            print(f"Payment verification failed: {response.text}")
            sys.exit(1)
            
        print("Payment verified successfully!")
        
        # 5. Check Registration Status changed to CONFIRMED
        db.refresh(test_reg)
        if test_reg.status != RegistrationStatus.CONFIRMED:
            print(f"Registration status was not updated to CONFIRMED. Is {test_reg.status}")
            sys.exit(1)
            
        print("Payment workflow testing completed successfully!")
        
    finally:
        # Cleanup
        db.query(Payment).filter(Payment.registration_id == test_reg.id).delete()
        db.delete(test_reg)
        db.delete(test_event)
        db.delete(test_user)
        db.commit()
        db.close()

if __name__ == "__main__":
    test_payments()
