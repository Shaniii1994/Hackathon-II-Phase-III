# Quickstart: MCP Tools & Backend Integration (Phase-III)

## Overview
This guide provides the essential information to get started with the MCP tools and AI agent integration for the todo application.

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL-compatible database (Neon recommended)
- Better Auth configured
- OpenAI API key
- MCP SDK compatible environment

## Setup Instructions

### 1. Environment Variables
Set up the required environment variables:

```bash
# Backend
export DATABASE_URL="postgresql://..."
export BETTER_AUTH_SECRET="your-jwt-secret"
export OPENAI_API_KEY="sk-..."

# MCP Server Configuration
export MCP_SERVER_HOST="localhost"
export MCP_SERVER_PORT=8001
```

### 2. Backend Installation
Install the backend dependencies:

```bash
cd backend
pip install fastapi sqlmodel uvicorn python-multipart openai python-jose[cryptography] better-auth
pip install @modelcontextprotocol/sdk  # MCP SDK
```

### 3. Database Setup
Initialize the database with the required tables:

```bash
# Run migrations or initialize directly with SQLModel
python -c "
from backend.src.models.task import Task, User, Conversation, Message
from sqlmodel import SQLModel, create_engine
engine = create_engine('your_database_url')
SQLModel.metadata.create_all(engine)
"
```

### 4. Running the MCP Server
Start the MCP server with the task tools:

```bash
cd backend
uvicorn src.mcp_server.server:app --host 0.0.0.0 --port 8001
```

### 5. Starting the Main API
Run the main API that connects the AI agent to the frontend:

```bash
cd backend
uvicorn src.api.chat_api:app --host 0.0.0.0 --port 8000
```

### 6. Frontend Setup
Set up and run the frontend:

```bash
cd frontend
npm install
npm run dev
```

## MCP Tool Usage Examples

### Adding a Task
```python
# Example of what the AI agent will call
result = await mcp_client.call_tool("add_task", {
    "user_id": 1,
    "title": "Buy groceries",
    "description": "Milk, bread, eggs",
    "due_date": "2026-02-08T10:00:00Z"
})
```

### Listing Tasks
```python
# Example of what the AI agent will call
result = await mcp_client.call_tool("list_tasks", {
    "user_id": 1,
    "include_completed": True
})
```

### Updating a Task
```python
# Example of what the AI agent will call
result = await mcp_client.call_tool("update_task", {
    "user_id": 1,
    "task_id": 5,
    "title": "Updated task title",
    "completed": True
})
```

## Integration Points

### Frontend to AI Agent
The frontend communicates with the AI agent through the `/api/{user_id}/chat` endpoint:

```typescript
// Example frontend call
const response = await fetch(`/api/${userId}/chat`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${jwtToken}` },
  body: JSON.stringify({ message: "Add a task to buy groceries" })
});
```

### AI Agent to MCP Tools
The AI agent uses the MCP client to call tools:

```python
# This happens inside the AI agent
def add_task_tool(user_id: int, title: str, description: str = None):
    # Validates user ownership and calls service layer
    return task_service.create_task(user_id, title, description)
```

## Troubleshooting

### Common Issues
1. **Authentication Failures**: Verify JWT token is being passed correctly to all API endpoints
2. **Database Connection**: Ensure DATABASE_URL is properly configured
3. **Tool Registration**: Verify MCP tools are properly registered with the server

### Debugging
Enable debug logging to trace MCP tool calls:

```bash
export LOG_LEVEL=DEBUG
```