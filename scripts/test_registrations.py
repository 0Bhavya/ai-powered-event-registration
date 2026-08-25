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
from app.models.registration import Registration

client = TestClient(app)

def test_registrations():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    user_email = f"user_reg_{suffix}@example.com"
    user_password = "securepassword123"
    
    db = SessionLocal()
    from app.auth.security import get_password_hash
    
    try:
        # 1. Setup DB Data
        test_user = User(
            name="Reg Test User",
            email=user_email,
            password_hash=get_password_hash(user_password),
            role="USER"
        )
        db.add(test_user)
        
        test_event = Event(
            title=f"Reg Event {suffix}",
            slug=f"reg-event-{suffix}",
            venue="Online",
            event_date=date(2026, 12, 1),
            start_time=time(10, 0),
            end_time=time(12, 0),
            capacity=10,
            available_seats=10,
            status=EventStatus.PUBLISHED
        )
        db.add(test_event)
        db.commit()
        db.refresh(test_user)
        db.refresh(test_event)
        
        # 2. Login User
        response = client.post(
            "/api/auth/login",
            data={"username": user_email, "password": user_password}
        )
        if response.status_code != 200:
            print("Login failed")
            sys.exit(1)
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Check availability
        print("Testing seat check...")
        response = client.post("/api/registrations/check", json={"event_id": test_event.id})
        if response.status_code != 200 or not response.json()["is_available"]:
            print(f"Check availability failed: {response.text}")
            sys.exit(1)
            
        print("Seat check successful!")
        
        # 4. Register
        print("Testing registration creation...")
        response = client.post("/api/registrations", json={"event_id": test_event.id}, headers=headers)
        if response.status_code != 201:
            print(f"Registration failed: {response.text}")
            sys.exit(1)
            
        reg_id = response.json()["id"]
        print(f"Registration created! ID: {reg_id}")
        
        # 5. Check Seat decremented
        db.refresh(test_event)
        if test_event.available_seats != 9:
            print(f"Available seats didn't decrement! Is {test_event.available_seats}")
            sys.exit(1)
            
        # 6. Try duplicate registration
        print("Testing duplicate registration prevention...")
        response = client.post("/api/registrations", json={"event_id": test_event.id}, headers=headers)
        if response.status_code != 400:
            print("Duplicate registration was allowed!")
            sys.exit(1)
        print("Duplicate prevented successfully!")
            
        # 7. Get my registrations
        print("Testing get my registrations...")
        response = client.get("/api/registrations/my-registrations", headers=headers)
        if response.status_code != 200 or len(response.json()) != 1:
            print("Failed to get my registrations")
            sys.exit(1)
            
        print("Registration workflow testing completed successfully!")
        
    finally:
        # Cleanup
        db.query(Registration).filter(Registration.user_id == test_user.id).delete()
        db.delete(test_event)
        db.delete(test_user)
        db.commit()
        db.close()

if __name__ == "__main__":
    test_registrations()
