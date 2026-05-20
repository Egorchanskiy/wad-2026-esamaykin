# wad-2026-esamaykin

FastAPI + MongoDB + Redis + local LLM chat application with SPA UI.

## Chosen architecture

- UI strategy: **SPA**
- Backend pattern: **MCS (Model-Controller-Service)**

## Stack

- Python
- FastAPI
- MongoDB
- Redis
- JWT (access + refresh)
- GitHub OAuth
- llama-cpp-python
- Docker / Docker Compose

## Run locally (single command)

1. Copy env:
   - `cp .env.example .env`
2. Fill required env values in `.env`:
   - `JWT_SECRET`
   - `GITHUB_CLIENT_ID`
   - `GITHUB_CLIENT_SECRET`
   - `GITHUB_REDIRECT_URI` (must match GitHub OAuth app callback URL)
   - optionally `LLM_MODEL_PATH` (default: `model.gguf`)
3. Start project:
   - `docker compose up --build`
4. Open:
   - SPA: `http://localhost:8000/`
   - Swagger: `http://localhost:8000/docs`

Stop and remove containers:

- `docker compose down`

## Environment variables

- `APP_NAME`, `ENV`, `DEBUG`, `API_V1_PREFIX`
- `MONGO_URI`, `MONGO_DB`
- `REDIS_URI`, `REFRESH_TOKEN_TTL_SECONDS` (default 30 days)
- `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_REDIRECT_URI`
- `LLM_MODEL_PATH`

## API endpoints

Auth:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET /api/v1/auth/github/login`
- `GET /api/v1/auth/github/callback?code=...`

Chats:

- `POST /api/v1/chats`
- `GET /api/v1/chats`
- `GET /api/v1/chats/{chat_id}/messages`
- `POST /api/v1/chats/{chat_id}/messages`
- `POST /api/v1/chats/{chat_id}/ask`