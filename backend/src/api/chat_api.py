from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import logging
from typing import Dict, Any
import asyncio
import json

from ..db.connection import get_session
from ..middleware.auth import get_current_user
from ..services.conversation_service import create_conversation, create_message, get_messages
from ..models.mcp_models import MessageRequest, MessageResponse

# Import the MCP tools
from ..mcp_server.tools.add_task import add_task_handler
from ..mcp_server.tools.list_tasks import list_tasks_handler
from ..mcp_server.tools.complete_task import complete_task_handler
from ..mcp_server.tools.delete_task import delete_task_handler
from ..mcp_server.tools.update_task import update_task_handler

from ..models.mcp_models import (
    AddTaskRequest, ListTasksRequest, CompleteTaskRequest,
    DeleteTaskRequest, UpdateTaskRequest
)

router = APIRouter()
logger = logging.getLogger(__name__)


class SimpleAIProcessor:
    """
    A simple AI processor that parses natural language and calls appropriate MCP tools.
    In a real implementation, this would connect to an LLM service like OpenAI.
    """
    
    def __init__(self):
        self.tool_keywords = {
            'add': ['add', 'create', 'make', 'new'],
            'list': ['list', 'show', 'view', 'see', 'display'],
            'complete': ['complete', 'finish', 'done', 'mark'],
            'delete': ['delete', 'remove', 'cancel'],
            'update': ['update', 'change', 'modify', 'edit']
        }
    
    async def process_message(self, message: str, user_id: int, session: Session) -> str:
        """
        Process a natural language message and call appropriate MCP tools.
        """
        message_lower = message.lower()
        
        # Determine which tool to call based on keywords
        if any(keyword in message_lower for keyword in self.tool_keywords['add']):
            return await self.handle_add_task(message, user_id, session)
        elif any(keyword in message_lower for keyword in self.tool_keywords['list']):
            return await self.handle_list_tasks(message, user_id, session)
        elif any(keyword in message_lower for keyword in self.tool_keywords['complete']):
            return await self.handle_complete_task(message, user_id, session)
        elif any(keyword in message_lower for keyword in self.tool_keywords['delete']):
            return await self.handle_delete_task(message, user_id, session)
        elif any(keyword in message_lower for keyword in self.tool_keywords['update']):
            return await self.handle_update_task(message, user_id, session)
        else:
            # Default response if no specific action is detected
            return f"I understood your message: '{message}'. How can I help you with your tasks?"
    
    async def handle_add_task(self, message: str, user_id: int, session: Session) -> str:
        """
        Extract task details from message and call add_task tool.
        """
        # Simple extraction - in a real implementation, this would use NLP
        import re
        
        # Look for task title in the message (everything after common phrases)
        title_match = re.search(r'(?:add|create|make)\s+(?:a\s+)?(.+?)(?:\s+to\s+my\s+tasks?|$)', message_lower)
        if not title_match:
            title_match = re.search(r'(?:add|create|make)\s+(.+)', message_lower)
        
        if title_match:
            title = title_match.group(1).strip()
            # Clean up the title
            title = re.sub(r'\s+', ' ', title)  # Replace multiple spaces with single space
        else:
            title = "New task"  # Default title if none found
        
        # Create request for add_task tool
        request = AddTaskRequest(
            user_id=user_id,
            title=title[:200] if len(title) > 200 else title,  # Ensure title is within limits
            description=f"Created from AI request: {message}"
        )
        
        # Call the MCP tool
        response = await add_task_handler(request, session)
        
        if response.success:
            return f"I've added the task '{title}' to your list."
        else:
            return f"Sorry, I couldn't add the task: {response.error_message}"
    
    async def handle_list_tasks(self, message: str, user_id: int, session: Session) -> str:
        """
        Call list_tasks tool and format the response.
        """
        # Determine if user wants completed tasks
        include_completed = 'incomplete' not in message_lower and 'uncompleted' not in message_lower
        
        # Create request for list_tasks tool
        request = ListTasksRequest(
            user_id=user_id,
            include_completed=include_completed,
            limit=10  # Limit to 10 tasks for readability
        )
        
        # Call the MCP tool
        response = await list_tasks_handler(request, session)
        
        if response.success:
            if not response.tasks:
                return "You don't have any tasks right now."
            
            task_list = []
            for task in response.tasks:
                status = "✓" if task.get('is_complete', False) else "○"
                task_list.append(f"{status} {task['title']}")
            
            return f"Here are your tasks:\n" + "\n".join([f"- {task}" for task in task_list])
        else:
            return f"Sorry, I couldn't retrieve your tasks: {response.error_message}"
    
    async def handle_complete_task(self, message: str, user_id: int, session: Session) -> str:
        """
        Extract task ID and call complete_task tool.
        """
        import re
        
        # Try to extract task ID from message
        task_id_match = re.search(r'task\s+(\d+)', message_lower)
        if not task_id_match:
            # If no specific task ID, try to find by title
            return "Please specify which task you want to mark as complete by its number or title."
        
        try:
            task_id = int(task_id_match.group(1))
            
            # Create request for complete_task tool
            request = CompleteTaskRequest(
                user_id=user_id,
                task_id=task_id,
                completed=True
            )
            
            # Call the MCP tool
            response = await complete_task_handler(request, session)
            
            if response.success:
                return f"I've marked task {task_id} as complete."
            else:
                return f"Sorry, I couldn't mark the task as complete: {response.error_message}"
        except ValueError:
            return "Invalid task number. Please specify a valid task number."
    
    async def handle_delete_task(self, message: str, user_id: int, session: Session) -> str:
        """
        Extract task ID and call delete_task tool.
        """
        import re
        
        # Try to extract task ID from message
        task_id_match = re.search(r'task\s+(\d+)', message_lower)
        if not task_id_match:
            return "Please specify which task you want to delete by its number."
        
        try:
            task_id = int(task_id_match.group(1))
            
            # Create request for delete_task tool
            request = DeleteTaskRequest(
                user_id=user_id,
                task_id=task_id
            )
            
            # Call the MCP tool
            response = await delete_task_handler(request, session)
            
            if response.success:
                return f"I've deleted task {task_id}."
            else:
                return f"Sorry, I couldn't delete the task: {response.error_message}"
        except ValueError:
            return "Invalid task number. Please specify a valid task number."
    
    async def handle_update_task(self, message: str, user_id: int, session: Session) -> str:
        """
        Extract task details and call update_task tool.
        """
        import re
        
        # Extract task ID and what to update
        task_id_match = re.search(r'task\s+(\d+)', message_lower)
        if not task_id_match:
            return "Please specify which task you want to update by its number."
        
        try:
            task_id = int(task_id_match.group(1))
            
            # For now, just update the title if mentioned
            title_match = re.search(r'(?:update|change|modify|edit)\s+task\s+\d+\s+(?:to|with|as)\s+(.+?)(?:\.|$)', message_lower)
            if not title_match:
                return "Please specify what you want to update in the task."
            
            new_title = title_match.group(1).strip()
            
            # Create request for update_task tool
            request = UpdateTaskRequest(
                user_id=user_id,
                task_id=task_id,
                title=new_title[:200] if len(new_title) > 200 else new_title
            )
            
            # Call the MCP tool
            response = await update_task_handler(request, session)
            
            if response.success:
                return f"I've updated task {task_id} with the new title."
            else:
                return f"Sorry, I couldn't update the task: {response.error_message}"
        except ValueError:
            return "Invalid task number. Please specify a valid task number."


