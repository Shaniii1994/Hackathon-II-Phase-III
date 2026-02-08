# Implementation Tasks: MCP Tools & Backend Integration (Phase-III)

**Branch**: `002-mcp-tools-backend` | **Date**: 2026-02-08 | **Spec**: [specs/002-mcp-tools-backend/spec.md](../../specs/002-mcp-tools-backend/spec.md)
**Input**: Implementation plan from `/specs/002-mcp-tools-backend/plan.md`

**Note**: This template is filled in by the `/sp.tasks` command. See `.specify/templates/commands/tasks.md` for the execution workflow.

## Task List

### Phase 1: MCP Server Infrastructure Setup

#### Task 1.1: Install MCP SDK Dependencies
- **Objective**: Set up the MCP SDK and related dependencies in the backend
- **Files to modify**: `backend/requirements.txt`, `backend/pyproject.toml` (if exists)
- **Acceptance Criteria**:
  - MCP SDK is installed and importable
  - All required dependencies are listed
  - Version compatibility is ensured with existing packages
- **Test**: Verify MCP SDK can be imported in a Python shell

#### Task 1.2: Create MCP Server Base Structure
- **Objective**: Implement the basic MCP server structure
- **Files to create**: `backend/src/mcp_server/server.py`
- **Acceptance Criteria**:
  - Server can start without errors
  - Basic configuration is set up
  - Logging is configured
- **Test**: Server starts successfully and shows startup logs

#### Task 1.3: Define MCP Tool Request/Response Models
- **Objective**: Create Pydantic models for MCP tool communication based on data-model.md
- **Files to create**: `backend/src/models/mcp_models.py`
- **Acceptance Criteria**:
  - All required request/response models are defined
  - Models match the contracts in contracts/task-contracts.md
  - Proper validation is implemented
- **Test**: Models validate correctly with sample data

### Phase 2: MCP Tool Implementation

#### Task 2.1: Implement add_task MCP Tool
- **Objective**: Create the add_task tool that creates new tasks in the database
- **Files to create**: `backend/src/mcp_server/tools/add_task.py`
- **Files to modify**: `backend/src/mcp_server/server.py`
- **Acceptance Criteria**:
  - Tool accepts user_id, title, description, and due_date parameters
  - Creates task in database with proper user association
  - Returns success response with task_id
  - Enforces user ownership
  - Follows contract in contracts/task-contracts.md
- **Test**: Tool successfully creates a task when called with valid parameters

#### Task 2.2: Implement list_tasks MCP Tool
- **Objective**: Create the list_tasks tool that retrieves user's tasks
- **Files to create**: `backend/src/mcp_server/tools/list_tasks.py`
- **Files to modify**: `backend/src/mcp_server/server.py`
- **Acceptance Criteria**:
  - Tool accepts user_id and optional filters
  - Returns only tasks belonging to the specified user
  - Applies include_completed filter correctly
  - Respects limit and offset parameters
  - Follows contract in contracts/task-contracts.md
- **Test**: Tool returns only the correct user's tasks with proper filtering

#### Task 2.3: Implement complete_task MCP Tool
- **Objective**: Create the complete_task tool that updates task completion status
- **Files to create**: `backend/src/mcp_server/tools/complete_task.py`
- **Files to modify**: `backend/src/mcp_server/server.py`
- **Acceptance Criteria**:
  - Tool accepts user_id and task_id parameters
  - Updates task completion status in database
  - Enforces user ownership (can only complete own tasks)
  - Returns success response with task_id
  - Follows contract in contracts/task-contracts.md
- **Test**: Tool successfully updates completion status for user's own task

#### Task 2.4: Implement delete_task MCP Tool
- **Objective**: Create the delete_task tool that removes tasks from database
- **Files to create**: `backend/src/mcp_server/tools/delete_task.py`
- **Files to modify**: `backend/src/mcp_server/server.py`
- **Acceptance Criteria**:
  - Tool accepts user_id and task_id parameters
  - Removes task from database
  - Enforces user ownership (can only delete own tasks)
  - Returns success response
  - Follows contract in contracts/task-contracts.md
