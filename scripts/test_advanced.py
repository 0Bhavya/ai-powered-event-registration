import sys
import os
import random
import string
import uuid
from datetime import date, time

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.admin_audit_log import AdminAuditLog
from app.models.event import Event
from app.models.user import User
from app.auth.security import get_password_hash

client = TestClient(app)
db = SessionLocal()

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def setup_users():
    admin_email = f"admin_{random_string()}@example.com"
    staff_email = f"staff_{random_string()}@example.com"
    user_email = f"user_{random_string()}@example.com"
    password = "testpassword123"

    # Create admin
    admin = User(name="Admin", email=admin_email, password_hash=get_password_hash(password), role="ADMIN")
    # Create staff
    staff = User(name="Staff", email=staff_email, password_hash=get_password_hash(password), role="STAFF")
    # Create user
    user = User(name="User", email=user_email, password_hash=get_password_hash(password), role="USER")
    
    db.add_all([admin, staff, user])
    db.commit()

    return (
        {"email": admin_email, "password": password},
        {"email": staff_email, "password": password},
        {"email": user_email, "password": password}
    )

def test_advanced_features():
    print("Setting up users...")
    admin_creds, staff_creds, user_creds = setup_users()

    # Logins
    admin_token = client.post("/api/auth/login", data={"username": admin_creds["email"], "password": admin_creds["password"]}).json()["access_token"]
    staff_token = client.post("/api/auth/login", data={"username": staff_creds["email"], "password": staff_creds["password"]}).json()["access_token"]
    user_token = client.post("/api/auth/login", data={"username": user_creds["email"], "password": user_creds["password"]}).json()["access_token"]

    print("1. Testing Audit Logging for Event Creation...")
    event_data = {
        "title": "Advanced AI Summit",
        "slug": f"advanced-ai-{random_string()}",
        "description": "Summit",
        "venue": "Virtual",
        "event_date": str(date.today()),
        "start_time": str(time(10, 0)),
        "end_time": str(time(18, 0)),
        "capacity": 50,
        "ticket_price": 500.0,
        "status": "PUBLISHED"
    }
    res = client.post("/api/events", json=event_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 201
    event_id = res.json()["id"]

    # Verify audit log exists
    audit_log = db.query(AdminAuditLog).filter(
        AdminAuditLog.action == "CREATE_EVENT",
        AdminAuditLog.entity_id == event_id
    ).first()
    assert audit_log is not None
    print("✅ Audit log recorded for event creation.")

    print("2. Testing Registration, Notification Dispatch, and Fraud Detection...")
    # Using the persisted model should not crash
    reg_res = client.post("/api/registrations", json={"event_id": event_id}, headers={"Authorization": f"Bearer {user_token}"})
    if reg_res.status_code != 201:
        print("Registration Failed:", reg_res.text)
    assert reg_res.status_code == 201
    reg_id = reg_res.json()["id"]
    print("✅ Registration passed ML fraud detection (model loaded).")

    print("3. Testing Payment and Notifications...")
    order_res = client.post("/api/payments/create-order", json={"registration_id": reg_id}, headers={"Authorization": f"Bearer {user_token}"})
    order_id = order_res.json()["order_id"]
    
    verify_data = {
        "razorpay_order_id": order_id,
        "razorpay_payment_id": "pay_demo_" + random_string(),
        "razorpay_signature": "demo_sig_valid"
    }
    
    verify_res = client.post("/api/payments/verify", json=verify_data, headers={"Authorization": f"Bearer {user_token}"})
    assert verify_res.status_code == 200
    ticket_id = verify_res.json()["ticket_id"]
    print("✅ Payment verified (Check console logs for mock email dispatch).")

    print("4. Testing Attendance Scanner Audit Log...")
    # Fetch ticket to get qr_token
    from app.models.ticket import Ticket
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    
    scan_res = client.post("/api/attendance/scan", json={"qr_token": ticket.qr_token}, headers={"Authorization": f"Bearer {staff_token}"})
    assert scan_res.status_code == 200
    assert scan_res.json()["success"] is True

    # Verify scan audit log
    scan_log = db.query(AdminAuditLog).filter(
        AdminAuditLog.action == "SCAN_TICKET"
    ).order_by(AdminAuditLog.id.desc()).first()
    
    assert scan_log is not None
    assert scan_log.metadata_info["ticket_id"] == ticket_id
    print("✅ Audit log recorded for ticket scanning.")
    
    print("\n🎉 All advanced features verified successfully!")

if __name__ == "__main__":
    test_advanced_features()
