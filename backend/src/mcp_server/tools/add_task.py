"""
MCP Tool Handler: add_task

This module implements the add_task MCP tool that allows AI agents to create
new tasks in the database for authenticated users.
"""

import logging
from sqlmodel import Session
from ...services.task_service import create_task
from ...models.mcp_models import AddTaskRequest, AddTaskResponse
from ...models.task import TaskCreate


logger = logging.getLogger(__name__)


async def add_task_handler(request: AddTaskRequest, session: Session) -> AddTaskResponse:
    """
    Handle the add_task MCP tool request.
    
    Args:
        request: The add_task request containing user_id, title, description, and due_date
        session: The database session
        
    Returns:
        AddTaskResponse with success status and task_id or error message
    """
    try:
        # Create a TaskCreate object from the request
        task_create_data = TaskCreate(
            title=request.title,
            description=request.description,
            due_date=request.due_date.date() if request.due_date else None
        )
        
        # Use the existing service to create the task
        task = await create_task(session, task_create_data, request.user_id)
        
        # Return success response with the new task ID
        return AddTaskResponse(
            success=True,
            task_id=task.id
        )
    except Exception as e:
        logger.error(f"Error in add_task_handler: {str(e)}")
        return AddTaskResponse(
            success=False,
            error_message=str(e)
        )