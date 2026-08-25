import sys
import os
import random
import string

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User

client = TestClient(app)

def test_events():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    admin_email = f"admin_test_{suffix}@example.com"
    admin_password = "secureadmin123"
    
    # 1. Create Admin user manually in DB because our register endpoint creates normal USERs
    db = SessionLocal()
    from app.auth.security import get_password_hash
    admin_user = User(
        name="Admin User",
        email=admin_email,
        password_hash=get_password_hash(admin_password),
        role="ADMIN"
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    try:
        # 2. Login
        response = client.post(
            "/api/auth/login",
            data={"username": admin_email, "password": admin_password}
        )
        if response.status_code != 200:
            print(f"Admin Login failed: {response.text}")
            sys.exit(1)
            
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. Create Event
        print("Testing Event Creation...")
        event_payload = {
            "title": "AI Summit 2026",
            "slug": f"ai-summit-2026-{suffix}",
            "description": "The biggest AI conference.",
            "venue": "Tech Park",
            "event_date": "2026-10-15",
            "start_time": "09:00:00",
            "end_time": "18:00:00",
            "capacity": 500,
            "ticket_price": 99.99,
            "status": "PUBLISHED"
        }
        
        response = client.post("/api/events", json=event_payload, headers=headers)
        if response.status_code != 201:
            print(f"Event creation failed: {response.status_code} {response.text}")
            sys.exit(1)
            
        event_data = response.json()
        event_id = event_data["id"]
        print(f"Event Created successfully! ID: {event_id}")
        
        # 4. Get Event
        print("Testing Get Event...")
        response = client.get(f"/api/events/{event_id}")
        if response.status_code != 200 or response.json()["title"] != "AI Summit 2026":
            print("Get event failed!")
            sys.exit(1)
            
        # 5. List Events
        print("Testing List Events...")
        response = client.get("/api/events")
        if response.status_code != 200 or len(response.json()) == 0:
            print("List events failed!")
            sys.exit(1)
            
        # 6. Update Event
        print("Testing Update Event...")
        response = client.put(
            f"/api/events/{event_id}",
            json={"capacity": 600, "ticket_price": 149.99},
            headers=headers
        )
        if response.status_code != 200 or response.json()["capacity"] != 600:
            print(f"Update event failed: {response.text}")
            sys.exit(1)
        print("Event updated successfully!")
            
        # 7. Delete Event
        print("Testing Delete Event...")
        response = client.delete(f"/api/events/{event_id}", headers=headers)
        if response.status_code != 204:
            print("Delete event failed!")
            sys.exit(1)
            
        # Verify deletion
        response = client.get(f"/api/events/{event_id}")
        if response.status_code != 404:
            print("Event was not deleted!")
            sys.exit(1)
            
        print("Event deleted successfully!")
        print("Event management flow testing completed successfully.")
        
    finally:
        # Cleanup
        db.delete(admin_user)
        db.commit()
        db.close()

if __name__ == "__main__":
    test_events()
