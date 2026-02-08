# Quick Reference Guide - Database Operations

## Common Database Operations

### Starting the Database

```python
from backend.src.db.init_db import init_db

# Initialize database (create tables)
init_db()
```

### Getting a Database Session

```python
from fastapi import Depends
from backend.src.db.connection import get_session
from sqlmodel import Session

@app.get("/tasks")
def get_tasks(session: Session = Depends(get_session)):
    # Use session here
    pass
```

### User Operations

```python
from backend.src.db.utils import (
    create_user,
    get_user_by_email,
    get_user_by_id
)

# Create user
user = create_user(session, "user@example.com", "hashed_password")

# Get user by email
user = get_user_by_email(session, "user@example.com")

# Get user by ID
user = get_user_by_id(session, 1)
```

### Task Operations

```python
from backend.src.db.utils import (
    create_task,
    get_user_tasks,
    get_task_by_id,
    update_task,
    delete_task,
    toggle_task_completion,
    get_task_statistics
)

# Create task
task = create_task(
    session,
    user_id=1,
    title="My Task",
    description="Task description",
    due_date=date.today()
)

# Get all user tasks
tasks = get_user_tasks(session, user_id=1)

# Get completed tasks only
completed = get_user_tasks(session, user_id=1, is_complete=True)

# Get pending tasks only
pending = get_user_tasks(session, user_id=1, is_complete=False)

# Get task by ID (with authorization check)
task = get_task_by_id(session, task_id=1, user_id=1)

# Update task
updated = update_task(
    session,
    task,
    title="Updated Title",
    is_complete=True
)

# Toggle completion
toggled = toggle_task_completion(session, task)

# Delete task
delete_task(session, task)

# Get statistics
stats = get_task_statistics(session, user_id=1)
# Returns: {total, completed, pending, overdue, completion_rate}
```

### Health Checks

```python
from backend.src.db.connection import check_connection

# Check database connectivity
if check_connection():
    print("Database is healthy")
```

### Cleanup

```python
from backend.src.db.connection import close_connections

# Close all connections (on shutdown)
close_connections()
```

## FastAPI Integration Example

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session
from backend.src.db.connection import get_session, check_connection, close_connections
from backend.src.db.utils import get_user_tasks, create_task
from backend.src.models.task import TaskCreate, TaskResponse

app = FastAPI()

@app.on_event("startup")
async def startup():
    """Verify database connection on startup."""
    if not check_connection():
        raise Exception("Failed to connect to database")

@app.on_event("shutdown")
async def shutdown():
    """Close database connections on shutdown."""
    close_connections()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = check_connection()
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }

@app.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    user_id: int,
    is_complete: bool = None,
    session: Session = Depends(get_session)
):
    """Get user's tasks."""
    tasks = get_user_tasks(session, user_id, is_complete)
    return tasks

@app.post("/tasks", response_model=TaskResponse)
async def create_new_task(
    user_id: int,
    task_data: TaskCreate,
    session: Session = Depends(get_session)
):
    """Create a new task."""
    task = create_task(
        session,
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        due_date=task_data.due_date
    )
    return task
```

## Environment Variables

Required in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
DATABASE_ECHO=false  # Set to true for SQL query logging

# Auth
BETTER_AUTH_SECRET=your-secret-key
BETTER_AUTH_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000
```

## Testing

```bash
# Run comprehensive test suite
cd backend
python test_database.py

# Expected output: All tests pass
```

## Migration

```bash
# Development: Reset database
python -c "from src.db.init_db import reset_db; reset_db()"

# Production: Apply migration
psql $DATABASE_URL -f migrations/001_optimize_schema.sql
```

## Monitoring

### Check Connection Pool Status

```python
from backend.src.db.connection import engine

pool = engine.pool
print(f"Pool size: {pool.size()}")
print(f"Checked out: {pool.checkedout()}")
print(f"Overflow: {pool.overflow()}")
```

### Check Index Usage

```sql
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;
```

### Find Slow Queries

```sql
SELECT
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
WHERE mean_time > 100  -- queries slower than 100ms
ORDER BY mean_time DESC
LIMIT 10;
```

## Common Issues

### Connection Pool Exhausted

**Error**: `QueuePool limit of size X overflow Y reached`

**Solution**: Increase pool size in `connection.py`:
```python
pool_size=10,
max_overflow=20,
```

### Stale Connection

**Error**: `server closed the connection unexpectedly`

**Solution**: Already fixed with `pool_pre_ping=True`

### Query Timeout

**Error**: `canceling statement due to statement timeout`

**Solution**: Increase timeout in `connection.py`:
```python
"options": "-c statement_timeout=60000",  # 60 seconds
```

## Performance Tips

1. **Use Indexes**: All common queries use indexes
2. **Batch Operations**: Use bulk inserts for multiple records
3. **Pagination**: Use limit/offset for large result sets
4. **Connection Reuse**: Always use `Depends(get_session)`
5. **Monitor Pool**: Keep connections under 15 (5 base + 10 overflow)

## Security Checklist

- ✅ SSL required for all connections
- ✅ Passwords hashed with bcrypt
- ✅ Parameterized queries (SQL injection prevention)
- ✅ Environment variables for credentials
- ✅ Row-level authorization (user_id checks)
- ✅ Connection timeouts configured
- ✅ Statement timeouts configured

## File Locations

- **Models**: `backend/src/models/`
- **Database**: `backend/src/db/`
- **Config**: `backend/src/core/config.py`
- **Migrations**: `backend/migrations/`
- **Tests**: `backend/test_database.py`
- **Docs**: `backend/DATABASE_SCHEMA.md`, `backend/MIGRATION_GUIDE.md`

## Next Steps

1. Run `python test_database.py` to verify setup
2. Apply migration if needed
3. Test application endpoints
4. Monitor connection pool in Neon Console
5. Set up query performance monitoring
