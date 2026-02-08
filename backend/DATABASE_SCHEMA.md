# Database Schema Documentation

## Overview

This document describes the database schema for the Todo Full-Stack Web Application using Neon Serverless PostgreSQL.

## Database Configuration

- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel (built on SQLAlchemy)
- **Connection Pooling**: Configured with PgBouncer via Neon's pooler endpoint
- **SSL**: Required (enforced)

## Connection Settings

```python
# Optimized for Neon Serverless
pool_size=5              # Minimum connections
max_overflow=10          # Additional connections when needed
pool_timeout=30          # Wait time for connection
pool_recycle=3600        # Recycle connections after 1 hour
pool_pre_ping=True       # Verify connection health
statement_timeout=30000  # 30 second query timeout
```

## Tables

### User Table

Stores user authentication and profile information.

**Table Name**: `user`

| Column        | Type         | Constraints                    | Description                    |
|---------------|--------------|--------------------------------|--------------------------------|
| id            | INTEGER      | PRIMARY KEY, AUTO INCREMENT    | Unique user identifier         |
| email         | VARCHAR(255) | UNIQUE, NOT NULL, INDEXED      | User's email (login)           |
| password_hash | VARCHAR(255) | NOT NULL                       | Bcrypt hashed password         |
| created_at    | TIMESTAMP    | NOT NULL, DEFAULT NOW()        | Account creation timestamp     |

**Indexes**:
- `ix_user_email` (UNIQUE): Fast email lookup for authentication

**SQL DDL**:
```sql
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX ix_user_email ON user(email);
```

### Task Table

Stores todo tasks associated with users.

**Table Name**: `task`

| Column       | Type         | Constraints                           | Description                    |
|--------------|--------------|---------------------------------------|--------------------------------|
| id           | INTEGER      | PRIMARY KEY, AUTO INCREMENT           | Unique task identifier         |
| title        | VARCHAR(200) | NOT NULL                              | Task title/summary             |
| description  | VARCHAR(2000)| NULL                                  | Detailed description           |
| due_date     | DATE         | NULL                                  | Task due date                  |
| is_complete  | BOOLEAN      | NOT NULL, DEFAULT FALSE               | Completion status              |
| user_id      | INTEGER      | NOT NULL, FOREIGN KEY, INDEXED        | Owner user ID                  |
| created_at   | TIMESTAMP    | NOT NULL, DEFAULT NOW()               | Creation timestamp             |
| updated_at   | TIMESTAMP    | NOT NULL, DEFAULT NOW(), ON UPDATE    | Last modification timestamp    |

**Foreign Keys**:
- `user_id` → `user.id` (ON DELETE CASCADE)
  - When a user is deleted, all their tasks are automatically deleted

**Indexes**:
- `ix_task_user_id`: Fast lookup of user's tasks
- `idx_task_user_status_date` (COMPOSITE): Optimized for common query patterns
  - Columns: (user_id, is_complete, due_date)
  - Supports: filtering by user, completion status, and sorting by due date

**SQL DDL**:
```sql
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description VARCHAR(2000),
    due_date DATE,
    is_complete BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER NOT NULL REFERENCES user(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_task_user_id ON task(user_id);
CREATE INDEX idx_task_user_status_date ON task(user_id, is_complete, due_date);

-- Trigger for auto-updating updated_at (PostgreSQL)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_task_updated_at BEFORE UPDATE ON task
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Relationships

```
User (1) ----< (Many) Task
  |                      |
  id  <--- user_id ------+

