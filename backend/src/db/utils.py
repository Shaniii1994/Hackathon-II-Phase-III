"""
Database utility functions for common operations.

This module provides helper functions for database operations
optimized for Neon Serverless PostgreSQL.
"""

from sqlmodel import Session, select
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .connection import engine
from ..models.user import User
from ..models.task import Task

logger = logging.getLogger(__name__)


# User Operations
def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """
    Get user by email address.

    Uses indexed email column for fast lookup.

    Args:
        session: Database session
        email: User's email address

    Returns:
        User object if found, None otherwise
    """
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    """
    Get user by ID.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        User object if found, None otherwise
    """
    return session.get(User, user_id)


def create_user(session: Session, email: str, password_hash: str) -> User:
    """
    Create a new user.

    Args:
        session: Database session
        email: User's email address
        password_hash: Hashed password

    Returns:
        Created User object

    Raises:
        Exception: If user with email already exists
    """
    try:
        user = User(email=email, password_hash=password_hash)
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"User created: {user.id}")
        return user
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create user: {e}")
        raise


# Task Operations
def get_user_tasks(
    session: Session,
    user_id: int,
    is_complete: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Task]:
    """
    Get tasks for a user with optional filtering.

    Uses composite index (user_id, is_complete, due_date) for optimal performance.

    Args:
        session: Database session
        user_id: User's ID
        is_complete: Filter by completion status (None = all tasks)
        limit: Maximum number of tasks to return
        offset: Number of tasks to skip (for pagination)

    Returns:
        List of Task objects
    """
    statement = select(Task).where(Task.user_id == user_id)

    if is_complete is not None:
        statement = statement.where(Task.is_complete == is_complete)

    # Order by due_date (nulls last), then by created_at
    statement = statement.order_by(
        Task.due_date.asc().nullslast(),
        Task.created_at.desc()
    )

    statement = statement.offset(offset).limit(limit)

    return session.exec(statement).all()


def get_task_by_id(session: Session, task_id: int, user_id: int) -> Optional[Task]:
    """
    Get task by ID, ensuring it belongs to the user.

    Args:
        session: Database session
        task_id: Task's ID
        user_id: User's ID (for authorization)

    Returns:
        Task object if found and belongs to user, None otherwise
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    return session.exec(statement).first()


def create_task(
    session: Session,
    user_id: int,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> Task:
    """
    Create a new task for a user.

    Args:
        session: Database session
        user_id: User's ID
        title: Task title
        description: Task description (optional)
        due_date: Task due date (optional)

    Returns:
        Created Task object

    Raises:
        Exception: If task creation fails
    """
    try:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Task created: {task.id} for user {user_id}")
        return task
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create task: {e}")
        raise


def update_task(
    session: Session,
    task: Task,
    **kwargs
) -> Task:
    """
    Update task fields.

    The updated_at timestamp will be automatically updated.

    Args:
        session: Database session
        task: Task object to update
        **kwargs: Fields to update (title, description, due_date, is_complete)

    Returns:
        Updated Task object

    Raises:
        Exception: If update fails
    """
    try:
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        session.add(task)
        session.commit()
        session.refresh(task)
        logger.info(f"Task updated: {task.id}")
        return task
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to update task: {e}")
        raise


def delete_task(session: Session, task: Task) -> None:
    """
    Delete a task.

    Args:
        session: Database session
        task: Task object to delete

    Raises:
        Exception: If deletion fails
    """
    try:
        session.delete(task)
        session.commit()
        logger.info(f"Task deleted: {task.id}")
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to delete task: {e}")
        raise


def toggle_task_completion(session: Session, task: Task) -> Task:
    """
    Toggle task completion status.

    Args:
        session: Database session
        task: Task object to toggle

    Returns:
        Updated Task object
    """
    task.is_complete = not task.is_complete
    return update_task(session, task)


def get_task_statistics(session: Session, user_id: int) -> Dict[str, Any]:
    """
    Get task statistics for a user.

    Args:
        session: Database session
        user_id: User's ID

    Returns:
        Dictionary with task statistics
    """
    all_tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()

    completed = sum(1 for task in all_tasks if task.is_complete)
    pending = len(all_tasks) - completed

    overdue = sum(
        1 for task in all_tasks
        if not task.is_complete and task.due_date and task.due_date < datetime.now().date()
    )

    return {
        "total": len(all_tasks),
        "completed": completed,
        "pending": pending,
        "overdue": overdue,
        "completion_rate": (completed / len(all_tasks) * 100) if all_tasks else 0
    }
