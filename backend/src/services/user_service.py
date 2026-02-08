from sqlmodel import Session, select
import bcrypt
import logging
import secrets
import hmac
from ..models.user import User, UserCreate
from ..core.exceptions import ValidationError
from ..core.config import settings

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with OWASP-compliant work factor.

    Security:
    - Uses bcrypt with minimum 12 rounds (configurable via settings)
    - Automatically generates cryptographically secure salt
    - Resistant to rainbow table attacks
    - Handles 72-byte bcrypt limit by truncating if necessary

    Args:
        password: Plain text password to hash

    Returns:
        Bcrypt hashed password string
    """
    # SECURITY: bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')[:72]

    # Generate salt with configured rounds (OWASP minimum: 12)
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)

    # Hash the password
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password using constant-time comparison.

    Security:
    - Uses bcrypt's checkpw which includes timing attack protection
    - Constant-time comparison prevents timing attacks
    - Automatically handles bcrypt salt extraction

    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        # SECURITY: bcrypt.checkpw uses constant-time comparison internally
        password_bytes = plain_password.encode('utf-8')[:72]
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        # Log error but don't expose details to caller
        logger.error(f"Password verification error: {str(e)}")
        return False


def create_user_sync(session: Session, user_data: UserCreate) -> User:
    """
    Create a new user with hashed password.

    Args:
        session: Database session
        user_data: User registration data (email and password)

    Returns:
        Created user object

    Raises:
        ValidationError: If email already exists or validation fails
    """
    # Normalize email to lowercase
    email = user_data.email.lower().strip()

    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if existing_user:
        logger.warning(f"Registration attempt with existing email: {email}")
        raise ValidationError("Email already registered")

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create new user
    user = User(
        email=email,
        password_hash=hashed_password,
    )

    # Debug logging
    logger.info(f"Creating user with email: {email}")
    
    session.add(user)
    logger.info("Added user to session")
    
    session.commit()
    logger.info("Committed transaction")
    
    session.refresh(user)
    logger.info(f"Refreshed user, ID: {user.id}")

    logger.info(f"User created successfully: {user.id} ({email})")
    return user


async def create_user(session: Session, user_data: UserCreate) -> User:
    """
    Async wrapper for create_user_sync to maintain compatibility.
    
    Args:
        session: Database session
        user_data: User registration data (email and password)

    Returns:
        Created user object

    Raises:
        ValidationError: If email already exists or validation fails
    """
    # For sync database operations, we can call the sync version directly
    # This avoids potential issues with async/await and database transactions
    return create_user_sync(session, user_data)


def get_user_by_email_sync(session: Session, email: str) -> User | None:
    """
    Get a user by email (case-insensitive).

    Args:
        session: Database session
        email: User email

    Returns:
        User object if found, None otherwise
    """
    email = email.lower().strip()
    return session.exec(select(User).where(User.email == email)).first()


async def get_user_by_email(session: Session, email: str) -> User | None:
    """
    Async wrapper for get_user_by_email_sync to maintain compatibility.

    Args:
        session: Database session
        email: User email

    Returns:
        User object if found, None otherwise
    """
    return get_user_by_email_sync(session, email)


def get_user_by_id_sync(session: Session, user_id: int) -> User | None:
    """
    Get a user by ID.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        User object if found, None otherwise
    """
    return session.get(User, user_id)


async def get_user_by_id(session: Session, user_id: int) -> User | None:
    """
    Async wrapper for get_user_by_id_sync to maintain compatibility.

    Args:
        session: Database session
        user_id: User ID

    Returns:
        User object if found, None otherwise
    """
    return get_user_by_id_sync(session, user_id)
