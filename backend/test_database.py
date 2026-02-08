"""
Database testing and verification script.

Run this script to verify database setup and test all operations.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlmodel import Session, select
from src.db.connection import engine, check_connection, close_connections
from src.db.init_db import init_db
from src.db.utils import (
    create_user, get_user_by_email, get_user_by_id,
    create_task, get_user_tasks, get_task_by_id,
    update_task, delete_task, toggle_task_completion,
    get_task_statistics
)
from src.models.user import User
from src.models.task import Task
from datetime import date, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test database connection."""
    print("\n" + "="*60)
    print("TEST 1: Database Connection")
    print("="*60)

    if check_connection():
        print("✅ Database connection successful")
        return True
    else:
        print("❌ Database connection failed")
        return False


def test_table_creation():
    """Test table creation."""
    print("\n" + "="*60)
    print("TEST 2: Table Creation")
    print("="*60)

    try:
        init_db()
        print("✅ Tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False


def test_indexes():
    """Test that indexes exist."""
    print("\n" + "="*60)
    print("TEST 3: Index Verification")
    print("="*60)

    try:
        with Session(engine) as session:
            # Check user indexes
            result = session.exec("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'user'
            """)
            user_indexes = [row[0] for row in result]

            print(f"User table indexes: {user_indexes}")

            if 'ix_user_email' in user_indexes:
                print("✅ User email index exists")
            else:
                print("⚠️  User email index missing")

            # Check task indexes
            result = session.exec("""
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = 'task'
            """)
            task_indexes = [row[0] for row in result]

            print(f"Task table indexes: {task_indexes}")

            if 'ix_task_user_id' in task_indexes:
                print("✅ Task user_id index exists")
            else:
                print("⚠️  Task user_id index missing")

            if 'idx_task_user_status_date' in task_indexes:
                print("✅ Task composite index exists")
            else:
                print("⚠️  Task composite index missing")

            return True
    except Exception as e:
        print(f"❌ Index verification failed: {e}")
        return False


def test_user_operations():
    """Test user CRUD operations."""
    print("\n" + "="*60)
    print("TEST 4: User Operations")
    print("="*60)

    try:
        with Session(engine) as session:
            # Create user
            test_email = "test_user@example.com"

            # Clean up if exists
            existing = get_user_by_email(session, test_email)
            if existing:
                session.delete(existing)
                session.commit()

            user = create_user(session, test_email, "hashed_password_123")
            print(f"✅ User created: ID={user.id}, Email={user.email}")

            # Get user by email
            found_user = get_user_by_email(session, test_email)
            if found_user and found_user.id == user.id:
                print("✅ User retrieved by email")
            else:
                print("❌ User retrieval by email failed")
                return False

            # Get user by ID
            found_user = get_user_by_id(session, user.id)
            if found_user and found_user.email == test_email:
                print("✅ User retrieved by ID")
            else:
                print("❌ User retrieval by ID failed")
                return False

            return user.id
    except Exception as e:
        print(f"❌ User operations failed: {e}")
        return False


def test_task_operations(user_id: int):
    """Test task CRUD operations."""
    print("\n" + "="*60)
    print("TEST 5: Task Operations")
    print("="*60)

    try:
        with Session(engine) as session:
            # Create tasks
            task1 = create_task(
                session,
                user_id=user_id,
                title="Test Task 1",
                description="First test task",
                due_date=date.today() + timedelta(days=1)
            )
            print(f"✅ Task 1 created: ID={task1.id}")

            task2 = create_task(
                session,
                user_id=user_id,
                title="Test Task 2",
                description="Second test task",
                due_date=date.today() + timedelta(days=7)
            )
            print(f"✅ Task 2 created: ID={task2.id}")

            task3 = create_task(
                session,
                user_id=user_id,
                title="Test Task 3 (No due date)",
                description="Third test task"
            )
            print(f"✅ Task 3 created: ID={task3.id}")

            # Get all user tasks
            tasks = get_user_tasks(session, user_id)
            if len(tasks) == 3:
                print(f"✅ Retrieved all tasks: {len(tasks)} tasks")
            else:
                print(f"❌ Expected 3 tasks, got {len(tasks)}")
                return False

            # Get task by ID
            found_task = get_task_by_id(session, task1.id, user_id)
            if found_task and found_task.title == "Test Task 1":
                print("✅ Task retrieved by ID")
            else:
                print("❌ Task retrieval by ID failed")
                return False

            # Update task
            updated_task = update_task(
                session,
                task1,
                title="Updated Task 1",
                is_complete=True
            )
            if updated_task.title == "Updated Task 1" and updated_task.is_complete:
                print("✅ Task updated successfully")
            else:
                print("❌ Task update failed")
                return False

            # Toggle completion
            toggled_task = toggle_task_completion(session, task2)
            if toggled_task.is_complete:
                print("✅ Task completion toggled")
            else:
                print("❌ Task toggle failed")
                return False

            # Get completed tasks
            completed_tasks = get_user_tasks(session, user_id, is_complete=True)
            if len(completed_tasks) == 2:
                print(f"✅ Retrieved completed tasks: {len(completed_tasks)}")
            else:
                print(f"❌ Expected 2 completed tasks, got {len(completed_tasks)}")

            # Get pending tasks
            pending_tasks = get_user_tasks(session, user_id, is_complete=False)
            if len(pending_tasks) == 1:
                print(f"✅ Retrieved pending tasks: {len(pending_tasks)}")
            else:
                print(f"❌ Expected 1 pending task, got {len(pending_tasks)}")

            # Get statistics
            stats = get_task_statistics(session, user_id)
            print(f"✅ Task statistics: {stats}")

            # Delete task
            delete_task(session, task3)
            remaining_tasks = get_user_tasks(session, user_id)
            if len(remaining_tasks) == 2:
                print("✅ Task deleted successfully")
            else:
                print(f"❌ Expected 2 tasks after deletion, got {len(remaining_tasks)}")
                return False

            return True
    except Exception as e:
        print(f"❌ Task operations failed: {e}")
        return False


def test_cascade_delete(user_id: int):
    """Test CASCADE DELETE on user deletion."""
    print("\n" + "="*60)
    print("TEST 6: CASCADE DELETE")
    print("="*60)

    try:
        with Session(engine) as session:
            # Get task count before deletion
            tasks_before = get_user_tasks(session, user_id)
            task_count = len(tasks_before)
            print(f"Tasks before user deletion: {task_count}")

            # Delete user
            user = get_user_by_id(session, user_id)
            if user:
                session.delete(user)
                session.commit()
                print(f"✅ User {user_id} deleted")

            # Check if tasks were deleted
            tasks_after = session.exec(
                select(Task).where(Task.user_id == user_id)
            ).all()

            if len(tasks_after) == 0:
                print("✅ CASCADE DELETE working: All user tasks deleted")
                return True
            else:
                print(f"❌ CASCADE DELETE failed: {len(tasks_after)} tasks remain")
                return False
    except Exception as e:
        print(f"❌ CASCADE DELETE test failed: {e}")
        return False


def test_connection_pool():
    """Test connection pool behavior."""
    print("\n" + "="*60)
    print("TEST 7: Connection Pool")
    print("="*60)

    try:
        # Get pool status
        pool = engine.pool
        print(f"Pool size: {pool.size()}")
        print(f"Checked out connections: {pool.checkedout()}")
        print(f"Overflow: {pool.overflow()}")
        print(f"Checked in connections: {pool.checkedin()}")

        # Test multiple concurrent sessions
        sessions = []
        for i in range(5):
            session = Session(engine)
            sessions.append(session)

        print(f"✅ Created 5 concurrent sessions")
        print(f"Checked out connections: {pool.checkedout()}")

        # Close sessions
        for session in sessions:
            session.close()

        print(f"✅ Closed all sessions")
        print(f"Checked out connections: {pool.checkedout()}")

        return True
    except Exception as e:
        print(f"❌ Connection pool test failed: {e}")
        return False


def run_all_tests():
    """Run all database tests."""
    print("\n" + "="*60)
    print("DATABASE VERIFICATION TESTS")
    print("="*60)

    results = []

    # Test 1: Connection
    results.append(("Connection", test_connection()))

    # Test 2: Table Creation
    results.append(("Table Creation", test_table_creation()))

    # Test 3: Indexes
    results.append(("Indexes", test_indexes()))

    # Test 4: User Operations
    user_id = test_user_operations()
    results.append(("User Operations", bool(user_id)))

    if user_id:
        # Test 5: Task Operations
        results.append(("Task Operations", test_task_operations(user_id)))

        # Test 6: CASCADE DELETE
        results.append(("CASCADE DELETE", test_cascade_delete(user_id)))

    # Test 7: Connection Pool
    results.append(("Connection Pool", test_connection_pool()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Database is properly configured.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")

    # Cleanup
    close_connections()

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
