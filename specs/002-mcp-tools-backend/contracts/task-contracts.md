# Task Operation Contracts: MCP Tools & Backend Integration (Phase-III)

## Overview
This document defines the contracts for all task-related operations accessible through MCP tools. These contracts ensure consistent behavior between the AI agent and the backend task management system.

## Add Task Contract

### Endpoint
`MCP Tool: add_task`

### Request Parameters
- `user_id`: Integer, required - The ID of the user creating the task
- `title`: String, required - The title of the task (1-200 characters)
- `description`: String, optional - The description of the task (up to 2000 characters)
- `due_date`: DateTime, optional - The due date for the task in ISO 8601 format

### Response Format
```json
{
  "success": true,
  "task_id": 123,
  "error_message": null
}
```

### Success Conditions
- Task is created in the database
- Task is associated with the correct user
- Current timestamp is recorded
- Response includes the new task ID

### Error Conditions
- Invalid user_id (returns 403 Forbidden)
- Missing or invalid title (returns 400 Bad Request)
- User quota exceeded (returns 429 Too Many Requests)
- Database error (returns 500 Internal Server Error)

### Validation Rules
- Title must be 1-200 characters
- Description, if provided, must be ≤2000 characters
- Due date, if provided, must be a valid future date
- User must exist and be authenticated

## List Tasks Contract

### Endpoint
`MCP Tool: list_tasks`

### Request Parameters
- `user_id`: Integer, required - The ID of the user whose tasks to retrieve
- `include_completed`: Boolean, optional (default: true) - Whether to include completed tasks
- `limit`: Integer, optional (default: 50, max: 100) - Maximum number of tasks to return
- `offset`: Integer, optional (default: 0) - Number of tasks to skip

### Response Format
```json
{
  "success": true,
  "tasks": [
    {
      "id": 123,
      "title": "Sample task",
      "description": "Task description",
      "completed": false,
      "due_date": "2026-02-08T10:00:00Z",
      "created_at": "2026-02-07T10:00:00Z",
      "updated_at": "2026-02-07T10:00:00Z"
    }
  ],
  "error_message": null
}
```

### Success Conditions
- Returns only tasks belonging to the specified user
- Respects include_completed filter
- Limits response size according to limit parameter
- Maintains order (most recent first)

### Error Conditions
- Invalid user_id (returns 403 Forbidden)
- Database error (returns 500 Internal Server Error)

### Validation Rules
- User must exist and be authenticated
- Limit parameter must be 1-100
- Offset parameter must be ≥0

## Complete Task Contract

### Endpoint
`MCP Tool: complete_task`

### Request Parameters
- `user_id`: Integer, required - The ID of the user requesting the change
- `task_id`: Integer, required - The ID of the task to update
- `completed`: Boolean, required - Whether the task is completed (true) or not (false)

### Response Format
```json
{
  "success": true,
  "task_id": 123,
  "error_message": null
}
```

### Success Conditions
- Task status is updated in the database
- Updated timestamp is recorded
- Only the requesting user's task can be modified

### Error Conditions
- Invalid user_id (returns 403 Forbidden)
- Invalid task_id (returns 404 Not Found)
- Task doesn't belong to user (returns 403 Forbidden)
- Database error (returns 500 Internal Server Error)

### Validation Rules
- Task must exist
- Task must belong to the specified user
- Completed parameter must be boolean

## Delete Task Contract

### Endpoint
`MCP Tool: delete_task`

### Request Parameters
- `user_id`: Integer, required - The ID of the user requesting the deletion
- `task_id`: Integer, required - The ID of the task to delete

### Response Format
```json
{
  "success": true,
  "error_message": null
}
```

### Success Conditions
- Task is removed from the database
- Associated data is cleaned up if needed

### Error Conditions
- Invalid user_id (returns 403 Forbidden)
- Invalid task_id (returns 404 Not Found)
- Task doesn't belong to user (returns 403 Forbidden)
- Database error (returns 500 Internal Server Error)

### Validation Rules
- Task must exist
- Task must belong to the specified user

## Update Task Contract

### Endpoint
`MCP Tool: update_task`

### Request Parameters
- `user_id`: Integer, required - The ID of the user requesting the update
- `task_id`: Integer, required - The ID of the task to update
- `title`: String, optional - New title for the task (1-200 characters)
- `description`: String, optional - New description for the task (≤2000 characters)
- `due_date`: DateTime, optional - New due date in ISO 8601 format
- `completed`: Boolean, optional - New completion status

### Response Format
```json
{
  "success": true,
  "task_id": 123,
  "error_message": null
}
```

### Success Conditions
- Specified task properties are updated in the database
- Updated timestamp is recorded
- Only the requesting user's task can be modified

### Error Conditions
- Invalid user_id (returns 403 Forbidden)
- Invalid task_id (returns 404 Not Found)
- Task doesn't belong to user (returns 403 Forbidden)
- Invalid parameter values (returns 400 Bad Request)
- Database error (returns 500 Internal Server Error)

### Validation Rules
- Task must exist
- Task must belong to the specified user
- If provided, title must be 1-200 characters
- If provided, description must be ≤2000 characters
- If provided, due date must be valid
- At least one property must be specified for update

## Authentication and Authorization Contracts

### JWT Token Validation
All MCP tools require a valid JWT token that:
- Is properly formatted
- Has not expired
- Contains a valid user ID
- Passes signature verification

### User Ownership Enforcement
Every operation must verify:
- The user_id in the request matches the user in the JWT token
- The requested task belongs to the authenticated user
- Cross-user access attempts are denied

## Error Response Format
All error responses follow this format:
```json
{
  "success": false,
  "error_message": "Descriptive error message"
}
```

## Performance Contracts
- All operations should complete within 2 seconds (95th percentile)
- MCP tools should handle at least 10 concurrent requests
- Database queries should use appropriate indexing