# Global instance of the AI processor
ai_processor = SimpleAIProcessor()


@router.post(
    "/{user_id}/chat",
    summary="Send a message to the AI agent",
    description="Process a natural language message through the AI agent and return a response.",
    responses={
        200: {"description": "AI response generated successfully"},
        401: {"description": "Invalid or missing authentication token"},
        422: {"description": "Validation error - invalid message data"},
    },
)
async def chat_with_ai(
    user_id: int,
    message_data: Dict[str, Any],  # Using Dict since we don't have a specific request model
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user),
):
    """
    Send a message to the AI agent and receive a response.
    
    The AI agent will interpret the natural language and call appropriate MCP tools
    to perform task operations.
    """
    # Verify that the user_id in the path matches the authenticated user
    if user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden: User ID mismatch")
    
    # Extract message content from the request
    message_content = message_data.get("message", "")
    if not message_content:
        raise HTTPException(status_code=400, detail="Message content is required")
    
    logger.info(f"User {user_id} sent message: {message_content}")
    
    try:
        # Process the message with the AI agent
        ai_response = await ai_processor.process_message(message_content, user_id, session)
        
        # Log the response
        logger.info(f"AI response for user {user_id}: {ai_response}")
        
        return {
            "success": True,
            "response": ai_response,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error processing AI message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")