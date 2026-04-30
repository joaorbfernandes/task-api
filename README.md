# Task-API

## Project Overview

Task-API is a backend engineering project built with FastAPI to explore clean backend design through a small but structured Task Manager API.

It focuses on:
- layered architecture
- domain-driven business rules
- clear responsibility boundaries
- unit and integration testing
- incremental architecture evolution

## Tech Stack

- [**FastAPI**](https://fastapi.tiangolo.com) — API framework
- [**Pydantic**](https://docs.pydantic.dev) — data validation and schemas
- [**SQLAlchemy**](https://docs.sqlalchemy.org) — ORM and persistence mapping
- [**PostgreSQL**](https://www.postgresql.org) — relational database
- [**Alembic**](https://alembic.sqlalchemy.org) — schema migrations
- [**Uvicorn**](https://uvicorn.dev/) — ASGI server
- [**Pytest**](https://pytest.org) — testing framework
- [**uv**](https://docs.astral.sh/uv/) — package and environment manager

## Requirements

- Python 3.13+
- uv
- PostgreSQL running locally
- a PostgreSQL admin user available for bootstrap

## Setup

Clone the repository:

```bash
git clone https://github.com/joaorbfernandes/task-api.git
cd task-api
```

Install dependencies (including test dependencies):

```bash
uv sync --extra dev
```

Create a local environment file:

```bash
cp .env.example .env
```

Before running the bootstrap step, make sure PostgreSQL is already running locally and accepting connections on the configured `DB_HOST` and `DB_PORT`.

The bootstrap script does not start PostgreSQL for you. It only provisions roles, database, and grants.

Fill in the database credentials in `.env`

Bootstrap the PostgreSQL environment:

```bash
DB_BOOTSTRAP_ADMIN_USER=postgres ./scripts/db/bootstrap_dev.sh
```

After bootstrap, apply all pending migrations:

```bash
alembic upgrade head
```

Start the development server:
```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

API: `http://127.0.0.1:8000`  
Docs: `http://127.0.0.1:8000/docs`

## Run Tests

```bash
uv run pytest
```

## Architecture

The project follows a layered backend structure:

```text
app/
├── main.py
├── api/
│   └── health_router.py
├── core/
│   └── config/
│       ├── settings.py
├── application/
│   └── unit_of_work.py
├── infrastructure/
│   └── db/
│       ├── base.py
│       ├── session_factory.py
│       └── sqlalchemy_unit_of_work.py
└── modules/
    └── tasks/
        ├── api/
        │   ├── dependencies.py
        │   ├── exception_handlers.py
        │   ├── task_router.py
        │   └── task_schemas.py
        ├── application/
        │   ├── task_dtos.py
        │   ├── task_mappers.py
        │   ├── task_repository.py
        │   └── task_service.py
        ├── domain/
        │   ├── task.py
        │   ├── task_errors.py
        │   └── task_status.py
        └── infrastructure/
            ├── in_memory_task_repository.py
            ├── sqlalchemy_task_repository.py
            └── task_model.py
```

 ## API Endpoints

|  Method  |    Endpoint   |      Description      |
|----------|---------------|-----------------------|
|   GET    | `/`           | Service information   |
|   GET    | `/health`     | Health check          | 
|   GET    | `/tasks`      | List tasks            |
|   POST   | `/tasks`      | Create task           |
|   GET    | `/tasks/{id}` | Get task by id        |
|   PUT    | `/tasks/{id}` | Update task           |
|   PATCH  | `/tasks/{id}` | Update task (partial) |
|   DELETE | `/tasks/{id}` | Delete task           |

## Main Features

- create, read, update, patch and delete tasks
- task lifecycle validation
- blocked-state rules
- due date validation
- explicit update flow with change detection
- repository abstraction
- PostgreSQL persistence through SQLAlchemy
- in-memory repository retained for isolated testing
- schema evolution through Alembic migrations

## Example Domain Rules

- title is trimmed and validated
- `IN_PROGRESS` requires `due_date`
- `COMPLETED` requires `due_date`
- `COMPLETED` can't be blocked
- update rejects `PENDING -> IN_PROGRESS` when the target state is blocked
- update rejects `IN_PROGRESS -> COMPLETED` when the target state is blocked
- tasks are only persisted when the state really changes


## Testing Strategy

The project uses:

- unit tests for isolated domain, service, mapper, repository and schema behaviour
- integration tests for HTTP contract and API behaviour

Tests follow the AAA pattern:

- Arrange
- Act
- Assert

## Database Setup and Migrations

### Responsibilities

Database bootstrap and schema migrations are intentionally separated:

- **Bootstrap** creates the PostgreSQL database, roles, and grants
- **Alembic** manages schema creation and schema evolution inside the existing database

### Roles

The project uses two PostgreSQL users per environment:

- **migrator user**: used by Alembic to create and evolve schema objects
- **application user**: used by the API at runtime to read and write application data

The application user should not have schema-change privileges.

### One-time Bootstrap

Before running Alembic, the environment must already contain:

- the target database
- the migrator role/user
- the application role/user
- the required grants for both roles

The project provides bootstrap scripts under:

```text
scripts/db/
```

These scripts create:

- PostgreSQL roles
- the target database
- grants and default privileges

### Migration Workflow

Generate a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe change here"
```

Review the generated migration manually before applying it.

Apply all pending migrations:

```bash
alembic upgrade head
```

Check the current database revision:

```bash
alembic current
```

Show migration history:

```bash
alembic history
```