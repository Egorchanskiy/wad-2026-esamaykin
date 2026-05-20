# wad-2026-esamaykin

FastAPI + MongoDB + Redis backend for ChatGPT-like chat application.

## Quick start

1. Copy env file:
   - `cp .env.example .env`
2. Start all services:
   - `docker compose up --build`
3. Open API:
   - `http://localhost:8000/docs`

## Stack

- Python
- FastAPI
- MongoDB
- Redis
- JWT (to be implemented in next steps)
- GitHub OAuth (to be implemented in next steps)
- llama-cpp-python for local model usage

## Implemented API (current)

- Auth:
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `POST /api/v1/auth/refresh`
  - `POST /api/v1/auth/logout`
  - `GET /api/v1/auth/me`
  - `GET /api/v1/auth/github/login`
  - `GET /api/v1/auth/github/callback`
- Chats:
  - `POST /api/v1/chats`
  - `GET /api/v1/chats`
  - `GET /api/v1/chats/{chat_id}/messages`
  - `POST /api/v1/chats/{chat_id}/messages`
  - `POST /api/v1/chats/{chat_id}/ask`