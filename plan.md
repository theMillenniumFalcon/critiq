## Minimal, practical plan to recreate (ordered steps)

This is a concise, incremental plan to recreate the pr-analyzer project. Start small, get a working pipeline, then iterate on features.

1. Create project skeleton and venv
   - Create repository and folder structure:
     - `app/` with `__init__.py`
     - `app/config.py`, `app/main.py`, `app/database.py`, `app/models.py`, `app/schemas.py`
     - `app/celery_app.py`
     - `app/services/github_service.py` (simple stub)
     - `app/agents/base_agent.py` and a simple `app/agents/style_agent.py` stub
     - `run_dev.py`, `run_celery.py`, `.env.example`, `requirements.txt`, `docker-compose.yml`, `Dockerfile`, `tests/`
   - Create Python venv and install dependencies.

2. Implement a minimal FastAPI app and DB models
   - Implement `app/config.py` using pydantic BaseSettings reading `.env`.
   - Implement `app/models.py` with a minimal `AnalysisTask` (task_id, repo_url, pr_number, status, results JSON).
   - Implement `app/database.py` with a `create_tables()` helper used on startup.
   - Implement `app/main.py` with:
     - `/` health endpoint
     - `POST /analyze-pr` that creates an `AnalysisTask` record and enqueues a Celery task (or uses a background stub initially).
   - Test: run `python run_dev.py` and hit `/health`.

3. Bring up infrastructure (Postgres + Redis) — use Docker Compose (fastest)
   - Provide `docker-compose.yml` with `postgres:15` and `redis:7`.
   - Or run quick dev containers with `docker run` for Postgres and Redis.
   - Set `.env` to point to them (DATABASE_URL, REDIS_URL, CELERY_BROKER_URL, CELERY_RESULT_BACKEND).

4. Add Celery scaffolding
   - Implement `app/celery_app.py` with Celery config and a stub `analyze_pr_task` that updates DB statuses via a sync DB session.
   - Create `run_celery.py` to start the worker in dev.
   - Start the worker and verify that POST `/analyze-pr` enqueues and Celery updates the DB.

5. Implement GitHub fetching (safe, incremental)
   - Use `PyGithub` in `app/services/github_service.py` to fetch PR metadata and changed files.
   - For first pass, implement a simple stub that returns a fake `PullRequestData` (one small file); later replace with real API calls and token support.

6. Implement one agent & coordinator integration
   - Implement a minimal `BaseAgent` but make `analyze_file` return deterministic/trivial results (e.g., no issues).
   - Implement `AnalysisCoordinator` to iterate files, call agents, and aggregate results.
   - Connect the coordinator to `analyze_pr_task` in Celery and store results in `AnalysisTask.results`.

7. Replace stub agent with LLM integration
   - Add LLM clients (Anthropic/Claude or OpenAI) in `BaseAgent._create_llm()` and update agent prompts.
   - Start with a safe mock LLM for development to avoid API costs.
   - Add the vector cache and embedding usage after core functionality works.

8. Add tests & CI
   - Add tests for API endpoints (`httpx` + `pytest-asyncio`) and unit tests for `github_service`, `coordinator`.
   - Add GitHub Actions for lint and tests.

## Edge cases to be aware of

- Very large files or binary files in PRs: avoid analyzing huge files and skip binary content. Implement size checks and graceful skipping.
- GitHub rate limits and private repos: provide token support and fallbacks; handle API errors and surface informative messages to the user.
- Non-JSON or unexpected LLM responses: implement robust parsing with safe fallbacks (regex heuristics) and defensive code, and record confidence.
- Partial failures in multi-agent runs: allow partial aggregation if some agents fail; store partial results and detailed error messages.
- DB/Redis connectivity loss during Celery jobs: implement retries and idempotent updates; ensure tasks can be retried safely.
- Concurrency and race conditions: Celery tasks updating same DB rows must use safe transactions; be careful with optimistic updates to progress fields.
- Cost & rate control for LLM APIs: implement caching (vector/store) and request throttling to avoid runaway costs.
- File encodings and decoding errors: normalize file content to UTF-8 and handle decoding errors gracefully (skip or mark as unanalyzable).
- Large PRs with many files: provide batching and limit parallelism; expose progress and estimated time to the user.
- Security of secrets: never log API keys; require `.env` and secure deployment; consider vault integrations for production.
- Language detection edge cases: fallback to file extension heuristics and mark unknown languages to avoid incorrect prompt templates.

## Quick dev commands (reference)

PowerShell (example):

```powershell
# Setup venv and install
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start infra via docker-compose
docker-compose up -d

# Start API server
python run_dev.py

# Start Celery worker
python run_celery.py

# Run tests
pytest tests/ -v
```

---

This `plan.md` is intended as a living checklist: implement the minimal slices first and iterate. If you'd like, I can scaffold the initial files and a working dev flow next.


/ (repo root)
├── .github/                    # CI workflows
├── infra/                      # docker-compose, k8s manifests, etc.
│   └── docker-compose.yml
├── server/                     # FastAPI + Celery agent server
│   ├── server.py               # Server entrypoint
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py             # app factory, include routers
│   │   ├── config.py           # pydantic settings
│   │   ├── api/                # API endpoints (routers)
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── analyze.py  # /analyze-pr, /status, /results
│   │   │   │   └── admin.py
│   │   ├── agents/             # analysis agents + coordinator
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py
│   │   │   ├── coordinator.py
│   │   │   └── style_agent.py
│   │   ├── services/           # external services (github, vector cache)
│   │   ├── db/                 # database models & session
│   │   │   ├── models.py
│   │   │   ├── database.py
│   │   ├── celery_app.py
│   │   ├── schemas.py          # pydantic request/response models
│   │   └── utils/              # logging, redis client, helpers
│   ├── tests/                  # server unit & integration tests
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── run_dev.py              # convenience to run uvicorn
│   └── run_celery.py
├── client/                     # Vite + React client app
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/                # small API client (status/results)
│   │   ├── components/
│   │   ├── pages/
│   │   └── hooks/
│   ├── public/
│   └── Dockerfile
├── scripts/                    # helper scripts (PowerShell / bash)
├── README.md
└── plan.md                     # your plan/checklist (you already have)