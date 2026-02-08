from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import List
import logging
from ..db.connection import get_session
from ..models.task import TaskCreate, TaskUpdate, TaskResponse
from ..services.task_service import (
    create_task,
    get_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    toggle_complete,
)
from ..middleware.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user. Task title is required.",
    responses={
        201: {"description": "Task created successfully"},
        401: {"description": "Invalid or missing authentication token"},
        422: {"description": "Validation error - invalid task data"},
    },
)
async def create_task_endpoint(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user),
):
    """
    Create a new task for the authenticated user.

    - **title**: Task title (required, 1-200 characters)
    - **description**: Optional detailed description (max 2000 characters)
    - **due_date**: Optional due date in YYYY-MM-DD format

    Requires JWT authentication via Authorization: Bearer <token> header.
    """
    logger.info(f"User {current_user_id} creating new task: {task_data.title}")
    task = await create_task(session, task_data, current_user_id)
    logger.info(f"Task {task.id} created successfully for user {current_user_id}")
    return TaskResponse.model_validate(task)


@router.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="Get all tasks",
    description="Retrieve all tasks for the authenticated user, ordered by creation date (newest first).",
    responses={
        200: {"description": "List of tasks retrieved successfully"},
        401: {"description": "Invalid or missing authentication token"},
    },
)
async def get_tasks_endpoint(
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user),
):
    """
    Get all tasks for the authenticated user.

    Returns tasks ordered by creation date (newest first).
    Requires JWT authentication via Authorization: Bearer <token> header.
    """
    logger.info(f"User {current_user_id} retrieving all tasks")
    tasks = await get_tasks(session, current_user_id, include_completed=True)
    logger.info(f"Retrieved {len(tasks)} tasks for user {current_user_id}")
    return [TaskResponse.model_validate(task) for task in tasks]


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a specific task",
    description="Retrieve a specific task by ID. User must own the task.",
    responses={
        200: {"description": "Task retrieved successfully"},
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Task belongs to another user"},
        404: {"description": "Task not found"},
    },
)
async def get_task_endpoint(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user),
):
    """
    Get a specific task by ID.

    - **task_id**: ID of the task to retrieve

    Requires JWT authentication via Authorization: Bearer <token> header.
    User must own the task.
    """
    logger.info(f"User {current_user_id} retrieving task {task_id}")
    task = await get_task_by_id(session, task_id, current_user_id)
    return TaskResponse.model_validate(task)


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update task details. Only provided fields will be updated.",
    responses={
        200: {"description": "Task updated successfully"},
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Task belongs to another user"},
        404: {"description": "Task not found"},
        422: {"description": "Validation error - invalid task data"},
    },
)
async def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user),
):
    """
    Update a task. Only provided fields will be updated.

    - **task_id**: ID of the task to update
    - **title**: Optional new title (1-200 characters)
    - **description**: Optional new description (max 2000 characters)
    - **due_date**: Optional new due date in YYYY-MM-DD format
    - **is_complete**: Optional completion status

    Requires JWT authentication via Authorization: Bearer <token> header.
    User must own the task.
    """
    logger.info(f"User {current_user_id} updating task {task_id}")
    task = await update_task(session, task_id, task_data, current_user_id)
    logger.info(f"Task {task_id} updated successfully")
    return TaskResponse.model_validate(task)


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task. This action cannot be undone.",
    responses={
        204: {"description": "Task deleted successfully"},
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Task belongs to another user"},
        404: {"description": "Task not found"},
    },
)
async def delete_task_endpoint(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user),
):
    """
    Delete a task permanently.

    - **task_id**: ID of the task to delete

    Requires JWT authentication via Authorization: Bearer <token> header.
    User must own the task. This action cannot be undone.
    """
    logger.info(f"User {current_user_id} deleting task {task_id}")
    await delete_task(session, task_id, current_user_id)
    logger.info(f"Task {task_id} deleted successfully")
    return None


@router.patch(
    "/tasks/{task_id}/complete",
    response_model=TaskResponse,
    summary="Toggle task completion",
    description="Toggle the completion status of a task (complete ↔ incomplete).",
    responses={
        200: {"description": "Task completion status toggled successfully"},
        401: {"description": "Invalid or missing authentication token"},
        403: {"description": "Task belongs to another user"},
        404: {"description": "Task not found"},
    },
)
async def toggle_complete_endpoint(
    task_id: int,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user),
):
    """
    Toggle task completion status.

    - **task_id**: ID of the task to toggle

    If task is complete, it will be marked incomplete.
    If task is incomplete, it will be marked complete.

    Requires JWT authentication via Authorization: Bearer <token> header.
    User must own the task.
    """
    logger.info(f"User {current_user_id} toggling completion for task {task_id}")
    task = await toggle_complete(session, task_id, current_user_id)
    logger.info(f"Task {task_id} completion toggled to {task.is_complete}")
    return TaskResponse.model_validate(task)