CASCADE DELETE: Deleting a user deletes all their tasks
```

## Query Optimization

### Common Query Patterns

1. **User Authentication** (uses `ix_user_email` index):
   ```sql
   SELECT * FROM user WHERE email = 'user@example.com';
   ```

2. **Get User's Tasks** (uses `idx_task_user_status_date` index):
   ```sql
   SELECT * FROM task
   WHERE user_id = 1
   ORDER BY due_date ASC NULLS LAST, created_at DESC;
   ```

3. **Filter by Completion Status** (uses `idx_task_user_status_date` index):
   ```sql
   SELECT * FROM task
   WHERE user_id = 1 AND is_complete = false
   ORDER BY due_date ASC NULLS LAST;
   ```

4. **Get Overdue Tasks** (uses `idx_task_user_status_date` index):
   ```sql
   SELECT * FROM task
   WHERE user_id = 1
     AND is_complete = false
     AND due_date < CURRENT_DATE
   ORDER BY due_date ASC;
   ```

### Index Strategy

- **Single-column indexes**: Used for unique lookups (email)
- **Foreign key indexes**: Prevent N+1 query problems (user_id)
- **Composite indexes**: Optimize multi-condition queries (user_id, is_complete, due_date)

## Data Integrity

### Constraints

1. **NOT NULL**: All required fields enforce non-null values
2. **UNIQUE**: Email addresses must be unique across users
3. **FOREIGN KEY**: Tasks must reference valid users
4. **CASCADE DELETE**: Orphaned tasks are automatically deleted
5. **CHECK**: Field lengths enforced at database level

### Validation Rules

- Email: Max 255 characters, unique, indexed
- Password Hash: Max 255 characters (bcrypt output)
- Task Title: Max 200 characters, required
- Task Description: Max 2000 characters, optional
- Due Date: Valid date or null

## Neon-Specific Optimizations

### Connection Pooling

Using Neon's built-in PgBouncer pooler:
- Connection string uses `-pooler` endpoint
- Pool size: 5 base + 10 overflow = 15 max connections
- Connections recycled every hour
- Health checks before each use (pool_pre_ping)

### Serverless Best Practices

1. **Connection Reuse**: Sessions reused within request lifecycle
2. **Automatic Cleanup**: Context managers ensure proper connection release
3. **Timeout Protection**: 30-second statement timeout prevents runaway queries
4. **Error Handling**: Automatic rollback on exceptions
5. **Health Checks**: Connection validation before queries

## Migration Strategy

### Current Approach

Using `SQLModel.metadata.create_all()` for initial development.

### Production Recommendation

Implement Alembic for production:

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Security Considerations

1. **Password Storage**: Only hashed passwords stored (bcrypt)
2. **SSL Required**: All connections use SSL/TLS
3. **Parameterized Queries**: SQLModel prevents SQL injection
4. **Connection String**: Stored in environment variables, not code
5. **Row-Level Security**: Enforced at application level (user_id checks)

## Performance Monitoring

### Key Metrics to Monitor

1. **Connection Pool Usage**: Track active/idle connections
2. **Query Performance**: Monitor slow queries (>100ms)
3. **Index Usage**: Verify indexes are being used
4. **Connection Errors**: Track connection failures/timeouts

### Neon Console Metrics

Monitor in Neon dashboard:
- Active connections
- Query duration (p50, p95, p99)
- Database size
- Connection pool saturation

## Backup and Recovery

Neon provides automatic backups:
- Point-in-time recovery (PITR)
- Automated daily backups
- Branch-based testing/staging

## Future Enhancements

Potential schema improvements:

1. **Task Categories/Tags**: Add many-to-many relationship
2. **Task Priority**: Add priority field with index
3. **Recurring Tasks**: Add recurrence pattern field
4. **Task Attachments**: Add file reference table
5. **Audit Log**: Track all changes to tasks
6. **Soft Deletes**: Add deleted_at field instead of hard deletes
7. **Full-Text Search**: Add GIN index for task search

## File References

- Models: `backend/src/models/user.py`, `backend/src/models/task.py`
- Connection: `backend/src/db/connection.py`
- Initialization: `backend/src/db/init_db.py`
- Utilities: `backend/src/db/utils.py`
- Configuration: `backend/src/core/config.py`
