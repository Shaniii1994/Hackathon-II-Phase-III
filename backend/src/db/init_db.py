from sqlmodel import SQLModel
from .connection import engine, check_connection
from ..models.user import User
from ..models.task import Task
import logging
from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)


def init_db():
    """
    Initialize database by creating all tables.

    This function imports all models and creates their corresponding
    tables in the database if they don't already exist.

    For production environments, use Alembic migrations instead of
    SQLModel.metadata.create_all() for better version control and
    rollback capabilities.

    Raises:
        Exception: If database connection fails or table creation fails
    """
    try:
        # First, verify database connectivity
        logger.info("Checking database connection...")
        if not check_connection():
            raise Exception("Failed to connect to database")

        # Import all models here to ensure they are registered with SQLModel
        # This is necessary for SQLModel.metadata.create_all() to work
        logger.info("Creating database tables...")

        # Create all tables
        SQLModel.metadata.create_all(engine)

        logger.info("Database tables created successfully")
        logger.info("Tables created: user, task")

        # Log indexes created
        logger.info("Indexes created:")
        logger.info("  - user.email (unique)")
        logger.info("  - task.user_id (foreign key)")
        logger.info("  - task.idx_task_user_status_date (composite)")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def drop_all_tables():
    """
    Drop all tables from the database.

    WARNING: This will delete all data. Use only in development/testing.

    Raises:
        Exception: If table deletion fails
    """
    try:
        logger.warning("Dropping all database tables...")
        
        # Get a connection to execute raw SQL
        with engine.connect() as conn:
            # First, drop all foreign key constraints to avoid dependency issues
            # This query gets all foreign key constraints in the database
            inspector = inspect(engine)
            for table_name in reversed(inspector.get_table_names()):
                # Get foreign key constraints for this table
                fks = inspector.get_foreign_keys(table_name)
                for fk in fks:
                    # Drop the foreign key constraint first
                    conn.execute(text(f"ALTER TABLE {table_name} DROP CONSTRAINT IF EXISTS {fk['name']} CASCADE"))
            
            # Commit the transaction
            conn.commit()
            
            # Now drop all tables with CASCADE
            for table in reversed(SQLModel.metadata.sorted_tables):
                conn.execute(text(f'DROP TABLE IF EXISTS "{table.name}" CASCADE'))
            
            # Commit the transaction
            conn.commit()
        
        logger.info("All tables dropped successfully")
    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise


def reset_db():
    """
    Reset database by dropping and recreating all tables.

    WARNING: This will delete all data. Use only in development/testing.

    Raises:
        Exception: If reset fails
    """
    try:
        logger.warning("Resetting database...")
        drop_all_tables()
        init_db()
        logger.info("Database reset complete")
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        raise
