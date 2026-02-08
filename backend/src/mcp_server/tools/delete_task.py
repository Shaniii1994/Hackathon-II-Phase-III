"""
MCP Tool Handler: delete_task

This module implements the delete_task MCP tool that allows AI agents to delete
tasks for authenticated users.
"""

import logging
from sqlmodel import Session
from ...services.task_service import delete_task
from ...models.mcp_models import DeleteTaskRequest, DeleteTaskResponse


logger = logging.getLogger(__name__)


async def delete_task_handler(request: DeleteTaskRequest, session: Session) -> DeleteTaskResponse:
    """
    Handle the delete_task MCP tool request.
    
    Args:
        request: The delete_task request containing user_id and task_id
        session: The database session
        
    Returns:
        DeleteTaskResponse with success status or error message
    """
    try:
        # Use the existing service to delete the task
        await delete_task(session, request.task_id, request.user_id)
        
        # Return success response
        return DeleteTaskResponse(
            success=True
        )
    except Exception as e:
        logger.error(f"Error in delete_task_handler: {str(e)}")
        return DeleteTaskResponse(
            success=False,
            error_message=str(e)
        )