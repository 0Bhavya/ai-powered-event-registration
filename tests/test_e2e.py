import pytest
from fastapi.testclient import TestClient
import random
import string
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User
from app.auth.security import get_password_hash

client = TestClient(app)

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

@pytest.fixture(scope="module")
def db():
    db = SessionLocal()
    yield db
    db.close()

def test_full_e2e_workflow(db):
    # 1. Create Users
    user_email = f"user_{random_string()}@example.com"
    password = "password123"
    user = User(name="Test User", email=user_email, password_hash=get_password_hash(password), role="USER")
    db.add(user)
    
    admin_email = f"admin_{random_string()}@example.com"
    admin = User(name="Admin", email=admin_email, password_hash=get_password_hash(password), role="ADMIN")
    db.add(admin)
    db.commit()
    db.refresh(user)
    db.refresh(admin)

    # 2. Login
    user_token = client.post("/api/auth/login", data={"username": user_email, "password": password}).json()["access_token"]
    admin_token = client.post("/api/auth/login", data={"username": admin_email, "password": password}).json()["access_token"]

    # 3. Create Event
    event_res = client.post("/api/events", json={
        "title": "E2E Test Event",
        "slug": f"e2e-evt-{random_string()}",
        "description": "Desc",
        "venue": "Virtual",
        "event_date": "2030-01-01",
        "start_time": "10:00:00",
        "end_time": "12:00:00",
        "capacity": 10,
        "ticket_price": 0.0,
        "status": "PUBLISHED"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert event_res.status_code == 201
    event_id = event_res.json()["id"]

    # 4. Register
    reg_res = client.post("/api/registrations", json={"event_id": event_id}, headers={"Authorization": f"Bearer {user_token}"})
    assert reg_res.status_code == 201
    reg_id = reg_res.json()["id"]

    # 5. Submit Feedback
    fb_res = client.post("/api/feedback", json={
        "registration_id": reg_id,
        "rating": 5,
        "comment": "This event was absolutely amazing and life-changing!"
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert fb_res.status_code == 201
    
    data = fb_res.json()
    assert data["sentiment"] == "POSITIVE"
    assert data["sentiment_score"] > 0
    
    # 6. Admin Stats & Audit
    stats_res = client.get("/api/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert stats_res.status_code == 200
    
    audit_res = client.get("/api/audit", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_res.status_code == 200
