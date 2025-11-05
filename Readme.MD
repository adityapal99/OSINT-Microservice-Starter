# OSINT Microservice Template

Version: 1.1.0

## Overview

This repository provides a structured template for building OSINT-focused backend microservices using:

* **FastAPI** for HTTP APIs
* **Celery** for asynchronous task execution
* **Redis** as message broker / result backend
* **Pydantic Settings** for configuration
* **Docker / Docker Compose** for containerized development

The template enforces consistent structure, enabling new services to be developed with minimal effort and maximum maintainability.

---

# Directory Structure

```
app/
  core/
    config.py          # Environment + application settings
    celery_app.py      # Global Celery instance
    logging.py         # Logging utility
  api/
    routes/
      analyze.py       # API routes
    schemas/
      analyze.py       # Pydantic request/response models
  services/
    logic.py           # Business logic
  tasks/
    analyze.py         # Celery task wrapping service logic
  models/              # Database models (optional)
  __init__.py
  main.py              # FastAPI initialization, router registration
tests/                 # Unit tests
.env                   # Environment variables
Dockerfile
docker-compose.yaml
requirements.txt
start-dev.sh
README.md
```

## Layer Responsibilities

| Layer       | Purpose                         |
| ----------- | ------------------------------- |
| `core/`     | Config, logging, shared objects |
| `api/`      | Request routing + serialization |
| `schemas/`  | Input/output validation         |
| `services/` | Business logic                  |
| `tasks/`    | Celery async tasks              |
| `models/`   | Database models (optional)      |

---

# Configuration

Located at `app/core/config.py`

Settings are managed with Pydantic’s `BaseSettings`, supported by `.env`.

```python
SECRET_KEY="..."
CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"
```

Override via environment variables when deploying.

---

# Celery

Celery is initialized once in `app/core/celery_app.py`.

```python
from app.core.celery_app import celery_app
```

Tasks auto-discover under `app/tasks/`.

Task naming convention:

```
app.tasks.<module>.<task name>
```

---

# API

FastAPI application is defined in `app/main.py`.

Routers are stored in:

```
app/api/routes/
```

### Sample router

`app/api/routes/analyze.py`

Provides:

* `/analyze` to enqueue work
* `/results/{task_id}` to poll results

All inputs must be validated with Pydantic schemas from:

```
app/api/schemas/
```

---

# Background Tasks

Long-running work must always be executed asynchronously using Celery.

A standard task lives at:

```
app/tasks/<module>.py
```

Example task:

```python
@celery_app.task(name="app.tasks.analyze.run_analysis")
def run_analysis(payload: dict):
    result = process_identifier(payload["identifier"])
    return {"status": "complete", "data": result}
```

The task delegates processing to `services/logic.py`.

---

# Business Logic

All OSINT-specific processing belongs under:

```
app/services/
```

Separation ensures:

* API layer stays minimal
* Task layer remains light
* Logic can be reused / tested independently

Example:

```python
def process_identifier(identifier: str):
    return {"message": f"Processed {identifier}"}
```

---

# Request / Response Schema

All request/response payloads must use Pydantic models.

Location:

```
app/api/schemas/
```

Example request model:

```python
class AnalyzePayload(BaseModel):
    identifier: str
```

---

# Running the Service

## Prerequisites

* Docker
* Docker Compose

## Start

```
chmod +x start-dev.sh
./start-dev.sh
```

This starts:

* FastAPI (`api`)
* Celery worker (`worker`)
* Redis
* (Optional) Postgres

FastAPI is available at:

```
http://localhost:8000
```

Swagger UI:

```
http://localhost:8000/docs
```

---

# API Endpoints

| Method | Path                 | Description       |
| ------ | -------------------- | ----------------- |
| GET    | `/health`            | Service status    |
| POST   | `/analyze`           | Submit task       |
| GET    | `/results/{task_id}` | Check task status |

---

# Security

All endpoints requiring authorization must validate API key:

Header:

```
x-api-key: <SECRET_KEY>
```

SECRET_KEY must be overridden via environment variables.

---

# Development Workflow

## Create New Module

1. Define schema
   `app/api/schemas/<name>.py`

2. Add logic
   `app/services/<name>.py`

3. Add Celery task
   `app/tasks/<name>.py`

4. Add API route
   `app/api/routes/<name>.py`

5. Register router
   `app/main.py`

6. Write tests
   `tests/`

---

# Testing

Tests live under:

```
/tests
```

Run:

```
pytest
```

Unit tests should cover:

* Route request/response
* Business logic
* Celery task behavior

---

# Logging

Use `app/core/logging.py`:

```python
log = get_logger(__name__)
log.info("...")
```

No `print()` in production code.

---

# Docker

### Build

```
docker compose build
```

### Start

```
docker compose up -d
```

### Stop

```
docker compose down
```

`docker-compose.yaml` provisions:

* FastAPI
* Worker
* Redis
* Postgres (optional)

---

# Coding Rules

1. No business logic in routes.
2. No async work inside routes; always delegate to Celery.
3. Every route MUST use Pydantic schemas.
4. No raw dict payloads.
5. No print logging.
6. New tasks must follow naming convention.
7. API changes must update OpenAPI docs automatically.

---

# Example Flow

1. Client sends request to `/analyze`.
2. FastAPI validates payload.
3. FastAPI sends Celery task.
4. Worker executes logic.
5. Client queries `/results/{task_id}`.
6. Worker returns final data.

---

# Extending the Template

Recommended improvements per module:

* Add error categorization
* Add retry/backoff strategy
* Collect metadata (duration, source)
* Implement rate limiting
* Add caching

---

# Summary

This template enforces:

* Clear separation of concerns
* Common task + API flow
* Strong typing
* Reusable service logic
* Consistent workflows
* Maintainability across teams

Follow this structure for all future microservices to ensure consistency and easy scaling.
