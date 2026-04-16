# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

AI Emotion Companion Assistant (情感AI助手) — a full-stack app that combines MBTI/SBTI/attachment personality assessments with RAG-augmented AI chat. Built with FastAPI (Python 3.11) backend and React 18 + TypeScript frontend. All UI text and docs are in Chinese (zh-CN is default locale).

## Common Commands

### Backend (from `backend/`)

```bash
# Run dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run all tests
pytest

# Run only unit tests (CI uses this)
pytest tests/unit/ -v --cov=app --cov-report=xml

# Run a single test file
pytest tests/unit/test_auth.py -v

# Run a single test function
pytest tests/unit/test_auth.py::test_login -v

# Lint
black --check app/ tests/
flake8 app/ tests/ --max-line-length=120 --ignore=E501,W503

# Type check
mypy app/ --ignore-missing-imports

# Database migration
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### Frontend (from `frontend/web/`)

```bash
# Install dependencies
npm ci

# Dev server (port 5173, proxies /api to localhost:8000)
npm run dev

# Build (runs tsc then vite build)
npm run build

# Lint
npm run lint
npm run lint:fix

# Format
npm run format

# Test
npm test                  # vitest
npm run test:coverage     # vitest with coverage
```

### Docker

```bash
# Full stack deployment
docker-compose up -d

# Simplified dev (no MinIO)
docker-compose -f docker-compose.simple.yml up -d

# One-click deploy with scripts
./deploy/deploy.sh
```

## Architecture

### Backend Structure

Entry point: `backend/app/main.py` — creates FastAPI app with lifespan handler, middleware stack, and mounts all routes at `/api/v1`.

**Layered architecture:** API routes (`api/v1/`) → Services (`services/`) → Models (`models/`) / Schemas (`schemas/`)

- **API routes** — 18 routers registered in `api/v1/__init__.py`: auth, user, mbti, sbti, attachment, profile, chat, diary, knowledge, member, payment, admin, user_memory, voice, growth, enterprise, feedback, analytics. Plus WebSocket at `/ws/chat`.
- **Dependency injection** — `api/deps.py` provides `get_db()`, `get_redis()`, `get_current_user()` via FastAPI Depends.
- **Services** — each domain has its own service file. Enterprise sub-services live in `services/enterprise/`. Services are imported directly (no DI container).
- **Models** — SQLAlchemy 2.0 ORM models in `models/`. 60+ model classes exported from `models/__init__.py`.
- **Schemas** — Pydantic v2 request/response schemas in `schemas/`.
- **Config** — `core/config.py` uses pydantic-settings with 50+ fields loaded from env vars.

### LLM/AI Subsystem

- **Provider factory** (`services/llm/factory.py`) — supports 15+ providers (OpenAI, Anthropic, GLM, Qwen, ERNIE, Hunyuan, Spark, Doubao, SiliconFlow, Volcengine, etc.) with automatic failover chain.
- **Failover order** (default): Volcengine → Doubao → GLM → Qwen → SiliconFlow → ERNIE → Hunyuan. Configurable via `LLM_FAILOVER_CHAIN` env var.
- **RAG pipeline** (`services/rag/`) — VectorStore → Retriever → Generator → Quality Assessment. Vector DB supports Milvus/Qdrant/FAISS (configurable via `VECTOR_DB_TYPE`). Knowledge base data in `services/rag/knowledge_data.py`.
- **Long-term memory** (`services/memory_service.py`) — persists user context across sessions.
- **Crisis detection** (`services/crisis_service.py`) — detects crisis content and provides referral resources.

### Frontend Structure

Entry point: `frontend/web/src/main.tsx`

- **Routing** — `App.tsx` defines all routes with `React.lazy()` for code splitting. Views in `views/` directory.
- **API client** — `api/request.ts` exports a configured Axios instance with auth token injection and error interceptors. All API calls go through this.
- **State management** — Zustand stores in `stores/`: auth (with localStorage persist), chat, mbti, assessment, diary.
- **i18n** — i18next with zh-CN (default) and en-US locales in `i18n/locales/`.
- **Theming** — Dark/light mode via `hooks/useTheme.ts`, Ant Design ConfigProvider in main.tsx.
- **Design tokens** — `design/tokens.ts` for consistent styling.

### Infrastructure

- **Database** — MySQL 8.0 primary (SQLite fallback when `DATABASE_URL` starts with `sqlite:`). Migrations via Alembic in `alembic/versions/`.
- **Cache** — Redis 7 via `redis.asyncio` (connection pool, max 50 connections).
- **Object storage** — MinIO for file uploads (avatars, attachments).
- **Reverse proxy** — Nginx routes `/api/` to backend:8000 and `/` to frontend static files. In dev, Vite proxies `/api` to localhost:8000.
- **CI/CD** — GitHub Actions (`.github/workflows/ci.yml`): Python 3.11 + Node 20, lint + test + Docker build. Deploys to production via SSH on push to main.

### Key Environment Variables

- `DATABASE_URL` — MySQL or SQLite connection string (SQLite: `sqlite:///./emotion_ai.db`)
- `LLM_PROVIDER` — Which LLM provider to use (e.g., `openai`, `glm`, `qwen`, `mock` for testing)
- `SECRET_KEY` — JWT signing key (required, 32+ chars in production)
- `VECTOR_DB_TYPE` — Vector DB backend: `milvus`, `qdrant`, or `faiss`
- `NEO4J_ENABLED` — Enable Neo4j knowledge graph (default: False, falls back to SQLAlchemy)
