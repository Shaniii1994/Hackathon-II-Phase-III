from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import logging
from ..core.config import settings
from ..core.exceptions import UnauthorizedError

# HTTP Bearer scheme for token extraction
security = HTTPBearer()
logger = logging.getLogger(__name__)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """
    Extract and validate JWT access token from Authorization header.

    Security Features:
    - Validates token signature using secret key
    - Verifies token expiration
    - Ensures token type is 'access' (not refresh)
    - Uses constant-time comparison for token validation
    - Returns generic error messages to prevent information leakage

    This dependency extracts the user ID from a valid JWT access token.
    Use this in route handlers to get the authenticated user's ID.

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        int: Authenticated user's ID

    Raises:
        UnauthorizedError: If token is invalid, expired, wrong type, or malformed

    Example:
        @router.get("/tasks")
        async def get_tasks(user_id: int = Depends(get_current_user)):
            return get_user_tasks(user_id)

    Security Notes:
    - Only accepts access tokens (not refresh tokens)
    - Logs validation failures for security monitoring
    - Returns generic error messages to users
    - Detailed errors logged server-side only
    """
    token = credentials.credentials

    try:
        # SECURITY: Decode and verify the JWT token signature and expiration
        payload = jwt.decode(
            token,
            settings.BETTER_AUTH_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        # SECURITY: Verify token type to prevent refresh token misuse
        token_type = payload.get("type")
        if token_type != "access":
            logger.warning(
                f"Invalid token type '{token_type}' used for authentication. "
                "Expected 'access' token."
            )
            raise UnauthorizedError("Invalid authentication credentials")

        # Extract user ID from token
        user_id: str = payload.get("sub")

        if user_id is None:
            # SECURITY: Don't expose internal details in error messages
            logger.warning("Token missing 'sub' claim")
            raise UnauthorizedError("Invalid authentication credentials")

        logger.debug(f"User {user_id} authenticated successfully")
        return int(user_id)

    except JWTError as e:
        # SECURITY: Log the actual error but return generic message to client
        # This prevents attackers from learning about token structure or validation logic
        logger.warning(f"JWT validation failed: {str(e)}")
        raise UnauthorizedError("Invalid authentication credentials")

