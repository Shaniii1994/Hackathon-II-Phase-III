from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class AddTaskRequest(BaseModel):
    user_id: int = Field(..., description="The ID of the user creating the task")
    title: str = Field(..., min_length=1, max_length=200, description="The title of the task")
    description: Optional[str] = Field(None, max_length=2000, description="The description of the task")
    due_date: Optional[datetime] = Field(None, description="The due date for the task in ISO 8601 format")


class AddTaskResponse(BaseModel):
    success: bool
    task_id: Optional[int] = None
    error_message: Optional[str] = None


class ListTasksRequest(BaseModel):
    user_id: int = Field(..., description="The ID of the user whose tasks to retrieve")
    include_completed: Optional[bool] = Field(True, description="Whether to include completed tasks")
    limit: Optional[int] = Field(50, ge=1, le=100, description="Maximum number of tasks to return")
    offset: Optional[int] = Field(0, ge=0, description="Number of tasks to skip")


class ListTasksResponse(BaseModel):
    success: bool
    tasks: List[dict]  # Will contain task data as returned by the existing TaskResponse model
    error_message: Optional[str] = None


class CompleteTaskRequest(BaseModel):
    user_id: int = Field(..., description="The ID of the user requesting the change")
    task_id: int = Field(..., description="The ID of the task to update")
    completed: bool = Field(True, description="Whether the task is completed (true) or not (false)")


class CompleteTaskResponse(BaseModel):
    success: bool
    task_id: Optional[int] = None
    error_message: Optional[str] = None


class DeleteTaskRequest(BaseModel):
    user_id: int = Field(..., description="The ID of the user requesting the deletion")
    task_id: int = Field(..., description="The ID of the task to delete")


class DeleteTaskResponse(BaseModel):
    success: bool
    error_message: Optional[str] = None


class UpdateTaskRequest(BaseModel):
    user_id: int = Field(..., description="The ID of the user requesting the update")
    task_id: int = Field(..., description="The ID of the task to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New title for the task")
    description: Optional[str] = Field(None, max_length=2000, description="New description for the task")
    due_date: Optional[datetime] = Field(None, description="New due date in ISO 8601 format")
    completed: Optional[bool] = Field(None, description="New completion status")


class UpdateTaskResponse(BaseModel):
    success: bool
    task_id: Optional[int] = None
    error_message: Optional[str] = None


class ConversationRequest(BaseModel):
    user_id: int = Field(..., description="The ID of the user creating the conversation")
    title: str = Field(..., max_length=200, description="The title of the conversation")


class ConversationResponse(BaseModel):
    success: bool
    conversation_id: Optional[int] = None
    error_message: Optional[str] = None


class MessageRequest(BaseModel):
    conversation_id: int = Field(..., description="The ID of the conversation")
    role: UserRole = Field(..., description="The role of the message sender (user, assistant, system)")
    content: str = Field(..., description="The content of the message")


class MessageResponse(BaseModel):
    success: bool
    message_id: Optional[int] = None
    error_message: Optional[str] = None