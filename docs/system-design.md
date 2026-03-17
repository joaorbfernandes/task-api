# TM System Design

## Overview

TM is a Task Manager API built as a backend engineering project.

The goal is to keep the product small and clear while evolving the internal architecture in a professional way.

## Focus

The project focuses on:

- task CRUD operations
- request validation
- testing
- architecture refactoring
- domain and persistence separation
- layered backend structure

## Architecture

The current structure is:

```text
routers
↓
services
↓
domain
↓
repositories
↓
in-memory storage
```

Responsibilities are separated as follows:
- routers handle HTTP concerns
- services orchestrate application behaviour
- repositories handle persistence
- domain entities hold business rules

## Core Domain

The system is currently centred on `Task`.

The domain is responsible for task behaviour and business rules.

This includes decisions such as:

- task lifecycle
- state changes
- editability rules
- domain-level consistency

Other entities such as comments or users may be introduced later, but they are not part of the current core scope.

### Task Rules

#### Main lifecycle status

| Status |
|---|
| `PENDING` |
| `IN_PROGRESS` |
| `COMPLETED` |
| `CANCELLED` |

#### Additional condition

| Condition | Meaning |
|---|---|
| `is_blocked` | Indicates that the task is temporarily blocked |

#### Status transitions

| From | To | Allowed | Notes |
|---|---|---|---|
| `PENDING` | `IN_PROGRESS` | Yes | If blocked, this transition clears `is_blocked` |
| `PENDING` | `CANCELLED` | Yes |  |
| `PENDING` | `COMPLETED` | No |  |
| `IN_PROGRESS` | `COMPLETED` | Yes |  |
| `IN_PROGRESS` | `CANCELLED` | Yes | If blocked, this transition clears `is_blocked` |
| `IN_PROGRESS` | `PENDING` | No |  |
| `COMPLETED` | any | No | Terminal state |
| `CANCELLED` | any | No | Terminal state |

#### Block rules

| Rule | Allowed |
|---|---|
| Block task in `PENDING` | Yes |
| Block task in `IN_PROGRESS` | Yes |
| Block task in `COMPLETED` | No |
| Block task in `CANCELLED` | No |
| Change status while blocked | No, except explicit allowed transitions |

##### Blocked operations

| Operation | Allowed | Result |
|---|---|---|
| Set `is_blocked=True` in `PENDING` | Yes | Task becomes blocked |
| Set `is_blocked=True` in `IN_PROGRESS` | Yes | Task becomes blocked |
| Set `is_blocked=True` in `COMPLETED` | No | Invalid domain operation |
| Set `is_blocked=True` in `CANCELLED` | No | Invalid domain operation |
| Set `is_blocked=False` when blocked | Yes | Task becomes unblocked |
| Set `is_blocked=False` when already unblocked | Yes | No real change |

##### Blocked status transition behaviour

| Current state | `is_blocked` | Target state | Allowed | Side effect |
|---|---|---|---|---|
| `PENDING` | `True` | `IN_PROGRESS` | Yes | Set `is_blocked=False` |
| `PENDING` | `True` | `CANCELLED` | No |  |
| `IN_PROGRESS` | `True` | `COMPLETED` | No |  |
| `IN_PROGRESS` | `True` | `CANCELLED` | Yes | Set `is_blocked=False` |
| `PENDING` | `True` | `COMPLETED` | No |  |
| `IN_PROGRESS` | `True` | `PENDING` | No |  |

#### Editability rules

| Status | Editable |
|---|---|
| `PENDING` | Yes |
| `IN_PROGRESS` | Yes |
| `COMPLETED` | No |
| `CANCELLED` | No |

#### Due date rules

| Rule |
|---|
| `due_date` cannot be earlier than the current date |
| `due_date` is required for transition to or persistence in `IN_PROGRESS` |
| `due_date` cannot be changed in `COMPLETED` |
| `due_date` cannot be changed in `CANCELLED` |

#### Persistence rule

| Rule |
|---|
| Persist only when the final task state actually changes |

## Roadmap

- EPIC-01 Core Task API
- EPIC-02 Architecture Refactor
- EPIC-03 Persistence Layer
- EPIC-04 Authentication and Ownership
- EPIC-05 Comments and Basic Collaboration
- EPIC-06 Production Readiness