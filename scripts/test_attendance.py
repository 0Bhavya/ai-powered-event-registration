import sys
import os
import random
import string
from datetime import date, time
import uuid

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.models.event import Event, EventStatus
from app.models.registration import Registration, RegistrationStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.attendance import Attendance

client = TestClient(app)

def test_attendance():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    staff_email = f"staff_{suffix}@example.com"
    staff_password = "securestaff123"
    
    user_email = f"user_att_{suffix}@example.com"
    
    db = SessionLocal()
    from app.auth.security import get_password_hash
    
    try:
        # 1. Setup DB Data
        test_staff = User(
            name="Staff User",
            email=staff_email,
            password_hash=get_password_hash(staff_password),
            role="STAFF"
        )
        db.add(test_staff)
        
        test_user = User(
            name="Att Test User",
            email=user_email,
            password_hash="doesn't_matter",
            role="USER"
        )
        db.add(test_user)
        
        test_event = Event(
            title=f"Att Event {suffix}",
            slug=f"att-event-{suffix}",
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
        db.refresh(test_staff)
        db.refresh(test_user)
        db.refresh(test_event)
        
        test_reg = Registration(
            registration_code=f"REG-ATT-{suffix}",
            user_id=test_user.id,
            event_id=test_event.id,
            status=RegistrationStatus.CONFIRMED
        )
        db.add(test_reg)
        db.commit()
        db.refresh(test_reg)
        
        qr_token = str(uuid.uuid4())
        test_ticket = Ticket(
            registration_id=test_reg.id,
            ticket_code=f"TKT-ATT-{suffix}",
            qr_token=qr_token,
            qr_image_path="/static/images/qr/fake.png",
            status=TicketStatus.VALID
        )
        db.add(test_ticket)
        db.commit()
        db.refresh(test_ticket)
        
        # 2. Login Staff
        response = client.post(
            "/api/auth/login",
            data={"username": staff_email, "password": staff_password}
        )
        if response.status_code != 200:
            print("Staff login failed!")
            sys.exit(1)
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Scan valid ticket
        print("Testing valid scan...")
        response = client.post(
            "/api/attendance/scan", 
            json={"qr_token": qr_token}, 
            headers=headers
        )
        
        if response.status_code != 200 or not response.json()["success"]:
            print(f"Scan failed: {response.text}")
            sys.exit(1)
            
        print("First scan successful!")
        
        # 4. Double scan (Already Checked In)
        print("Testing double scan...")
        response = client.post(
            "/api/attendance/scan", 
            json={"qr_token": qr_token}, 
            headers=headers
        )
        
        if response.status_code != 200 or response.json()["success"]:
            print(f"Double scan didn't return failure state: {response.text}")
            sys.exit(1)
            
        print(f"Double scan correctly reported: {response.json()['message']}")
        
        # 5. Invalid scan
        print("Testing invalid scan...")
        response = client.post(
            "/api/attendance/scan", 
            json={"qr_token": "invalid_fake_token"}, 
            headers=headers
        )
        
        if response.status_code != 200 or response.json()["success"]:
            print(f"Invalid scan didn't return failure state: {response.text}")
            sys.exit(1)
            
        print(f"Invalid scan correctly reported: {response.json()['message']}")
        print("Attendance scanner testing completed successfully!")
        
    finally:
        # Cleanup
        db.query(Attendance).filter(Attendance.ticket_id == test_ticket.id).delete()
        db.delete(test_ticket)
        db.delete(test_reg)
        db.delete(test_event)
        db.delete(test_user)
        db.delete(test_staff)
        db.commit()
        db.close()

if __name__ == "__main__":
    test_attendance()
