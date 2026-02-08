from sqlmodel import create_engine, Session
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

# Neon Serverless PostgreSQL Connection Configuration
# Optimized for serverless environments with connection pooling

# Connection arguments for Neon
# Note: statement_timeout is not supported with Neon's pooler endpoint
connect_args = {
    "sslmode": "require",  # Enforce SSL for Neon
    "connect_timeout": 10,  # Connection timeout in seconds
}

# Create database engine with Neon-optimized pooling
# Using Neon's connection pooler endpoint (-pooler) with PgBouncer
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,  # Set to False in production

    # Connection Pool Settings for Serverless
    pool_size=5,  # Minimum connections to maintain
    max_overflow=10,  # Additional connections when pool is exhausted
    pool_timeout=30,  # Seconds to wait for connection from pool
    pool_recycle=3600,  # Recycle connections after 1 hour (Neon best practice)
    pool_pre_ping=True,  # Verify connection health before using (critical for serverless)

    # Connection arguments
    connect_args=connect_args,

    # For serverless functions with very short lifecycles, consider NullPool
    # Uncomment below and comment out pool settings above if using NullPool
    # poolclass=NullPool,
)


def get_session():
    """
    Dependency function to get a database session.
    Use this in FastAPI endpoints with Depends(get_session).

    Implements proper connection management for Neon Serverless:
    - Automatic connection cleanup via context manager
    - Connection reuse from pool
    - Graceful error handling

    Example:
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            return session.exec(select(User)).all()
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            session.rollback()
            raise
        finally:
            session.close()


def check_connection():
    """
    Health check function to verify database connectivity.
    Use this for application startup checks or health endpoints.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with Session(engine) as session:
            session.exec(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


def close_connections():
    """
    Gracefully close all database connections.
    Call this during application shutdown.
    """
    try:
        engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
