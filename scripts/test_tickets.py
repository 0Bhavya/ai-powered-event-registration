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
from app.models.ticket import Ticket

client = TestClient(app)

def test_tickets():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    user_email = f"user_tkt_{suffix}@example.com"
    user_password = "securepassword123"
    
    db = SessionLocal()
    from app.auth.security import get_password_hash
    
    try:
        # 1. Setup DB Data
        test_user = User(
            name="Tkt Test User",
            email=user_email,
            password_hash=get_password_hash(user_password),
            role="USER"
        )
        db.add(test_user)
        
        test_event = Event(
            title=f"Tkt Event {suffix}",
            slug=f"tkt-event-{suffix}",
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
        
        # 3. Create Order & Verify (This should trigger ticket creation)
        print("Testing Order Creation...")
        response = client.post("/api/payments/create-order", json={"registration_id": test_reg.id}, headers=headers)
        order_id = response.json()["order_id"]
        
        print("Testing Payment Verification to Generate Ticket...")
        verify_payload = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": f"pay_demo_{suffix}",
            "razorpay_signature": f"demo_sig_valid_{suffix}"
        }
        response = client.post("/api/payments/verify", json=verify_payload, headers=headers)
        if response.status_code != 200:
            print(f"Payment verification failed: {response.text}")
            sys.exit(1)
            
        verify_data = response.json()
        ticket_id = verify_data.get("ticket_id")
        
        if not ticket_id:
            print("Ticket ID was not returned in payment verification response!")
            sys.exit(1)
            
        print(f"Ticket generated successfully! ID: {ticket_id}")
        
        # 4. Fetch Ticket Data
        print("Testing Fetch Ticket...")
        response = client.get(f"/api/tickets/{ticket_id}", headers=headers)
        if response.status_code != 200:
            print(f"Fetch ticket failed: {response.text}")
            sys.exit(1)
            
        ticket_data = response.json()
        print(f"Ticket fetched: {ticket_data['ticket_code']}")
        
        # 5. Fetch Ticket QR Image
        print("Testing Fetch QR Image...")
        response = client.get(f"/api/tickets/{ticket_id}/qr", headers=headers)
        if response.status_code != 200:
            print(f"Fetch QR failed: {response.status_code}")
            sys.exit(1)
            
        print("QR Code image successfully fetched!")
        print("Ticket and QR generation testing completed successfully!")
        
    finally:
        # Cleanup
        ticket = db.query(Ticket).filter(Ticket.registration_id == test_reg.id).first()
        if ticket:
            # optionally delete physical file
            # file_path = Path(settings.static_dir) / ...
            db.delete(ticket)
            
        db.query(Payment).filter(Payment.registration_id == test_reg.id).delete()
        db.delete(test_reg)
        db.delete(test_event)
        db.delete(test_user)
        db.commit()
        db.close()

if __name__ == "__main__":
    test_tickets()
