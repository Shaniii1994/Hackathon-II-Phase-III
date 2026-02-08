"""
MCP Tool Handler: complete_task

This module implements the complete_task MCP tool that allows AI agents to update
the completion status of tasks for authenticated users.
"""

import logging
from sqlmodel import Session
from ...services.task_service import toggle_complete
from ...models.mcp_models import CompleteTaskRequest, CompleteTaskResponse


logger = logging.getLogger(__name__)


async def complete_task_handler(request: CompleteTaskRequest, session: Session) -> CompleteTaskResponse:
    """
    Handle the complete_task MCP tool request.
    
    Args:
        request: The complete_task request containing user_id and task_id
        session: The database session
        
    Returns:
        CompleteTaskResponse with success status and task_id or error message
    """
    try:
        # Use the existing service to toggle the task completion status
        task = await toggle_complete(session, request.task_id, request.user_id)
        
        # Return success response with the task ID
        return CompleteTaskResponse(
            success=True,
            task_id=task.id
        )
    except Exception as e:
        logger.error(f"Error in complete_task_handler: {str(e)}")
        return CompleteTaskResponse(
            success=False,
            error_message=str(e)
        )