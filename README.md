# Momentum-AI Backend

A FastAPI-powered backend for AI-driven learning roadmap generation and task management. Generates personalized learning plans using OpenAI, manages roadmaps with weekly and daily task breakdowns, and tracks progress through a Supabase database.

---

## Production API Base URL

> **Hosted on Render**
>
> Replace the placeholder below with your actual Render service URL (from the Render dashboard).

```text
https://momentum-ai-fb1g.onrender.com
```

The frontend (or any API client) should send all requests to this base URL in production.

---

## Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn (development) / Gunicorn (production)
- **Database**: Supabase (PostgreSQL)
- **AI Integration**: OpenAI API (via OpenRouter)
- **HTTP Client**: httpx
- **Data Processing**: pandas
- **Environment Management**: python-dotenv

---

## Architecture Overview

Frontend (Next.js on Vercel)
        ↓
FastAPI Backend (Render)
        ↓
Supabase (Postgres)
        ↓
OpenRouter (LLM)

## Core Responsibilities

1. **Roadmap Generation**: AI-powered creation of multi-week learning roadmaps based on user goals, duration, experience level, and available hours per day.

2. **Task Management**: Persistent storage and retrieval of AI-generated tasks, organized by week and day within a roadmap.

3. **Progress Tracking**: Update and monitor task completion status across roadmaps.

4. **AI Assistant**: Context-aware question answering about specific roadmaps, weeks, and days using OpenAI language models.

5. **Data Persistence**: Atomic roadmap creation with transaction safety—full rollback if any part of the insertion fails.

---

## API Endpoints

### Roadmap Operations

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/generate_roadmap` | Generate and persist a new AI roadmap (consumed by frontend) |
| `GET` | `/roadmaps?user_id={user_id}` | List all roadmaps for a user |
| `GET` | `/roadmap/{roadmap_id}` | Fetch all tasks for a roadmap |
| `DELETE` | `/roadmap/{roadmap_id}?user_id={user_id}` | Delete a roadmap and its tasks |

### Weekly & Daily Details

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/roadmap/{roadmap_id}/weeks` | Get all weeks in a roadmap |
| `GET` | `/roadmap/{roadmap_id}/week/{week_number}` | Get tasks for a specific week with daily breakdown |

### Task Management

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/task/update` | Mark a task as completed or incomplete |

### AI Assistant

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/ask-assistant` | Query AI assistant about a roadmap, week, or specific day (consumed by frontend) |

### Health Check

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/health` | Verify backend is running |

---

## Request/Response Examples

### Generate Roadmap

**Request:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "goal": "Learn Python for data science",
  "duration_weeks": 12,
  "daily_hours": 2,
  "level": "intermediate"
}
```

**Response:**
```json
{
  "roadmap_id": 42,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "Learn Python for data science",
  "level": "intermediate",
  "duration_weeks": 12,
  "daily_hours": 2,
  "is_active": true,
  "created_at": "2025-01-26T10:30:00Z"
}
```

### Update Task Status

**Request:**
```json
{
  "task_id": "12345",
  "completed": true
}
```

**Response:**
```json
{
  "success": true
}
```

### Ask Assistant

**Request:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "roadmap_id": 42,
  "input_data": "How do I practice the concepts from Week 2?",
  "week_number": 2,
  "day_number": null
}
```

**Response:**
```json
{
  "response": "Based on your Week 2 tasks, focus on... [AI-generated response]"
}
```

---

## Environment Variables

Required for production deployment:

| Variable | Description | Example |
|----------|-------------|---------|
| `SUPABASE_URL` | Supabase project URL | `https://project.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role API key (used for database operations) | `eyJ...` |
| `OPENAI_API_KEY` | OpenAI API key for roadmap generation and assistant (uses OpenRouter) | `sk-or-v1-...` |

Create a `.env` file in the project root:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
```

---

## Local Development Setup

### Prerequisites
- Python 3.9+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/momentum-ai.git
cd momentum-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Supabase and OpenAI credentials
```

5. Run the development server:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 10000
```

The API will be available at `http://localhost:10000`.

### API Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: `http://localhost:10000/docs`
- **ReDoc**: `http://localhost:10000/redoc`

---

## Deployment Notes

### Render Deployment

1. **CORS Configuration**  
   The backend should be configured to accept requests from:
   - `http://localhost:3000` (local frontend development, if you have one)
   - Your production frontend URL (for example: `https://momentum-ai-frontend.vercel.app`)

   Update the CORS settings in your FastAPI app (e.g. in `api.py`) if you change frontend origins.

2. **Environment Variables on Render**  
   In the Render dashboard, open your backend service and configure the following env vars:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `OPENAI_API_KEY`

   These must match the values you use locally in `.env`.

3. **Start Command**  
   Configure the Render service start command, for example:

   ```bash
   uvicorn api:app --host 0.0.0.0 --port 10000
   ```

   Render will automatically bind the correct port via the `$PORT` environment variable; if you prefer, you can use `--port $PORT` instead of a hardcoded value.

4. **Logs & Monitoring**  
   Use the Render dashboard **Logs** tab to monitor startup, request handling, and any runtime errors.

---

## Database Schema

The backend uses the following key tables in Supabase:

- **roadmaps**: User roadmaps with goal descriptions, duration, and difficulty level
- **goals**: High-level objectives linked to roadmaps (legacy support)
- **tasks**: General tasks (legacy support)
- **roadmap_tasks**: AI-generated tasks organized by week, day, effort, and category
- **time_entries, rules, activity_logs**: Supporting tables for future features

Detailed schema available in [src/dao/schema.sql](src/dao/schema.sql).

---

## Error Handling & Rollback

When generating and persisting a roadmap:

1. AI generates the full roadmap structure
2. Roadmap is inserted into the database
3. Tasks are inserted for each week and day
4. **If any step fails**, the entire roadmap and its tasks are automatically deleted (transaction safety)

This ensures the database never contains incomplete roadmaps.

---

## Health Check

Before integrating with the frontend, verify the backend is operational on Render:

```bash
curl https://momentum-ai-fb1g.onrender.com/health
```

Expected response:
```json
{
  "status": "ok"
}
```

---

## Live Demo

Frontend: https://momentum-ai-frontend.vercel.app
Backend: https://momentum-ai-fb1g.onrender.com/docs

## Support & Troubleshooting

- **Roadmap generation fails**: Check OPENAI_API_KEY is valid and has available credits
- **Database connection errors**: Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are correct
- **CORS errors from frontend**: Confirm the frontend URL is in the allowed origins in `api.py`

---

## License

Proprietary. Do not distribute without permission.
