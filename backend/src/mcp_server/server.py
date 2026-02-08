"""
MCP (Model Context Protocol) Server for AI Agent Integration

This module sets up an MCP server that exposes tools for AI agents to interact
with the todo application backend. The server provides secure, authenticated
access to task management functions while enforcing user ownership.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from backend.src.core.config import settings
from backend.src.db.connection import get_session
from backend.src.middleware.auth import get_current_user
from backend.src.mcp_server.tools.add_task import add_task_handler
from backend.src.mcp_server.tools.list_tasks import list_tasks_handler
from backend.src.mcp_server.tools.complete_task import complete_task_handler
from backend.src.mcp_server.tools.delete_task import delete_task_handler
from backend.src.mcp_server.tools.update_task import update_task_handler
from backend.src.models.mcp_models import (
    AddTaskRequest, AddTaskResponse,
    ListTasksRequest, ListTasksResponse,
    CompleteTaskRequest, CompleteTaskResponse,
    DeleteTaskRequest, DeleteTaskResponse,
    UpdateTaskRequest, UpdateTaskResponse
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    logger.info("Starting MCP server...")
    # Startup logic here
    yield
    # Shutdown logic here
    logger.info("Shutting down MCP server...")


# Create FastAPI app for MCP server
app = FastAPI(
    title="Todo App MCP Server",
    description="MCP server for AI agent integration with todo application",
    version="1.0.0",
    lifespan=lifespan,
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, configure specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the MCP server."""
    return {"status": "healthy", "service": "mcp-server"}


# Tool endpoints
@app.post("/tools/add_task", response_model=AddTaskResponse)
async def add_task_endpoint(
    request: AddTaskRequest,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    """
    MCP tool endpoint for adding a new task.
    
    This endpoint validates that the user_id in the request matches the authenticated user,
    then delegates to the handler function.
    """
    # Verify user ownership
    if request.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: User ID mismatch")
    
    try:
        result = await add_task_handler(request, session)
        return result
    except Exception as e:
        logger.error(f"Error in add_task: {str(e)}")
        return AddTaskResponse(success=False, error_message=str(e))


@app.post("/tools/list_tasks", response_model=ListTasksResponse)
async def list_tasks_endpoint(
    request: ListTasksRequest,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    """
    MCP tool endpoint for listing tasks.
    
    This endpoint validates that the user_id in the request matches the authenticated user,
    then delegates to the handler function.
    """
    # Verify user ownership
    if request.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: User ID mismatch")
    
    try:
        result = await list_tasks_handler(request, session)
        return result
    except Exception as e:
        logger.error(f"Error in list_tasks: {str(e)}")
        return ListTasksResponse(success=False, tasks=[], error_message=str(e))


@app.post("/tools/complete_task", response_model=CompleteTaskResponse)
async def complete_task_endpoint(
    request: CompleteTaskRequest,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    """
    MCP tool endpoint for completing a task.
    
    This endpoint validates that the user_id in the request matches the authenticated user,
    then delegates to the handler function.
    """
    # Verify user ownership
    if request.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: User ID mismatch")
    
    try:
        result = await complete_task_handler(request, session)
        return result
    except Exception as e:
        logger.error(f"Error in complete_task: {str(e)}")
        return CompleteTaskResponse(success=False, error_message=str(e))


@app.post("/tools/delete_task", response_model=DeleteTaskResponse)
async def delete_task_endpoint(
    request: DeleteTaskRequest,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    """
    MCP tool endpoint for deleting a task.
    
    This endpoint validates that the user_id in the request matches the authenticated user,
    then delegates to the handler function.
    """
    # Verify user ownership
    if request.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: User ID mismatch")
    
    try:
        result = await delete_task_handler(request, session)
        return result
    except Exception as e:
        logger.error(f"Error in delete_task: {str(e)}")
        return DeleteTaskResponse(success=False, error_message=str(e))


@app.post("/tools/update_task", response_model=UpdateTaskResponse)
async def update_task_endpoint(
    request: UpdateTaskRequest,
    session: Session = Depends(get_session),
    current_user_id: int = Depends(get_current_user)
):
    """
    MCP tool endpoint for updating a task.
    
    This endpoint validates that the user_id in the request matches the authenticated user,
    then delegates to the handler function.
    """
    # Verify user ownership
    if request.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Unauthorized: User ID mismatch")
    
    try:
        result = await update_task_handler(request, session)
        return result
    except Exception as e:
        logger.error(f"Error in update_task: {str(e)}")
        return UpdateTaskResponse(success=False, error_message=str(e))


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "server:app",
        host=os.getenv("MCP_SERVER_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_SERVER_PORT", 8001)),
        reload=True,
        log_level="info"
    )