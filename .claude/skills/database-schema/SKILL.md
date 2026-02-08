---
name: database-schema
description: Design database schemas, create tables, and manage migrations for web applications.
---

# Database Skill – Tables, Migrations, Schema Design

## Instructions

1. **Schema Design**
   - Identify entities and relationships
   - Define primary keys, foreign keys, and indexes
   - Normalize tables to reduce redundancy

2. **Table Creation**
   - Use SQL or ORM tools to define tables
   - Specify data types and constraints
   - Ensure proper naming conventions

3. **Migrations**
   - Use migration tools to version schema changes
   - Write reversible migration scripts
   - Apply migrations consistently across environments

4. **Data Integrity**
   - Use constraints (NOT NULL, UNIQUE, CHECK)
   - Apply cascading rules for foreign keys
   - Ensure referential integrity

## Best Practices
- Keep table names singular and descriptive
- Index frequently queried columns
- Avoid storing redundant or derived data
- Document schema changes
- Follow consistent naming conventions
- Plan for scalability and future modifications

## Example Structure
```sql
-- Users Table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts Table
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Example Migration (Adding a new column)
ALTER TABLE posts
ADD COLUMN published BOOLEAN DEFAULT FALSE;
