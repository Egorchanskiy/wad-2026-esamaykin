# Code Structure

## Backend pattern

The backend follows **MCS (Model-Controller-Service)** for a SPA-oriented API:

- `app/models` - Mongo document-oriented model helpers and persistence shapes.
- `app/api` - thin route/controller layer (request parsing, dependency wiring).
- `app/services` - business logic (auth, chat, LLM orchestration).
- `app/schemas` - Pydantic request/response DTOs.
- `app/db` - database clients and connection lifecycle.
- `app/core` - settings and cross-cutting configuration.

## Current status

Current implementation includes:

- App bootstrap (`app/main.py`)
- Config (`app/core/config.py`)
- Mongo and Redis connection management
- Auth module (`app/api/auth.py`, `app/services/auth_service.py`, `app/core/security.py`)
- Chat module (`app/api/chats.py`, `app/services/chat_service.py`)
- Local LLM integration (`app/services/llm_service.py`)
- API routers (`app/api/router.py`)
- Simple SPA client (`web/index.html`) served from `/`

## Note

You can find dull report in wad-2026-esamaykin.pdf
