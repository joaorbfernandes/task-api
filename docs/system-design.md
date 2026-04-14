# TM System Design

## Overview

Task-API is a Task Manager API built as a backend engineering project.

The goal is to keep the product small and clear while evolving the internal architecture.

## Project Structure

```text
app/
├── main.py
├── api/
│   └── health_router.py
└── modules/
    └── tasks/
        ├── api/
        ├── application/
        ├── domain/
        └── infrastructure/
```

## General Flow

`Router → Schema → Service → Domain → Repository → Persistence`

## Layer Responsibilities

- Router handles HTTP concerns
- Schema validates request and response data
- Service coordinates the use case
- Domain enforces business rules and state consistency
- Repository abstracts persistence
- Persistence stores application data

## Endpoints

### POST /tasks

`Router → Schema → Mapper → DTO [TaskInput] → Service.create_task() → Task.create() → Repository → In-memory`

### GET /tasks

`Router → Service.list_tasks() → Repository → In-memory`

### GET /tasks/{id}

`Router → Service.get_task() → Repository → In-memory`

### DELETE /tasks/{id}

`Router → Service.delete_task() → Repository → In-memory`

### PUT /tasks/{id}

`Router → Schema → Mapper → DTO [TaskInput] → Service.update_task() → Service._apply_update() → Task.update() → Repository.save_task()`

### PATCH /tasks/{id}

`Router → Schema → Mapper → DTO [PatchTaskInput] → Service.patch_task() → merge current state with patch → Service._apply_update() → Task.update() → Repository.save_task()`

### PUT/PATCH Shared Update Flow

```text
Task.update(...)
├─ _ensure_editable()             → blocks updates for terminal tasks
├─ _validate_title()              → trims and validates title
├─ _validate_status_transition()  → validates status changes when needed
├─ _validate_blocked_transition() → validates blocked transition rules when needed
└─ _validate_final_state()        → validates final task state consistency
   ├─ _validate_due_date()        → validates due date rules
   └─ _validate_blocked_state()   → validates blocked state rules

If changed:
Service → Task.mark_updated() → Repository.save_task()
```

## Core Domain

### Task
id · title · description · status · due_date · created_at · updated_at · is_blocked

#### Status

PENDING · IN_PROGRESS · COMPLETED · CANCELLED

#### Editable status

PENDING · IN_PROGRESS

#### Terminal status

COMPLETED · CANCELLED

#### Task Lifecycle

```text
   ┌────────────────────┐
   ▼                    │
PENDING ─────────▶ IN_PROGRESS ─────────▶ COMPLETED
   │                    │
   │                    └───────────────▶ CANCELLED
   │                                           ▲
   └───────────────────────────────────────────┘
```

Note:

- blocked tasks follow extra transition restrictions during update

#### Current Task Rules
- title is trimmed and cannot be empty 
- title must be at least 3 characters long
- title must be at most 120 characters long
- IN_PROGRESS requires due_date
- COMPLETED requires due_date
- due_date cannot be in the past
- COMPLETED cannot remain blocked
- blocked tasks have extra transition restrictions
- updates are fully validated before changes are applied
- tasks are saved only when the state really changes

## Persistence

Current:

- repository abstraction
- in-memory persistence

Next step:

- PostgreSQL persistence

## Direction

The project is evolving in small steps:

- keep domain rules explicit
- keep the architecture simple
- replace in-memory persistence with PostgreSQL
- prepare the base for future features such as authentication and ownership