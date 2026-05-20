# Changelog

## 2026-05-17

- Initialized FastAPI project skeleton with MCS-oriented package layout.
- Added Dockerfile and `docker-compose.yml` with API, MongoDB, and Redis services.
- Added environment template and base configuration for JWT, Redis TTL, GitHub OAuth, and local LLM path.
- Added startup/shutdown DB connection lifecycle and initial health endpoint.
- Implemented auth foundation: registration/login/me/refresh/logout endpoints.
- Added password hashing (bcrypt), JWT access+refresh flow, and refresh session storage in Redis with 30-day TTL.

## 2026-05-20

- Added unique index setup for user login in MongoDB.
- Added GitHub OAuth flow endpoints (`/auth/github/login`, `/auth/github/callback`) with user provisioning.
- Implemented chat and message APIs with persisted MongoDB history.
- Added LLM ask endpoint per chat (`POST /chats/{chat_id}/ask`) that stores both question and answer.
- Added simple SPA UI (`/`) for auth, chat creation, history view, and asking LLM.
- Extended architecture docs (`arch/api-structure.md`, `arch/code-structure.md`, `arch/database.md`, `arch/ui.md`).
- Updated README with full run instructions, env vars, and API list.
- Replaced passlib with native `bcrypt` hashing to fix bcrypt 4.1+ compatibility (`__about__` AttributeError).
- SPA: client-side validation for login/password length, chat selection before ask, and clearer error alerts.
- Chat routes: return `400` when `chat_id` is missing instead of opaque `404` on `/chats//...`.
