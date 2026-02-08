from sqlmodel import Session, select
from datetime import datetime
from typing import List
import logging
from ..models.task import Task, TaskCreate, TaskUpdate
from ..core.exceptions import NotFoundError, ForbiddenError

logger = logging.getLogger(__name__)


async def create_task(session: Session, task_data: TaskCreate, user_id: int) -> Task:
    """
    Create a new task for a user.

    Args:
        session: Database session
        task_data: Task creation data
        user_id: ID of the user creating the task

    Returns:
        Created task

    Raises:
        ValidationError: If task data is invalid
    """
    task = Task(
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date,
        user_id=user_id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    logger.info(f"Created task {task.id} for user {user_id}")
    return task


async def get_tasks(session: Session, user_id: int, include_completed: bool = True, limit: int = 50, offset: int = 0) -> List[Task]:
    """
    Get tasks for a user with optional filtering, ordered by creation date (newest first).

    Args:
        session: Database session
        user_id: ID of the user
        include_completed: Whether to include completed tasks (default: True)
        limit: Maximum number of tasks to return (default: 50)
        offset: Number of tasks to skip (default: 0)

    Returns:
        List of tasks
    """
    statement = select(Task).where(Task.user_id == user_id)
    
    # Apply completion filter if needed
    if not include_completed:
        statement = statement.where(Task.is_complete == False)
    
    # Order by creation date (newest first) and apply limits
    statement = statement.order_by(Task.created_at.desc()).offset(offset).limit(limit)
    
    tasks = session.exec(statement).all()
    logger.info(f"Retrieved {len(tasks)} tasks for user {user_id} with filters: include_completed={include_completed}, limit={limit}, offset={offset}")
    return list(tasks)


async def get_task_by_id(session: Session, task_id: int, user_id: int) -> Task:
    """
    Get a specific task by ID with ownership verification.

    Args:
        session: Database session
        task_id: ID of the task
        user_id: ID of the user

    Returns:
        Task if found and owned by user

    Raises:
        NotFoundError: If task not found
        ForbiddenError: If task doesn't belong to user
    """
    task = session.get(Task, task_id)

    if not task:
        logger.warning(f"Task {task_id} not found")
        raise NotFoundError(f"Task with id {task_id} not found")

    if task.user_id != user_id:
        logger.warning(f"User {user_id} attempted to access task {task_id} owned by user {task.user_id}")
        raise ForbiddenError("You don't have permission to access this task")

    return task


async def update_task(session: Session, task_id: int, task_data: TaskUpdate, user_id: int) -> Task:
    """
    Update a task with ownership verification.

    Args:
        session: Database session
        task_id: ID of the task to update
        task_data: Task update data (only provided fields will be updated)
        user_id: ID of the user

    Returns:
        Updated task

    Raises:
        NotFoundError: If task not found
        ForbiddenError: If task doesn't belong to user
    """
    task = await get_task_by_id(session, task_id, user_id)

    # Update only provided fields (partial update)
    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Always update the timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    logger.info(f"Updated task {task_id} for user {user_id}")
    return task


async def delete_task(session: Session, task_id: int, user_id: int) -> None:
    """
    Delete a task with ownership verification.

    Args:
        session: Database session
        task_id: ID of the task to delete
        user_id: ID of the user

    Raises:
        NotFoundError: If task not found
        ForbiddenError: If task doesn't belong to user
    """
    task = await get_task_by_id(session, task_id, user_id)
    session.delete(task)
    session.commit()
    logger.info(f"Deleted task {task_id} for user {user_id}")


async def toggle_complete(session: Session, task_id: int, user_id: int) -> Task:
    """
    Toggle task completion status with ownership verification.

    Args:
        session: Database session
        task_id: ID of the task
        user_id: ID of the user

    Returns:
        Updated task with toggled completion status

    Raises:
        NotFoundError: If task not found
        ForbiddenError: If task doesn't belong to user
    """
    task = await get_task_by_id(session, task_id, user_id)
    task.is_complete = not task.is_complete
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)
    logger.info(f"Toggled task {task_id} completion to {task.is_complete} for user {user_id}")
    return task
