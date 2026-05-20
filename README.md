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
- Local model to test: `https://huggingface.co/hugging-quants/Llama-3.2-1B-Instruct-Q4_K_M-GGUF/blob/main/llama-3.2-1b-instruct-q4_k_m.gguf`
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

## Troubleshooting (common log lines)

**`422` on `/auth/register` or `/auth/login`**

- Not caused by missing GitHub env vars.
- The API expects JSON: `{"login": "...", "password": "..."}` with `Content-Type: application/json`.
- Validation rules: **login** length 3–64, **password** length 8–128. Shorter values return `422` with a Pydantic detail body.

**`401` on `/auth/me` or `/chats`**

- Normal if you are not logged in or the access token expired. Use **Login** or **Refresh**; the SPA stores tokens in `localStorage`.

**`POST /api/v1/chats//ask` → `404`**

- The URL had an **empty chat id** (double slash). Create a chat and select it in the dropdown before **Ask LLM**.

**`(trapped) error reading bcrypt version` / register `400`**

- This was a **passlib + bcrypt** incompatibility in older installs. The project now uses the **`bcrypt` package directly** (no passlib). Rebuild the image: `docker compose build --no-cache api` then `docker compose up`.

**Example `.env` only**

- `JWT_SECRET=change-me` is enough for local try-outs.
- GitHub OAuth buttons will fail until `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` / `GITHUB_REDIRECT_URI` are set; password register/login still works.