- **Test**: Tool successfully deletes user's own task from database

#### Task 2.5: Implement update_task MCP Tool
- **Objective**: Create the update_task tool that modifies task properties
- **Files to create**: `backend/src/mcp_server/tools/update_task.py`
- **Files to modify**: `backend/src/mcp_server/server.py`
- **Acceptance Criteria**:
  - Tool accepts user_id, task_id, and optional update parameters
  - Updates specified task properties in database
  - Enforces user ownership (can only update own tasks)
  - Returns success response with task_id
  - Follows contract in contracts/task-contracts.md
- **Test**: Tool successfully updates task properties for user's own task

### Phase 3: Authentication and Authorization

#### Task 3.1: Create MCP Authentication Middleware
- **Objective**: Implement authentication middleware for MCP tools
- **Files to create**: `backend/src/mcp_server/auth.py`
- **Acceptance Criteria**:
  - Validates JWT tokens from MCP tool requests
  - Extracts user_id from token
  - Returns appropriate errors for invalid tokens
  - Integrates with existing auth_service
- **Test**: Middleware correctly authenticates valid tokens and rejects invalid ones

#### Task 3.2: Implement User Ownership Enforcement
- **Objective**: Ensure all MCP tools verify user ownership of tasks
- **Files to modify**: All tool files in `backend/src/mcp_server/tools/`
- **Acceptance Criteria**:
  - Each tool verifies the task belongs to the authenticated user
  - Appropriate errors are returned for cross-user access attempts
  - Existing service layer functions are reused where possible
- **Test**: Attempts to access another user's tasks are properly rejected

### Phase 4: Conversation Tracking

#### Task 4.1: Extend Database Models for Conversations
- **Objective**: Add Conversation and Message models to database
- **Files to modify**: `backend/src/models/__init__.py`, `backend/src/models/conversation.py`
- **Acceptance Criteria**:
  - Conversation model with user relationship is defined
  - Message model with conversation relationship is defined
  - Proper indexes are added for performance
  - Models match data-model.md specification
- **Test**: Models can be created and queried in database

#### Task 4.2: Create Conversation Services
- **Objective**: Implement services for managing conversations and messages
- **Files to create**: `backend/src/services/conversation_service.py`
- **Acceptance Criteria**:
  - Functions to create conversations
  - Functions to add messages to conversations
  - Functions to retrieve conversation history
  - Proper error handling is implemented
- **Test**: Conversation and message CRUD operations work correctly

### Phase 5: AI Agent Integration

#### Task 5.1: Create Chat API Endpoint
- **Objective**: Implement API endpoint for frontend to communicate with AI agent
- **Files to create**: `backend/src/api/chat_api.py`
- **Acceptance Criteria**:
  - Accepts user messages and JWT authentication
  - Processes messages through AI agent
  - AI agent can call MCP tools based on message content
  - Returns AI agent responses to frontend
- **Test**: API successfully processes a message and returns an AI response

#### Task 5.2: Integrate AI Agent with MCP Tools
- **Objective**: Connect the AI agent to use MCP tools for task operations
- **Files to create**: `backend/src/ai_agent/agent.py`
- **Files to modify**: `backend/src/api/chat_api.py`
- **Acceptance Criteria**:
  - AI agent can parse natural language requests
  - AI agent calls appropriate MCP tools based on user requests
  - AI agent provides appropriate responses based on tool results
  - Conversation context is maintained
- **Test**: AI agent correctly interprets "Add a task to buy groceries" and calls add_task tool

### Phase 6: Frontend Integration

#### Task 6.1: Create ChatKit Component Structure
- **Objective**: Set up the basic ChatKit component structure in frontend
- **Files to create**: 
  - `frontend/src/components/ChatKit/ChatWindow.tsx`
  - `frontend/src/components/ChatKit/Message.tsx`
  - `frontend/src/components/ChatKit/TaskDisplay.tsx`
