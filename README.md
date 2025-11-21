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

## Structure

- `src/app`: Main application code
- `src/app/api`: API endpoints
- `src/app/models`: Database models
- `src/app/tasks`: Celery tasks
- `src/app/ml`: Machine Learning logic
- `tests`: Tests

