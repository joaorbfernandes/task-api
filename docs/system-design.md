# TM System Design

## 1. Overview

This project is a **Task Manager API**.

It started as a simple task API and is now being shaped into a small but professional backend project focused on:

- clean API design
- validation
- testing
- architecture evolution
- backend engineering best practices

The goal is to keep the product simple and coherent, without expanding yet into a larger work management platform.

---

## 2. Product Goal

Build a simple and professional task management backend for developers.

The system should make it possible to:

- create tasks
- update tasks
- track task status
- validate input correctly
- evolve the backend with a clean structure

This project is also meant to serve as a strong portfolio example of backend engineering.

---

## 3. Current Scope

Implemented so far:

- FastAPI backend
- Task CRUD API
- request validation with Pydantic
- `TaskStatus` enum
- integration tests with pytest
- boundary validation tests

Still missing:

- service layer
- repository layer
- database persistence
- comments
- authentication
- production readiness

---

## 4. Domain Model

This project focuses on a simple task management domain.

The current domain is intentionally small.

```text
Task
  ↓
Comment
```

Future versions may introduce `User`, but the first focus is to stabilise the task domain itself.

---

## 5. Core Entities

### Task

Represents a unit of work.

Main fields:

- id
- title
- description
- status
- due_date
- created_at
- updated_at

Future fields planned for the first persistent version:
- priority
- created_by
- assigned_to

### Comment

Represents a contextual note or discussion attached to a task.

This entity is planned for a later phase.

Potential fields:

- id
- task_id
- author
- content
- created_at

### User

User support may be introduced later to enable:

- task ownership
- task assignment
- comment authorship

This is not part of the first implementation phase.

---

## 6. Task Status Workflow

The default task workflow is:

- pending
- in_progress
- completed
- cancelled

This workflow is intentionally simple and sufficient for the first version of the project.

---

## 7. Default Domain Rules

The following rules apply to the first version of the system.

- Every task has a title
- A task may have a description
- A task may have a due date
- A task always has a status
- New tasks start with `pending`
- PUT requires full task replacement data
- PATCH supports partial updates
- Comments will belong to tasks
- Users are planned, but not required in the first phase

---

## 8. Initial Architecture

The current architecture is still simple.

```text
API
↓
Application logic
↓
In-memory storage
```

The target architecture for the next phase is:

```text
routers
↓
services / use cases
↓
repositories
↓
database
```

This keeps the project easy to understand while preparing it for proper backend structure.

The architecture should favour dependency injection between routers, services and repositories.

This helps:
- reduce coupling
- improve testability
- support future persistence changes
- allow easier replacement of implementations

---

## 9. Development Strategy

Development will happen in phases.

### Phase 1
Stabilise the current Task API.

### Phase 2
Refactor the architecture:

- service layer
- repository layer
- better separation of concerns

### Phase 3
Add persistence:

- database
- ORM models
- migrations

### Phase 5
Add authentication and task ownership

### Phase 5
Add comments and basic collaboration

### Phase 6
Prepare the project for production:

- Docker
- CI pipeline
- logging
- health improvements

---

## 10. Initial Roadmap

### EPIC-01
Core Task API

### EPIC-02
Architecture Refactor

### EPIC-03
Persistence Layer

### EPIC-04
Authentication and Ownership

### EPIC-05
Comments and Basic Collaboration

### EPIC-06
Production Readiness

---

## 11. Closed Decisions

The following decisions are already defined.

- The domain will stay centred on `Task`
- The task workflow will remain simple in the initial versions
- Comments will be introduced after authentication
- Priority will be part of the first persistent version of Task
- Categories and tags will not be part of the first release
- Task ownership will start with created_by
- assigned_to will be introduced later
- created_by and assigned_to are part of the future Task model, not the current implementation