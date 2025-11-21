# ResuMatch

A resume matching application using FastAPI, Celery, and ML.

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Start services:
   ```bash
   docker-compose up --build
   ```

## Database Migrations

The application uses Alembic for database migrations. The web container automatically runs `alembic upgrade head` on startup.

To create a new migration after changing models:
```bash
# 1. Make sure containers are running
docker-compose up -d

# 2. Generate migration script
docker-compose exec web alembic revision --autogenerate -m "description_of_change"

# 3. Apply migration (optional, as restarting web will also do it)
docker-compose exec web alembic upgrade head
```

## Structure

- `src/app`: Main application code
- `src/app/api`: API endpoints
- `src/app/models`: Database models
- `src/app/tasks`: Celery tasks
- `src/app/ml`: Machine Learning logic
- `tests`: Tests

