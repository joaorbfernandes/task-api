# Task-API

## Project Overview

Task-API is a small project built with FastAPI.

The goal is not only to build a task management API, but also to better understand backend architecture and responsibility boundaries.

This project is being used to explore:

- API design
- validation
- testing
- separation of responsibilities
- service, repository and domain boundaries
- architecture evolution with clear decisions

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

Install dependencies (including test dependencies):

```bash
uv sync --extra dev
```

Start the development server:
```bash
uv run uvicorn app.main:app --reload
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
├── api/          # HTTP layer
├── domain/       # domain entities and rules
├── services/     # application orchestration
├── repositories/ # persistence layer
├── schemas/      # request and response schemas
└── main.py       # application entrypoint
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

The project uses:

- unit tests for isolated behaviour
- integration tests for HTTP and API behaviour
- system tests for basic service checks

Tests follow the AAA pattern:

- Arrange
- Act
- Assert