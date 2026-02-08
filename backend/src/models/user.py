from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List
from pydantic import field_validator
import re

if TYPE_CHECKING:
    from .conversation import Conversation
    from .task import Task


class User(SQLModel, table=True):
    """
    User model for authentication and task ownership.

    Indexes:
    - email: Unique index for fast lookup during authentication

    Constraints:
    - email: UNIQUE, NOT NULL
    - password_hash: NOT NULL

    Security Features:
    - Failed login tracking for rate limiting
    - Account lockout mechanism
    - Refresh token storage for session management
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # Email with unique constraint and index for fast authentication lookups
    email: str = Field(
        index=True,
        unique=True,
        max_length=255,
        nullable=False,
        description="User's email address (unique identifier)"
    )

    # Password hash - never store plain passwords
    password_hash: str = Field(
        max_length=255,
        nullable=False,
        description="Bcrypt hashed password"
    )

    # SECURITY: Failed login tracking for rate limiting and account lockout
    failed_login_attempts: int = Field(
        default=0,
        nullable=False,
        description="Number of consecutive failed login attempts"
    )

    # SECURITY: Account lockout timestamp
    locked_until: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Account locked until this timestamp (None if not locked)"
    )

    # SECURITY: Last failed login attempt timestamp for rate limiting
    last_failed_login: Optional[datetime] = Field(
        default=None,
        nullable=True,
        description="Timestamp of last failed login attempt"
    )

    # Timestamp with server-side default
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Account creation timestamp"
    )



class UserCreate(SQLModel):
    """Schema for user registration with validation."""

    email: str = Field(
        min_length=3,
        max_length=255,
        description="Valid email address"
    )
    password: str = Field(
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)"
    )

    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format and normalize to lowercase."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError("Invalid email format")
        return v.lower().strip()

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Validate password strength requirements (OWASP compliant).

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        # SECURITY: Require special characters for stronger passwords
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
        return v


class UserLogin(SQLModel):
    """Schema for user login."""

    email: str
    password: str


class UserResponse(SQLModel):
    """Schema for user response (without password)."""

    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True