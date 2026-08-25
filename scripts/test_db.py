import sys
import os

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.session import SessionLocal
from app.models.user import User

def test_db():
    db = SessionLocal()
    try:
        # Create a test user
        test_user = User(
            name="Test User",
            email="test@example.com",
            password_hash="fakehash",
            role="USER"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"Successfully created user with ID: {test_user.id}")
        
        # Query the user
        queried_user = db.query(User).filter(User.email == "test@example.com").first()
        if queried_user:
            print(f"Successfully queried user: {queried_user.name}")
            
        # Clean up
        db.delete(test_user)
        db.commit()
        print("Successfully deleted test user. Database is working!")
        
    except Exception as e:
        print(f"Database test failed: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
