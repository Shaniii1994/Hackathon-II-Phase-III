import asyncio
import sys
from sqlmodel import Session
from src.db.connection import get_session_context
from src.models.user import UserCreate
from src.services.user_service import create_user

async def test_registration():
    print("Testing user registration...")
    
    # Create test user data
    user_data = UserCreate(
        email="test@example.com",
        password="TestPass123!"
    )
    
    # Get a session
    async with get_session_context() as session:
        try:
            print("Attempting to create user...")
            user = await create_user(session, user_data)
            print(f"User created successfully: {user.id}, {user.email}")
        except Exception as e:
            print(f"Error creating user: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_registration())