- **Acceptance Criteria**:
  - Components are properly structured and styled
  - Message display functionality is implemented
  - Basic chat interface is responsive
- **Test**: Chat window renders without errors

#### Task 6.2: Implement AI Agent Service
- **Objective**: Create service to communicate with AI agent backend
- **Files to create**: `frontend/src/services/ai-agent-service.ts`
- **Acceptance Criteria**:
  - Service can send messages to backend API
  - Service can receive and process AI responses
  - Error handling is implemented
  - Authentication headers are properly included
- **Test**: Service successfully sends a message and receives a response

#### Task 6.3: Integrate ChatKit with AI Agent Service
- **Objective**: Connect ChatKit UI with AI agent service
- **Files to modify**: `frontend/src/components/ChatKit/ChatWindow.tsx`
- **Acceptance Criteria**:
  - Messages typed in UI are sent to AI agent
  - AI responses are displayed in chat window
  - Loading states are shown during processing
  - Error states are handled appropriately
- **Test**: Full chat interaction cycle works from UI to AI agent and back

### Phase 7: Testing and Validation

#### Task 7.1: Unit Tests for MCP Tools
- **Objective**: Write unit tests for all MCP tools
- **Files to create**: `backend/tests/unit/test_mcp_tools.py`
- **Acceptance Criteria**:
  - Each MCP tool has comprehensive unit tests
  - Tests cover success and error cases
  - Mock objects are used appropriately
  - Test coverage is >90% for MCP tools
- **Test**: All unit tests pass

#### Task 7.2: Integration Tests for AI Agent
- **Objective**: Write integration tests for AI agent functionality
- **Files to create**: `backend/tests/integration/test_chat_api.py`
- **Acceptance Criteria**:
  - Tests verify end-to-end functionality
  - Natural language inputs are processed correctly
  - MCP tools are called as expected
  - Responses are returned properly
- **Test**: All integration tests pass

#### Task 7.3: Contract Tests for Task Operations
- **Objective**: Verify all task operations follow the defined contracts
- **Files to create**: `backend/tests/contract/test_task_contracts.py`
- **Acceptance Criteria**:
  - Tests verify all contract requirements are met
  - Error conditions return appropriate responses
  - Success conditions return expected formats
  - Authentication and authorization are enforced
- **Test**: All contract tests pass

### Phase 8: Documentation and Deployment

#### Task 8.1: Update API Documentation
- **Objective**: Document the new MCP server and chat API endpoints
- **Files to modify**: Update relevant README files
- **Acceptance Criteria**:
  - API endpoints are documented with request/response examples
  - Authentication requirements are explained
  - Usage examples are provided
- **Test**: Documentation is clear and accurate

#### Task 8.2: Environment Configuration
- **Objective**: Set up environment variables and configuration for MCP server
- **Files to modify**: `.env.example`, `backend/.env`, `backend/src/core/config.py`
- **Acceptance Criteria**:
  - All required environment variables are defined
  - MCP server configuration is properly set up
  - Default values are provided where appropriate
- **Test**: MCP server starts with configuration values

## Dependencies

- Task 1.1 must be completed before Tasks 1.2, 1.3
- Task 1.2 must be completed before Tasks 2.1-2.5
- Task 1.3 must be completed before Tasks 2.1-2.5
- Tasks 2.1-2.5 can be worked on in parallel after 1.2 and 1.3
- Task 3.1 should be completed before Tasks 2.1-2.5 are finalized
- Task 4.1 should be completed before Task 5.1
- Task 5.1 should be completed before Tasks 6.2, 6.3
- Task 6.1 should be completed before Task 6.3
- Tasks 7.1-7.3 can be done in parallel after their respective implementation phases

## Success Metrics

- All MCP tools function according to contracts
- User ownership is enforced for all operations
- AI agent can successfully process natural language requests
- Frontend ChatKit integrates seamlessly with backend
- All tests pass (>90% coverage)
- Performance meets requirements (<2s response time)