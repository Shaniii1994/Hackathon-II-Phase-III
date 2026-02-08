---

description: "Task list for Todo Full-Stack Web Application implementation"
---

# Tasks: Todo Full-Stack Web Application (Authenticated, Multi-User)

**Input**: Design documents from `/specs/001-auth-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests not explicitly requested in spec - optional inclusion

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Tasks use web application structure as defined in constraints

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project directories for backend and frontend at repository root
- [ ] T002 Initialize Python backend project with FastAPI dependencies in backend/
- [ ] T003 Initialize Next.js frontend project with App Router in frontend/
- [ ] T004 [P] Create requirements.txt for backend Python dependencies
- [ ] T005 [P] Create package.json for frontend Node dependencies
- [ ] T006 [P] Create .env.example template with BETTER_AUTH_SECRET placeholder
- [ ] T007 [P] Create .gitignore files for both backend and frontend

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Setup database connection to Neon PostgreSQL in backend/src/db/connection.py
- [ ] T009 [P] Create User SQLModel in backend/src/models/user.py with email, password_hash, id fields
- [ ] T010 [P] Create Task SQLModel in backend/src/models/task.py with title, description, due_date, is_complete, user_id, id fields
- [ ] T011 [P] Implement JWT verification middleware in backend/src/middleware/auth.py
- [ ] T012 [P] Setup FastAPI routing structure in backend/src/api/router.py
- [ ] T013 Configure error handling in backend/src/core/exceptions.py
- [ ] T014 Configure logging in backend/src/core/logging.py
- [ ] T015 Setup environment configuration management in backend/src/core/config.py
- [ ] T016 Create database initialization script in backend/src/db/init_db.py
- [ ] T017 Create main FastAPI application entry point in backend/main.py
- [ ] T018 [P] Configure Better Auth in frontend with JWT plugin in frontend/src/lib/auth.ts
- [ ] T019 [P] Create frontend API client in frontend/src/lib/api-client.ts for attaching JWT to requests
- [ ] T020 Create base layout component in frontend/src/app/layout.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Login (Priority: P1) 🎯 MVP

**Goal**: Enable users to register accounts and login with secure JWT tokens

**Independent Test**: Create account, logout, login again, verify session persists and JWT is issued

### Implementation for User Story 1

- [ ] T021 [US1] Implement user registration service in backend/src/services/user_service.py
- [ ] T022 [US1] Implement user login service in backend/src/services/auth_service.py
- [ ] T023 [US1] Create registration API endpoint POST /api/auth/register in backend/src/api/auth.py
- [ ] T024 [US1] Create login API endpoint POST /api/auth/login in backend/src/api/auth.py
- [ ] T025 [US1] Add password hashing to registration service in backend/src/services/user_service.py
- [ ] T026 [US1] Add JWT token generation to login service in backend/src/services/auth_service.py
- [ ] T027 [US1] Create registration page component in frontend/src/app/register/page.tsx
- [ ] T028 [US1] Create login page component in frontend/src/app/login/page.tsx
- [ ] T029 [US1] Integrate Better Auth signup in registration page in frontend/src/app/register/page.tsx
- [ ] T030 [US1] Integrate Better Auth signin in login page in frontend/src/app/login/page.tsx
- [ ] T031 [US1] Add form validation for email and password in both auth pages
- [ ] T032 [US1] Add error handling and display for auth failures
- [ ] T033 [US1] Create home/redirect page in frontend/src/app/page.tsx
- [ ] T034 [US1] Add protected route check in frontend layout to redirect unauthenticated users
- [ ] T035 [US1] Store JWT token in frontend state after successful login

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task Creation and List View (Priority: P1)

**Goal**: Enable authenticated users to create tasks and view their task list

**Independent Test**: Login, create multiple tasks, verify all appear in list with correct details

### Implementation for User Story 2

- [ ] T036 [P] [US2] Create task service in backend/src/services/task_service.py
- [ ] T037 [P] [US2] Create GET /api/{user_id}/tasks endpoint in backend/src/api/tasks.py
- [ ] T038 [P] [US2] Create POST /api/{user_id}/tasks endpoint in backend/src/api/tasks.py
- [ ] T039 [US2] Add task ownership validation to task service in backend/src/services/task_service.py
- [ ] T040 [US2] Add task title validation to creation endpoint in backend/src/api/tasks.py
- [ ] T041 [US2] Create task list page in frontend/src/app/tasks/page.tsx
- [ ] T042 [US2] Create task creation form component in frontend/src/components/TaskForm.tsx
- [ ] T043 [US2] Create task list display component in frontend/src/components/TaskList.tsx
- [ ] T044 [US2] Integrate API client to fetch tasks in task list page
- [ ] T045 [US2] Integrate API client to create tasks in task form component
- [ ] T046 [US2] Add loading states for task operations
- [ ] T047 [US2] Add error handling and display for task operations
- [ ] T048 [US2] Add due date input to task creation form
- [ ] T049 [US2] Style task list to be responsive for mobile and desktop

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently (MVP complete)

---

## Phase 5: User Story 3 - Task Completion Toggle (Priority: P2)

**Goal**: Enable users to mark tasks as complete or incomplete

**Independent Test**: Create task, mark complete, toggle back to incomplete, verify status persists

### Implementation for User Story 3

- [ ] T050 [US3] Create PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/src/api/tasks.py
- [ ] T051 [US3] Add completion status toggle to task service in backend/src/services/task_service.py
- [ ] T052 [US3] Add ownership check to completion endpoint in backend/src/api/tasks.py
- [ ] T053 [US3] Update task list component to show completion status in frontend/src/components/TaskList.tsx
- [ ] T054 [US3] Add completion toggle button/checkbox in task list item
- [ ] T055 [US3] Add visual styling for completed tasks (strikethrough, dimmed)
- [ ] T056 [US3] Integrate API client to toggle task completion
- [ ] T057 [US3] Add optimistic UI update for completion toggle
- [ ] T058 [US3] Add error handling for completion toggle failure

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Task Editing (Priority: P2)

**Goal**: Enable users to modify task details

**Independent Test**: Create task, edit title/description/due date, verify changes persist

### Implementation for User Story 4

- [ ] T059 [US4] Create PUT /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py
- [ ] T060 [US4] Add task update method to task service in backend/src/services/task_service.py
- [ ] T061 [US4] Add ownership check to update endpoint in backend/src/api/tasks.py
- [ ] T062 [US4] Create task edit form component in frontend/src/components/TaskEditForm.tsx
- [ ] T063 [US4] Add edit button to task list items in frontend/src/components/TaskList.tsx
- [ ] T064 [US4] Create task edit page/modal in frontend/src/app/tasks/[id]/edit/page.tsx
- [ ] T065 [US4] Pre-fill edit form with existing task data
- [ ] T066 [US4] Integrate API client to update task
- [ ] T067 [US4] Add validation to task edit form
- [ ] T068 [US4] Add loading and error states for task edit

**Checkpoint**: All 4 user stories should now be independently functional

---

## Phase 7: User Story 5 - Task Deletion (Priority: P3)

**Goal**: Enable users to remove tasks

**Independent Test**: Create task, delete it, verify it's removed from list and database

### Implementation for User Story 5

- [ ] T069 [US5] Create DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/api/tasks.py
- [ ] T070 [US5] Add task delete method to task service in backend/src/services/task_service.py
- [ ] T071 [US5] Add ownership check to delete endpoint in backend/src/api/tasks.py
- [ ] T072 [US5] Add delete button to task list items in frontend/src/components/TaskList.tsx
- [ ] T073 [US5] Add confirmation dialog for deletion
- [ ] T074 [US5] Integrate API client to delete task
- [ ] T075 [US5] Add optimistic UI update for deletion
- [ ] T076 [US5] Add error handling for deletion failure

**Checkpoint**: All 5 user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T077 [P] Add empty state message when no tasks exist in frontend/src/components/TaskList.tsx
- [ ] T078 [P] Add logout functionality in frontend with JWT cleanup
- [ ] T079 [P] Add navigation between pages in frontend layout
- [ ] T080 Ensure all API endpoints return correct HTTP status codes
- [ ] T081 Verify all endpoints require valid JWT authentication
- [ ] T082 Verify user isolation - users cannot access other users' tasks
- [ ] T083 Add responsive design validation for mobile viewport
- [ ] T084 Add responsive design validation for desktop viewport
- [ ] T085 Test task data persistence across login/logout cycles
- [ ] T086 Create README.md with setup instructions
- [ ] T087 Create environment variable documentation
- [ ] T087 Run full end-to-end validation of all 5 user stories

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in priority order (P1 → P2 → P3)
  - US1 and US2 are both P1, but US1 (auth) must complete before US2 (tasks)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - Foundation for all other stories
- **User Story 2 (P1)**: Depends on US1 completion (requires auth)
- **User Story 3 (P2)**: Depends on US2 completion (requires tasks)
- **User Story 4 (P2)**: Depends on US2 completion (requires tasks)
- **User Story 5 (P3)**: Depends on US2 completion (requires tasks)

### Within Each User Story

- Backend services before API endpoints
- API endpoints before frontend components
- Core components before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- US3, US4, and US5 can be implemented in parallel after US2 completes
- Different user story phases can be worked on in parallel by different team members

---

## Parallel Example: User Story 2

```bash
# Launch task service creation and API endpoints together:
Task: "Create task service in backend/src/services/task_service.py"
Task: "Create GET /api/{user_id}/tasks endpoint in backend/src/api/tasks.py"
Task: "Create POST /api/{user_id}/tasks endpoint in backend/src/api/tasks.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1-2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Auth)
4. Complete Phase 4: User Story 2 (Task CRUD)
5. **STOP and VALIDATE**: Test MVP independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Secure auth available
3. Add User Story 2 → Test independently → Deploy/Demo (MVP!)
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Auth)
3. After US1 completes:
   - Developer A: User Story 2 (Tasks)
   - Developer B: User Story 3 (Completion)
4. After US2 completes:
   - Developer B: User Story 4 (Edit)
   - Developer C: User Story 5 (Delete)
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Total tasks: 87
- MVP scope: T001-T035 (35 tasks for user registration and authentication)
