"""
MCP Tool Handler: update_task

This module implements the update_task MCP tool that allows AI agents to update
task properties for authenticated users.
"""

import logging
from sqlmodel import Session
from ...services.task_service import update_task
from ...models.mcp_models import UpdateTaskRequest, UpdateTaskResponse
from ...models.task import TaskUpdate


logger = logging.getLogger(__name__)


async def update_task_handler(request: UpdateTaskRequest, session: Session) -> UpdateTaskResponse:
    """
    Handle the update_task MCP tool request.
    
    Args:
        request: The update_task request containing user_id, task_id, and update fields
        session: The database session
        
    Returns:
        UpdateTaskResponse with success status and task_id or error message
    """
    try:
        # Create a TaskUpdate object from the request, only including provided fields
        update_data = {}
        if request.title is not None:
            update_data['title'] = request.title
        if request.description is not None:
            update_data['description'] = request.description
        if request.due_date is not None:
            update_data['due_date'] = request.due_date.date()  # Convert datetime to date
        if request.completed is not None:
            update_data['is_complete'] = request.completed
            
        task_update_data = TaskUpdate(**update_data)
        
        # Use the existing service to update the task
        task = await update_task(session, request.task_id, task_update_data, request.user_id)
        
        # Return success response with the task ID
        return UpdateTaskResponse(
            success=True,
            task_id=task.id
        )
    except Exception as e:
        logger.error(f"Error in update_task_handler: {str(e)}")
        return UpdateTaskResponse(
            success=False,
            error_message=str(e)
        )