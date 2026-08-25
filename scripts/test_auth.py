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

def test_auth():
    # Random suffix to avoid unique constraint issues if ran multiple times
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    test_email = f"auth_test_{suffix}@example.com"
    test_password = "securepassword123"
    
    print(f"Testing Registration for {test_email}...")
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Auth Test User",
            "email": test_email,
            "password": test_password,
            "phone": "1234567890",
            "college": "Test University"
        }
    )
    if response.status_code != 201:
        print(f"Registration failed: {response.status_code} {response.text}")
        sys.exit(1)
    
    print("Registration successful!")
    
    print("Testing Login...")
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_email,
            "password": test_password
        }
    )
    if response.status_code != 200:
        print(f"Login failed: {response.status_code} {response.text}")
        sys.exit(1)
        
    print("Login successful!")
    token_data = response.json()
    access_token = token_data["access_token"]
    
    print("Testing /me endpoint...")
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    if response.status_code != 200:
        print(f"/me endpoint failed: {response.status_code} {response.text}")
        sys.exit(1)
        
    user_data = response.json()
    print(f"Successfully retrieved user profile: {user_data['name']} ({user_data['email']})")
    print("Auth flow testing completed successfully.")
    
    # Cleanup
    db = SessionLocal()
    user = db.query(User).filter(User.email == test_email).first()
    if user:
        db.delete(user)
        db.commit()
    db.close()

if __name__ == "__main__":
    test_auth()
