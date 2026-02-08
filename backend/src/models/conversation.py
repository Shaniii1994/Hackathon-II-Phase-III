from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from pydantic import field_validator
import re

if TYPE_CHECKING:
    from .user import User


class Conversation(SQLModel, table=True):
    """
    Conversation model to track AI agent interactions with users.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to user
    user: "User" = Relationship(back_populates="conversations")


class Message(SQLModel, table=True):
    """
    Message model to store individual messages in a conversation.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str = Field(regex=r"^(user|assistant|system)$")  # user, assistant, or system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to conversation
    conversation: Conversation = Relationship(back_populates="messages")
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate that the role is one of the allowed values."""
        if v not in ['user', 'assistant', 'system']:
            raise ValueError("Role must be one of: user, assistant, system")
        return v