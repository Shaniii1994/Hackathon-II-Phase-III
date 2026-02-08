from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, Index
from datetime import datetime, date
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from .user import User


class Task(SQLModel, table=True):
    """
    Task model for todo items.

    Indexes:
    - user_id: Foreign key index for fast user task lookups
    - idx_task_user_status_date: Composite index on (user_id, is_complete, due_date)
      for optimized filtering and sorting queries

    Constraints:
    - title: NOT NULL
    - user_id: NOT NULL, FOREIGN KEY with CASCADE DELETE
    - is_complete: NOT NULL, DEFAULT FALSE

    Relationships:
    - user: Many-to-one relationship with User (CASCADE DELETE)
    """

    __table_args__ = (
        # Composite index for common query patterns:
        # - Get all tasks for a user
        # - Filter by completion status
        # - Sort by due date
        Index('idx_task_user_status_date', 'user_id', 'is_complete', 'due_date'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    # Task title - required field
    title: str = Field(
        max_length=200,
        nullable=False,
        description="Task title or summary"
    )

    # Optional description with reasonable length limit
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        nullable=True,
        description="Detailed task description"
    )

    # Optional due date for task scheduling
    due_date: Optional[date] = Field(
        default=None,
        nullable=True,
        description="Task due date"
    )

    # Completion status with default
    is_complete: bool = Field(
        default=False,
        nullable=False,
        description="Task completion status"
    )

    # Foreign key to user with CASCADE DELETE and index
    # When user is deleted, all their tasks are automatically deleted
    user_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        index=True,  # Critical: Index foreign key for query performance
        ondelete="CASCADE",  # Automatically delete tasks when user is deleted
        description="ID of the user who owns this task"
    )

    # Timestamps with automatic management
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp"
    )

    # Auto-updating timestamp using SQLAlchemy's onupdate
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={
            "onupdate": datetime.utcnow,  # Automatically update on record modification
            "nullable": False
        },
        description="Last modification timestamp"
    )

    # Relationship to user
    user: "User" = Relationship(back_populates="tasks")


class TaskCreate(SQLModel):
    """Schema for task creation with validation."""

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (max 2000 characters)"
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Task due date (YYYY-MM-DD format)"
    )


class TaskUpdate(SQLModel):
    """Schema for task update with validation."""

    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Task description (max 2000 characters)"
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Task due date (YYYY-MM-DD format)"
    )
    is_complete: Optional[bool] = Field(
        default=None,
        description="Task completion status"
    )


class TaskResponse(SQLModel):
    """Schema for task response."""

    id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    is_complete: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
