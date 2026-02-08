from datetime import datetime, timedelta
from jose import jwt, JWTError
from sqlmodel import Session
import logging
from typing import Optional
from ..models.user import User, UserLogin
from ..core.config import settings
from ..core.exceptions import UnauthorizedError
from .user_service import get_user_by_email, verify_password

logger = logging.getLogger(__name__)


def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for the user.

    Security:
    - Short expiration (30 minutes) following OWASP recommendations
    - Includes user ID, expiration, and issued-at claims
    - Signed with HS256 algorithm (acceptable for symmetric keys)

    Args:
        user_id: User ID to encode in the token

    Returns:
        Encoded JWT access token string
    """
    # SECURITY: Short expiration for access tokens (OWASP: 15-30 minutes)
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # Create token payload with standard JWT claims
    payload = {
        "sub": str(user_id),           # Subject (user ID)
        "exp": expire,                  # Expiration time
        "iat": datetime.utcnow(),       # Issued at
        "type": "access"                # Token type for validation
    }

    # Encode and return token
    return jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token for long-lived sessions.

    Security:
    - Longer expiration (7 days) for session persistence
    - Separate token type to prevent misuse as access token
    - Should be stored securely (httpOnly cookie recommended)

    Args:
        user_id: User ID to encode in the token

    Returns:
        Encoded JWT refresh token string
    """
    # SECURITY: Longer expiration for refresh tokens (7 days)
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"  # SECURITY: Distinguish from access tokens
    }

    return jwt.encode(
        payload,
        settings.BETTER_AUTH_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )


def verify_refresh_token(token: str) -> Optional[int]:
    """
    Verify and decode a refresh token.

    Security:
    - Validates token signature and expiration
    - Ensures token type is 'refresh'
    - Returns None on any validation failure

    Args:
        token: JWT refresh token to verify

    Returns:
        User ID if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # SECURITY: Verify token type to prevent access token misuse
        if payload.get("type") != "refresh":
            logger.warning("Invalid token type for refresh operation")
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        return int(user_id)

    except JWTError as e:
        logger.warning(f"Refresh token validation failed: {str(e)}")
        return None


async def check_account_lockout(user: User) -> bool:
    """
    Check if user account is currently locked due to failed login attempts.

    Security:
    - Implements account lockout mechanism (OWASP recommendation)
    - Prevents brute-force attacks
    - Automatic unlock after lockout period expires

    Args:
        user: User object to check

    Returns:
        True if account is locked, False otherwise
    """
    if user.locked_until is None:
        return False

    # Check if lockout period has expired
    if datetime.utcnow() >= user.locked_until:
        # SECURITY: Lockout period expired, account is no longer locked
        return False

    # Account is still locked
    return True


async def reset_failed_login_attempts(session: Session, user: User) -> None:
    """
    Reset failed login attempts counter after successful login.

    Security:
    - Clears failed attempt tracking
    - Removes account lockout
    - Part of rate limiting mechanism

    Args:
        session: Database session
        user: User object to reset
    """
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_failed_login = None
    session.add(user)
    session.commit()


async def increment_failed_login_attempts(session: Session, user: User) -> None:
    """
    Increment failed login attempts and apply account lockout if threshold exceeded.

    Security:
    - Tracks failed login attempts (OWASP recommendation)
    - Implements progressive account lockout
    - Prevents brute-force attacks

    Args:
        session: Database session
        user: User object to update
    """
    user.failed_login_attempts += 1
    user.last_failed_login = datetime.utcnow()

    # SECURITY: Lock account if max attempts exceeded
    if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
        lockout_duration = timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
        user.locked_until = datetime.utcnow() + lockout_duration
        logger.warning(
            f"Account locked for user {user.id} due to {user.failed_login_attempts} "
            f"failed attempts. Locked until {user.locked_until}"
        )

    session.add(user)
    session.commit()


async def authenticate_user(
    session: Session,
    login_data: UserLogin,
) -> dict[str, int | str]:
    """
    Authenticate user with email and password.

    Security:
    - Generic error messages prevent email enumeration
    - Account lockout protection against brute-force
    - Failed attempt tracking and rate limiting
    - Constant-time password comparison
    - Returns both access and refresh tokens

    Args:
        session: Database session
        login_data: User login credentials

    Returns:
        Dictionary with access token, refresh token, token type, and user ID

    Raises:
        UnauthorizedError: If credentials are invalid or account is locked
    """
    # Normalize email
    email = login_data.email.lower().strip()

    # Get user by email
    user = await get_user_by_email(session, email)

    # SECURITY: Use generic error message to prevent email enumeration
    if not user:
        logger.warning(f"Login attempt with non-existent email: {email}")
        raise UnauthorizedError("Invalid email or password")

    # SECURITY: Check if account is locked due to failed attempts
    if await check_account_lockout(user):
        lockout_remaining = (user.locked_until - datetime.utcnow()).total_seconds() / 60
        logger.warning(
            f"Login attempt for locked account: {user.id}. "
            f"Locked for {lockout_remaining:.1f} more minutes"
        )
        raise UnauthorizedError(
            f"Account temporarily locked due to multiple failed login attempts. "
            f"Please try again in {int(lockout_remaining) + 1} minutes."
        )

    # SECURITY: Verify password using constant-time comparison
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Failed login attempt for user: {user.id}")

        # SECURITY: Increment failed attempts and potentially lock account
        await increment_failed_login_attempts(session, user)

        # SECURITY: Generic error message (don't reveal if email exists)
        raise UnauthorizedError("Invalid email or password")

    # SECURITY: Reset failed attempts on successful login
    await reset_failed_login_attempts(session, user)

    # Create JWT tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    logger.info(f"User {user.id} logged in successfully")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
    }


async def refresh_access_token(
    session: Session,
    refresh_token: str,
) -> dict[str, str]:
    """
    Generate a new access token using a valid refresh token.

    Security:
    - Validates refresh token signature and expiration
    - Ensures token type is 'refresh'
    - Verifies user still exists
    - Returns new access token for continued session

    Args:
        session: Database session
        refresh_token: Valid JWT refresh token

    Returns:
        Dictionary with new access token and token type

    Raises:
        UnauthorizedError: If refresh token is invalid or user not found
    """
    # Verify refresh token
    user_id = verify_refresh_token(refresh_token)

    if user_id is None:
        logger.warning("Invalid refresh token provided")
        raise UnauthorizedError("Invalid refresh token")

    # Verify user still exists
    from .user_service import get_user_by_id
    user = await get_user_by_id(session, user_id)

    if not user:
        logger.warning(f"Refresh token for non-existent user: {user_id}")
        raise UnauthorizedError("Invalid refresh token")

    # SECURITY: Check if account is locked
    if await check_account_lockout(user):
        logger.warning(f"Refresh attempt for locked account: {user_id}")
        raise UnauthorizedError("Account is locked")

    # Generate new access token
    new_access_token = create_access_token(user_id)

    logger.info(f"Access token refreshed for user {user_id}")

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
