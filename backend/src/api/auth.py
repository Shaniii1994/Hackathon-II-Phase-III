from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from pydantic import BaseModel
import logging

from ..core.exceptions import ValidationError
from ..db.connection import get_session
from ..models.user import UserCreate, UserLogin, UserResponse
from ..services.user_service import create_user
from ..services.auth_service import authenticate_user, refresh_access_token

router = APIRouter()
logger = logging.getLogger(__name__)


class LoginResponse(BaseModel):
    """
    Response model for login endpoint.

    Security:
    - Returns both access and refresh tokens
    - Access token: short-lived (30 min) for API requests
    - Refresh token: long-lived (7 days) for obtaining new access tokens
    """
    access_token: str
    refresh_token: str
    token_type: str
    user_id: int


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh endpoint."""
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    """Response model for token refresh endpoint."""
    access_token: str
    token_type: str


@router.post(
    "/register",
    response_model=LoginResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password and return authentication tokens.",
    responses={
        201: {"description": "User registered successfully and logged in"},
        422: {"description": "Validation error - email already exists or invalid data"},
    },
)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session),
):
    """
    Register a new user account and return authentication tokens.

    Security Requirements (OWASP Compliant):
    - **email**: Valid email address (will be normalized to lowercase)
    - **password**: Minimum 8 characters with:
      - At least one uppercase letter
      - At least one lowercase letter
      - At least one digit
      - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

    Password is hashed using bcrypt with 12 rounds (OWASP minimum).
    Password is never stored in plain text.

    After successful registration, returns authentication tokens to auto-login the user.
    """
    logger.info(f"Registration endpoint hit for email: {user_data.email}")
    
    try:
        # Create the user
        logger.info("Calling create_user function")
        user = await create_user(session, user_data)
        logger.info(f"User creation returned: {user.id if user else 'None'}")

        # After successful registration, create and return authentication tokens
        # This provides a seamless experience for the user
        from ..services.auth_service import create_access_token, create_refresh_token

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        logger.info(f"User registered and tokens generated successfully: {user.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id
        }
    except ValidationError as ve:
        logger.error(f"Validation error during registration: {ve}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during registration: {e}")
        session.rollback()  # Ensure rollback on error
        raise


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login user",
    description="Authenticate user and receive JWT access and refresh tokens.",
    responses={
        200: {"description": "Login successful, returns access and refresh tokens"},
        401: {"description": "Invalid credentials or account locked"},
    },
)
async def login(
    login_data: UserLogin,
    session: Session = Depends(get_session),
):
    """
    Login user and return JWT tokens.

    Security Features:
    - Generic error messages prevent email enumeration
    - Account lockout after 5 failed attempts (30 min lockout)
    - Failed attempt tracking and rate limiting
    - Constant-time password comparison

    Returns:
    - **access_token**: Short-lived token (30 min) for API requests
    - **refresh_token**: Long-lived token (7 days) for obtaining new access tokens
    - **token_type**: "bearer"
    - **user_id**: Authenticated user's ID

    Usage:
    1. Use access_token in Authorization header: `Authorization: Bearer <access_token>`
    2. When access_token expires, use refresh_token at /auth/refresh to get new access_token
    3. Store refresh_token securely (httpOnly cookie recommended for web apps)
    """
    logger.info(f"Login attempt for email: {login_data.email}")
    result = await authenticate_user(session, login_data)
    return result


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Refresh access token",
    description="Generate a new access token using a valid refresh token.",
    responses={
        200: {"description": "New access token generated successfully"},
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh_token(
    request: RefreshTokenRequest,
    session: Session = Depends(get_session),
):
    """
    Refresh access token using a valid refresh token.

    Security:
    - Validates refresh token signature and expiration
    - Verifies user still exists and account is not locked
    - Returns new access token for continued session

    Use this endpoint when your access token expires to obtain a new one
    without requiring the user to log in again.

    Best Practice:
    - Call this endpoint when you receive a 401 error on protected routes
    - Store refresh token securely (httpOnly cookie for web apps)
    - Never expose refresh token in URLs or logs
    """
    logger.info("Token refresh attempt")
    result = await refresh_access_token(session, request.refresh_token)
    logger.info("Token refreshed successfully")
    return result
