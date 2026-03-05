# System Report: claude_connector_trail

## 1) What is happening

This repository is a three-service integration:

- `frontend/` is a React + Vite task manager UI.
- `backend/` is a FastAPI task API.
- `mcp-server/` is an MCP tool server that exposes tools for task operations and external service APIs.

The MCP server is launched from `claude_config_file` as a local stdio MCP process.

## 2) How it is happening (runtime flow)

### Frontend flow

1. UI loads tasks + stats from backend (`/tasks`, `/tasks/stats/summary`).
2. User actions call backend CRUD endpoints.
3. UI refreshes state by refetching tasks and stats.

### Backend flow

1. FastAPI app starts in `backend/main.py`.
2. CORS allows all origins.
3. Data is held in-memory in `tasks_db`.
4. Endpoints provide CRUD + summary stats.

### MCP flow

1. `mcp-server/mcp_server.py` loads `.env`.
2. MCP tools are registered via `@mcp.tool()`.
3. A sliding-window rate limiter guards each tool.
4. Tools call backend/GitHub/Airtable/Trello APIs.
5. In-memory metrics track usage/errors/rate-limit hits.

## 3) Changes applied

- Fixed `backend/Procfile` to use `$PORT` instead of `$8000`.
- Updated `backend/main.py` to read `HOST`/`PORT` from env.
- Added backend priority validation (`low|medium|high`) via `Literal`.
- Changed backend task timestamps to UTC ISO format with `Z`.
- Made MCP backend URL configurable via `BACKEND_URL` env var.
- Made frontend API URL configurable via `VITE_API_BASE_URL`.
- Added `python-dotenv==1.0.1` to MCP requirements.
- Updated `claude_config_file` to Windows paths for this machine.
- Replaced duplicate/malformed `.gitignore` with clean entries.
- Added env templates:
  - `backend/.env.example`
  - `frontend/.env.example`
  - `mcp-server/.env.example`

## 4) Remaining risks

- `mcp-server/.env` contains live secrets; rotate tokens if exposed.
- Backend data is in-memory only (no persistence).
- MCP metrics/rate-limit state resets on process restart.
