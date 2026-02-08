"""
Database migration runner script.
Executes SQL migration files against the Neon PostgreSQL database.
"""
import psycopg2
from src.core.config import settings
import sys

def run_migration(sql_file_path: str):
    """
    Execute a SQL migration file against the database.

    Args:
        sql_file_path: Path to the SQL migration file
    """
    try:
        # Connect to database
        print(f"Connecting to database...")
        conn = psycopg2.connect(settings.DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        # Read migration file
        print(f"Reading migration file: {sql_file_path}")
        with open(sql_file_path, 'r') as f:
            sql = f.read()

        # Execute migration
        print(f"Executing migration...")
        cursor.execute(sql)

        # Fetch and display results if any
        if cursor.description:
            results = cursor.fetchall()
            if results:
                print("\nMigration verification results:")
                for row in results:
                    print(f"  {row}")

        print("\n[SUCCESS] Migration completed successfully!")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_file.sql>")
        sys.exit(1)

    migration_file = sys.argv[1]
    run_migration(migration_file)
