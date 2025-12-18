# ResuMatch

A resume matching application using FastAPI, Celery, and ML/AI with RAG (Retrieval-Augmented Generation) for intelligent resume-job comparison and suggestions.

## Features

- **Resume Analysis**: Upload and analyze resumes against job descriptions
- **Semantic Matching**: Uses sentence transformers for similarity scoring
- **RAG-Powered Suggestions**: AI-generated feedback comparing resumes with job requirements using LangChain
  - Powered by LangChain for robust prompt management and structured outputs
  - Strengths and weaknesses analysis
  - Actionable improvement suggestions
  - Keyword recommendations
  - Overall assessment

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Configure environment variables in `.env`:
   - Database settings (PostgreSQL)
   - Redis settings
   - **Optional**: `OPENAI_API_KEY` - For RAG-powered suggestions (if not provided, falls back to keyword-based analysis)
   - **Optional**: `OPENAI_MODEL` - Model to use (default: `gpt-4o-mini`)

3. Start services:
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

## API Endpoints

### Resume Analysis
- `POST /api/v1/analyze` - Upload and analyze a resume against a job role
- `GET /api/v1/candidates` - List all candidates
- `GET /api/v1/candidates/{candidate_id}` - Get candidate analysis results
- `GET /api/v1/candidates/{candidate_id}/suggestions` - Get RAG-powered suggestions comparing resume with job description

### Job Roles
- `POST /api/v1/roles` - Create a new job role
- `GET /api/v1/roles` - List all job roles
- `GET /api/v1/roles/{role_id}` - Get a specific job role

## Structure

- `src/app`: Main application code
- `src/app/api`: API endpoints
- `src/app/models`: Database models and DTOs
- `src/app/tasks`: Celery tasks for async processing
- `src/app/ml`: Machine Learning logic and RAG service
- `tests`: Tests

