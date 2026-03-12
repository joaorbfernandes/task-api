# Task-API

## Project Overview

Simple task management API built with FastAPI.

Features:
- CRUD operations
- input validation with Pydantic
- integration tests with pytest
- in-memory storage

## Tech Stack

- [**FastAPI**](https://fastapi.tiangolo.com) — API framework
- [Pydantic](https://docs.pydantic.dev) — data validation and schemas
- [Uvicorn](https://uvicorn.dev/) — ASGI server
- [Pytest](https://pytest.org) — testing framework
- [uv](https://docs.astral.sh/uv/) — package and environment manager

## Requirements

- Python 3.13+
- uv

## Setup

Clone the repository:

```bash
git clone https://github.com/joaorbfernandes/task-api.git
cd task-api
```

Install dependencies
```bash
uv sync
```

Start the development server:
```bash
uv sync --extra dev
```

```bash
uv run uvicorn app.main:app --reload
```

Install development dependencies (required for tests):

```markdown
API available at: 
http://127.0.0.1:8000

Interactive docs: 
http://127.0.0.1:8000/docs
```

## Run Tests

```bash
uv run pytest
```

## Project Structure

```bash
app/
├── main.py
├── api/
│ └── routers
│ ├── health.py
│ └── tasks.py
└── schemas/
└── task.py

tests/
├── conftest.py
├── system/
└── test_health.py
└── tasks/
├── test_tasks_create.py
├── test_tasks_read.py
├── test_tasks_update.py
├── test_tasks_delete.py
└── test_tasks_validation.py
```

## API Endpoints

|  Method  |    Endpoint   |      Description      |
|----------|---------------|-----------------------|
|   GET    | `/`           | Service information   |
|   GET    | `/health`     | Health check          | 
|   GET    | `/tasks`      | List tasks            |
|   POST   | `/tasks`      | Create task           |
|   GET    | `/tasks/{id}` | Get task by id        |
|   PUT    | `/tasks/{id}` | Update task (replace) |
|   PATCH  | `/tasks/{id}` | Update task (partial) |
|   DELETE | `/tasks/{id}` | Delete task           |

## Testing Strategy

Integration tests using pytest and FastAPI TestClient.

The API is tested through HTTP requests, validating routes, input validation and responses.

Tests follow the AAA pattern (Arrange, Act, Assert).

Fixtures:
- client
- create_task

Test coverage includes:

- CRUD operations
- validation errors
- edge cases
- boundary validations