# Data Model: MCP Tools & Backend Integration (Phase-III)

## Task Model
The core Task entity remains largely unchanged from Phase-II but will be enhanced to support MCP tool interactions:

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key to user
    user_id: int = Field(foreign_key="user.id")

    # Relationship
    user: User = Relationship(back_populates="tasks")
```

## User Model
The User entity from Phase-II remains the same but will be used for ownership validation:

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    tasks: List[Task] = Relationship(back_populates="user")
```

## Conversation Model
New model to track AI agent conversations:

```python
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=200)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key relationship
    user: User = Relationship(back_populates="conversations")

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversation.id")
    role: str = Field(regex="^(user|assistant|system)$")  # user, assistant, or system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    conversation: Conversation = Relationship(back_populates="messages")
```

## MCP Tool Request/Response Models
Models for MCP tool communication:

```python
class AddTaskRequest(BaseModel):
    user_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None

class AddTaskResponse(BaseModel):
    success: bool
    task_id: Optional[int] = None
    error_message: Optional[str] = None

class ListTasksRequest(BaseModel):
    user_id: int
    completed_only: Optional[bool] = None
    include_completed: Optional[bool] = True

class ListTasksResponse(BaseModel):
    success: bool
    tasks: List[Task]
    error_message: Optional[str] = None

class CompleteTaskRequest(BaseModel):
    user_id: int
    task_id: int
    completed: bool = True

class CompleteTaskResponse(BaseModel):
    success: bool
    task_id: Optional[int] = None
    error_message: Optional[str] = None

class DeleteTaskRequest(BaseModel):
    user_id: int
    task_id: int

class DeleteTaskResponse(BaseModel):
    success: bool
    error_message: Optional[str] = None

class UpdateTaskRequest(BaseModel):
    user_id: int
    task_id: int
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None

class UpdateTaskResponse(BaseModel):
    success: bool
    task_id: Optional[int] = None
    error_message: Optional[str] = None
```

## Database Relationships
The data model maintains the same relationships established in Phase-II:
- User (1) → (*) Task (many tasks per user)
- User (1) → (*) Conversation (many conversations per user)
- Conversation (1) → (*) Message (many messages per conversation)

## Indexing Strategy
- Primary indexes on all ID fields
- Foreign key indexes for efficient joins
- User ID index on Task table for fast user-specific queries
- Timestamp indexes for chronological ordering