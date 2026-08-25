import sys
import os
import random
import string

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.auth.security import get_password_hash

client = TestClient(app)
db = SessionLocal()

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def test_p1():
    print("Testing P1 Features...")
    
    # Setup test user
    email = f"user_{random_string()}@example.com"
    password = "password123"
    user = User(name="Test User", email=email, password_hash=get_password_hash(password), role="USER")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Login
    token = client.post("/api/auth/login", data={"username": email, "password": password}).json()["access_token"]
    
    # Create Event (as admin - need to create admin or just mock it)
    admin_email = f"admin_{random_string()}@example.com"
    admin = User(name="Admin", email=admin_email, password_hash=get_password_hash(password), role="ADMIN")
    db.add(admin)
    db.commit()
    
    admin_token = client.post("/api/auth/login", data={"username": admin_email, "password": password}).json()["access_token"]
    
    event_res = client.post("/api/events", json={
        "title": "Feedback Event",
        "slug": f"fb-evt-{random_string()}",
        "description": "Desc",
        "venue": "Virtual",
        "event_date": "2030-01-01",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "capacity": 10,
        "ticket_price": 0.0,
        "status": "PUBLISHED"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    event_id = event_res.json()["id"]
    
    # Register
    reg_res = client.post("/api/registrations", json={"event_id": event_id}, headers={"Authorization": f"Bearer {token}"})
    reg_id = reg_res.json()["id"]
    
    # Submit Feedback
    fb_res = client.post("/api/feedback", json={
        "registration_id": reg_id,
        "rating": 5,
        "comment": "This event was absolutely amazing and life-changing!"
    }, headers={"Authorization": f"Bearer {token}"})
    
    print(fb_res.json())
    assert fb_res.status_code == 201
    
    data = fb_res.json()
    assert data["sentiment"] == "POSITIVE"
    assert data["sentiment_score"] > 0
    print("✅ Feedback & Sentiment Analysis passed!")

if __name__ == "__main__":
    test_p1()
