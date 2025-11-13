# ST Assistant — Travel Chat (Commerit)

Minimal README for local development.

## Overview

ST Assistant is a travel planning chat assistant with:

- Scrape endpoint to fetch, clean, chunk, embed and upsert to Pinecone
- Chat endpoint with RAG (OpenAI Response API / Chat Completions)
- History endpoint returning last 50 chats from Supabase
- Frontend (Vue) chat UI

This repo contains:

- backend/app — FastAPI backend (endpoints: /scrape, /chat, /history)
- frontend — Vue 3 frontend
- docker-compose.yml — local docker setup (if present)

## Prerequisites

- Docker & docker-compose (preferred for Docker flow)
- Node.js (16+) — only if running frontend locally
- Python 3.10+ — only if running backend locally
- Accounts / keys for:
  - OpenAI (OPENAI_API_KEY)
  - Pinecone (PINECONE_API_KEY, PINECONE_ENV, PINECONE_INDEX)
  - Supabase (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY)

## Environment variables

Set these in a `.env` file in the project root (do NOT commit):

- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY (preferred) or SUPABASE_KEY
- OPENAI_API_KEY
- PINECONE_API_KEY
- PINECONE_ENV
- PINECONE_INDEX
- Any other config you use

The docker-compose setup will load variables from `.env` automatically.

## Run with Docker (recommended)

1. Copy example env or create `.env`:

   - cp .env.example .env
   - Fill in required variables.

2. Build and start services (pass build-arg so Dockerfiles that use ARG CONTEXT work when building from the service folders):

   - docker compose build --build-arg CONTEXT=. && docker compose up -d

3. Tail logs:

   - docker compose logs -f

4. Stop and remove containers:

   - docker compose down

5. Run just one service (optional):
   - docker compose build --build-arg CONTEXT=. backend
   - docker compose up backend

Ports (common defaults)

- Backend: 8000 (uvicorn)
- Frontend: 5173 (Vite) or 80 inside container (nginx) — adjust in docker-compose.yml if different.

Notes:

- Passing --build-arg CONTEXT=. lets the Dockerfiles use '.' as the internal copy prefix when you run the compose command from the service directory. If you build from repo root, set CONTEXT=frontend or CONTEXT=backend instead.
- If you change .env, restart containers: docker compose down && docker compose build --build-arg CONTEXT=. && docker compose up -d

## Run backend (local, without Docker)

From repository root:

1. cd backend
2. python -m venv .venv
3. source .venv/bin/activate
4. pip install -r requirements.txt
5. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Run frontend (local, without Docker)

From repository root:

1. cd frontend
2. npm install
3. npm run dev

Change API base URL in the frontend if backend host/port differs.

## Important endpoints

- POST /scrape — fetch, clean, chunk, embed, upsert to Pinecone (dedupe by URL hash)
- POST /chat — body: { question: "..." } → returns { answer, citations }
- GET /history — returns last 50 chats from Supabase: { "chats": [ { id, title, messages, created_at }, ... ] }

## History endpoint notes

- Implemented in `backend/app/history.py`
- Router returns normalized messages arrays with { role, text } items
- Table name used by default is `chats` (change if your schema uses `chat_history`)

## Troubleshooting

- 404 /history: Ensure `app.main` includes `from app.history import router as history_router` and `app.include_router(history_router)` and that backend container was restarted after changes.
- ImportError on startup: avoid creating FastAPI app or running remote-client code at import time in routers; env var access should be lazy.
- Missing env vars will cause runtime errors — verify `.env` and docker-compose environment.
