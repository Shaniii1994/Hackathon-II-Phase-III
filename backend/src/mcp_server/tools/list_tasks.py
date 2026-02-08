"""
MCP Tool Handler: list_tasks

This module implements the list_tasks MCP tool that allows AI agents to retrieve
tasks for authenticated users.
"""

import logging
from sqlmodel import Session
from ...services.task_service import get_tasks
from ...models.mcp_models import ListTasksRequest, ListTasksResponse


logger = logging.getLogger(__name__)


async def list_tasks_handler(request: ListTasksRequest, session: Session) -> ListTasksResponse:
    """
    Handle the list_tasks MCP tool request.
    
    Args:
        request: The list_tasks request containing user_id, filters, limit, and offset
        session: The database session
        
    Returns:
        ListTasksResponse with success status and list of tasks or error message
    """
    try:
        # Use the existing service to get tasks for the user
        tasks = await get_tasks(
            session=session,
            user_id=request.user_id,
            include_completed=request.include_completed,
            limit=request.limit,
            offset=request.offset
        )
        
        # Convert tasks to dictionaries for the response
        task_dicts = []
        for task in tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "is_complete": task.is_complete,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            task_dicts.append(task_dict)
        
        # Return success response with the tasks
        return ListTasksResponse(
            success=True,
            tasks=task_dicts
        )
    except Exception as e:
        logger.error(f"Error in list_tasks_handler: {str(e)}")
        return ListTasksResponse(
            success=False,
            tasks=[],
            error_message=str(e)
        )