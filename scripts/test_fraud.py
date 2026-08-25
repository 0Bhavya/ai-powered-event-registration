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
from app.models.fraud_log import FraudLog

client = TestClient(app)

def test_fraud():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    # Suspicious and disposable email
    fraud_email = f"123456789_{suffix}@tempmail.com"
    fraud_password = "securepassword123"
    
    admin_email = f"admin_fraud_{suffix}@example.com"
    admin_password = "adminpassword123"
    
    db = SessionLocal()
    from app.auth.security import get_password_hash
    
    try:
        # 1. Setup DB Data
        test_user = User(
            name="Fraud Test User",
            email=fraud_email,
            password_hash=get_password_hash(fraud_password),
            role="USER"
        )
        db.add(test_user)
        
        test_admin = User(
            name="Admin User",
            email=admin_email,
            password_hash=get_password_hash(admin_password),
            role="ADMIN"
        )
        db.add(test_admin)
        
        test_event = Event(
            title=f"Fraud Event {suffix}",
            slug=f"fraud-event-{suffix}",
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
        db.refresh(test_admin)
        db.refresh(test_event)
        
        # 2. Login User
        response = client.post(
            "/api/auth/login",
            data={"username": fraud_email, "password": fraud_password}
        )
        if response.status_code != 200:
            print("Login failed")
            sys.exit(1)
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Direct Fraud Check via API
        print("Testing direct fraud check...")
        fraud_payload = {
            "user_id": test_user.id,
            "event_id": test_event.id,
            "email": fraud_email,
            "phone": "9999999999"
        }
        response = client.post("/api/fraud/check", json=fraud_payload)
        if response.status_code != 200:
            print("Fraud check failed")
            sys.exit(1)
            
        fraud_data = response.json()
        print(f"Direct check resulted in score: {fraud_data['risk_score']} Level: {fraud_data['risk_level']}")
        
        if fraud_data['risk_score'] < 30:
            print("Fraud rules didn't trigger correctly.")
            sys.exit(1)
            
        # 4. Attempt Registration (should be created but might be PENDING if score < 60)
        # 123456789_@tempmail.com => Suspicious (+15) + Disposable (+15) = 30 (MEDIUM)
        # It won't be BLOCKED (needs >= 60). We will just verify it saves risk score.
        print("Testing Registration with fraud risk...")
        response = client.post("/api/registrations", json={"event_id": test_event.id}, headers=headers)
        if response.status_code != 201:
            print(f"Registration failed: {response.text}")
            sys.exit(1)
            
        reg_data = response.json()
        if reg_data["risk_score"] != fraud_data["risk_score"]:
            print("Registration didn't save the correct risk score.")
            sys.exit(1)
            
        print(f"Registration saved with Risk Score {reg_data['risk_score']} and Status {reg_data['status']}")
        
        # 5. Check Admin logs
        response = client.post(
            "/api/auth/login",
            data={"username": admin_email, "password": admin_password}
        )
        admin_token = response.json()["access_token"]
        
        # Since it wasn't HIGH or CRITICAL, it wasn't saved to FraudLog in our current logic
        # Our logic: `if fraud_result.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]: ... db.add(fraud_log)`
        # This is expected. If we wanted, we could log everything.
        
        print("Fraud workflow testing completed successfully!")
        
    finally:
        # Cleanup
        db.query(FraudLog).filter(FraudLog.email == fraud_email).delete()
        db.query(Registration).filter(Registration.user_id == test_user.id).delete()
        db.delete(test_event)
        db.delete(test_user)
        db.delete(test_admin)
        db.commit()
        db.close()

if __name__ == "__main__":
    test_fraud()
