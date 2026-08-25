import sys
import os

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.database.session import SessionLocal
from app.models.user import User

client = TestClient(app)
db = SessionLocal()

def test_p2p3():
    print("Testing P2 & P3 Features...")
    
    # Check stats endpoint
    stats_res = client.get("/api/stats")
    assert stats_res.status_code == 200
    print("✅ /api/stats OK:", stats_res.json())
    
    # Need an admin to test audit logs
    admin = db.query(User).filter(User.role == "ADMIN").first()
    if admin:
        token = client.post("/api/auth/login", data={"username": admin.email, "password": "password123"}).json()["access_token"]
        
        audit_res = client.get("/api/audit", headers={"Authorization": f"Bearer {token}"})
        assert audit_res.status_code == 200
        print("✅ /api/audit OK:", audit_res.json()[:2]) # print top 2
        
    print("Tests passed.")

if __name__ == "__main__":
    test_p2p3()
