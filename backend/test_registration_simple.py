import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from sqlmodel import create_engine, Session
from src.core.config import settings
from src.models.user import UserCreate
from src.services.user_service import create_user_sync
from src.db.connection import engine

def test_registration():
    print("Testing user registration...")
    
    # Create test user data
    user_data = UserCreate(
        email="test@example.com",
        password="TestPass123!"
    )
    
    try:
        # Create a session manually
        with Session(engine) as session:
            print("Attempting to create user...")
            user = create_user_sync(session, user_data)
            print(f"User created successfully: {user.id}, {user.email}")
    except Exception as e:
        print(f"Error creating user: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_registration()