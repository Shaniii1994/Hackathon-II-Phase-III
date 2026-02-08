---
id: 1
title: project-constitution-init
stage: constitution
date: 2026-01-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: shanisiddiqui
command: /sp.constitution
labels: ["constitution","spec-driven","governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - history/prompts/constitution/001-project-constitution-init.constitution.prompt.md
tests:
 - constitution-validation (semantic versioning applied correctly)
 - template-alignment (all placeholders resolved)
---

## Prompt

# /sp.constitution

## Project
**Todo Full-Stack Web Application (Multi-User, Authenticated, Spec-Driven)**

---

## Core Principles
- **Spec-driven development** (no manual coding; all outputs generated via prompts)
- **Security-first architecture** (JWT-based authentication, strict user isolation)
- **Correctness & consistency** (API behavior matches specification exactly)
- **Reproducibility** (any agent can regenerate the same system from specs)
- **Separation of concerns** (authentication, backend logic, frontend UI clearly isolated)
- **Production readiness** (clean architecture, scalable patterns)

---

## Key Standards
- All features must be explicitly defined in specs before implementation
- No feature outside the written spec may be implemented
- Authentication is mandatory for **all** API endpoints
- JWT tokens must be validated on every backend request
- Task data must always be scoped to the authenticated user
- REST API must follow standard HTTP semantics and status codes
- Frontend must communicate with backend **only** through documented REST APIs
- Environment variables must be used for all secrets (no hard-coded keys)
- All agent outputs must be deterministic and auditable

---

## Technology Constraints
- **Frontend:** Next.js 16+ (App Router)
- **Backend:** Python FastAPI
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** Better Auth (JWT enabled)
- **Auth Transport:** `Authorization: Bearer <JWT>`
- **Spec Workflow:**
  `sp.constitution → sp.specify → plan → tasks → implementation`
- **Coding Rule:** ❌ No manual coding allowed

---

## Functional Constraints
- Must implement **all 5 Basic Level features** as a web application
- Must support **multi-user access with strict isolation**
- Persistent storage is mandatory (no in-memory storage)
- API endpoints must exactly match the defined routes and behaviors
- Backend must reject unauthenticated requests with `401 Unauthorized`
- Task ownership must be enforced on every CRUD operation
- JWT secret must be shared using `BETTER_AUTH_SECRET` in both services

---

## Non-Functional Constraints
- Responsive UI (mobile & desktop)
- Predictable and clear error handling
- Stateless backend authentication
- Token expiry enforced (e.g., 7 days)
- Clean separation between frontend and backend services

---

## Success Criteria
- Users can sign up and sign in successfully
- JWT tokens are issued and validated correctly
- Authenticated users can only view and modify their own tasks
- All REST endpoints behave exactly as specified
- Data persists across sessions using Neon PostgreSQL
- Requests without valid JWT return `401 Unauthorized`
- Entire system can be regenerated from specs without manual changes
- Project passes hackathon review for **process, specifications, and architecture**

## Response snapshot

Constitution successfully created with version 1.0.0. All 6 core principles established: Spec-Driven Development, Security-First Architecture, Correctness & Consistency, Reproducibility, Separation of Concerns, and Production Readiness. Technology constraints, functional constraints, non-functional constraints, and governance procedures documented with semantic versioning. Templates verified for alignment. No template updates required.

## Outcome

- ✅ Impact: Foundation established for spec-driven development workflow with clear governance
- 🧪 Tests: Constitution validation completed - all placeholders resolved, semantic versioning applied correctly
- 📁 Files: .specify/memory/constitution.md (v1.0.0), PHR created
- 🔁 Next prompts: /sp.specify to create feature specification for Todo App
- 🧠 Reflection: Constitution comprehensive with 6 principles covering spec-driven development, security, correctness, reproducibility, separation of concerns, and production readiness. Governance section includes amendment procedures and violation handling.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS (all placeholders resolved, semantic versioning correct, governance complete)
- Prompt variant: N/A (first constitution setup)
- Next experiment: Follow with /sp.specify to validate spec-driven workflow alignment with constitution principles
