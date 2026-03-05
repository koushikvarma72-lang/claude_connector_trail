import httpx
import os
import time
import threading
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ── Load .env ──
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# ── Config ──
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://task-manager-backend-production-1f80.up.railway.app"
).rstrip("/")
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", 30))  # Configurable via .env

mcp = FastMCP("Task Manager MCP")


# ════════════════════════════════════════════════
# ── RATE LIMITER (Sliding Window, In-Memory) ──
# ════════════════════════════════════════════════

# Stores timestamps of recent calls per client
call_log: dict[str, list[float]] = defaultdict(list)
call_lock = threading.Lock()


def is_rate_limited(client_id: str = "global") -> tuple[bool, int]:
    """
    Sliding window rate limiter.
    Returns (is_limited: bool, requests_remaining: int).

    How it works:
      - Keeps a list of timestamps for each client_id
      - On every call, drops timestamps older than 60s
      - If count >= RATE_LIMIT → blocked
      - Otherwise → records timestamp and allows
    """
    now = time.time()
    window_start = now - 60  # 60-second rolling window

    with call_lock:
        # Remove calls outside the sliding window
        call_log[client_id] = [
            t for t in call_log[client_id] if t > window_start
        ]

        count = len(call_log[client_id])

        if count >= RATE_LIMIT:
            return True, 0  # Rate limited

        # Record this call
        call_log[client_id].append(now)
        return False, RATE_LIMIT - count - 1  # Allowed


# ════════════════════════════════════════════════
# ── USAGE METRICS ──
# ════════════════════════════════════════════════

MAX_LOG_SIZE = 500  # Keep last 500 invocation records

metrics: dict = {
    "total_invocations": 0,
    "per_tool": defaultdict(int),        # e.g. {"github_list_repos": 5}
    "per_tool_errors": defaultdict(int), # e.g. {"airtable_list_records": 2}
    "rate_limit_hits": 0,
    "invocation_log": []                 # Rolling log of last MAX_LOG_SIZE calls
}
metrics_lock = threading.Lock()


def record_invocation(tool_name: str, success: bool, error: str = None):
    """Record a tool call into the metrics store."""
    with metrics_lock:
        metrics["total_invocations"] += 1
        metrics["per_tool"][tool_name] += 1

        if not success:
            metrics["per_tool_errors"][tool_name] += 1

        metrics["invocation_log"].append({
            "tool": tool_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": success,
            "error": error
        })

        # Trim log to max size
        if len(metrics["invocation_log"]) > MAX_LOG_SIZE:
            metrics["invocation_log"] = metrics["invocation_log"][-MAX_LOG_SIZE:]


def record_rate_limit_hit(tool_name: str):
    """Increment rate limit hit counter."""
    with metrics_lock:
        metrics["rate_limit_hits"] += 1
        metrics["invocation_log"].append({
            "tool": tool_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": False,
            "error": "rate_limit_exceeded"
        })


# ════════════════════════════════════════════════
# ── GUARD HELPER ──
# ════════════════════════════════════════════════

def guarded_tool(tool_name: str, client_id: str = "global") -> dict | None:
    """
    Call at the start of every tool function.
    - Checks rate limit
    - Records the invocation
    Returns an error dict if rate limited, else None (meaning: proceed).

    Usage inside any tool:
        if err := guarded_tool("your_tool_name"):
            return err
    """
    limited, remaining = is_rate_limited(client_id)

    if limited:
        record_rate_limit_hit(tool_name)
        return {
            "error": "Rate limit exceeded",
            "limit": f"{RATE_LIMIT} requests/min",
            "window": "60 seconds",
            "retry_after": "Try again within 60 seconds",
            "tip": "You can change RATE_LIMIT_PER_MIN in your .env to increase the limit"
        }

    record_invocation(tool_name, success=True)
    return None  # All good — proceed


# ════════════════════════════════════════════════
# ── TOOLS ──
# ════════════════════════════════════════════════

# ── GitHub ──
@mcp.tool()
async def github_list_repos() -> dict:
    """List repositories for the authenticated GitHub user."""
    if err := guarded_tool("github_list_repos"):
        return err

    token = os.getenv("GITHUB_TOKEN")
    base_url = os.getenv("GITHUB_BASE_URL")

    if not token or not base_url:
        record_invocation("github_list_repos", success=False, error="missing_credentials")
        return {"error": "GitHub credentials not configured."}

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{base_url}/user/repos", headers=headers)

        if response.status_code != 200:
            record_invocation("github_list_repos", success=False, error=f"http_{response.status_code}")
            return {"error": response.text}

        repos = response.json()
        return {
            "count": len(repos),
            "repositories": [
                {"name": r["name"], "full_name": r["full_name"]}
                for r in repos
            ]
        }


# ── Airtable ──
@mcp.tool()
async def airtable_list_records() -> dict:
    """List records from the configured Airtable table."""
    if err := guarded_tool("airtable_list_records"):
        return err

    token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    table_name = os.getenv("AIRTABLE_TABLE_NAME")

    if not token or not base_id or not table_name:
        record_invocation("airtable_list_records", success=False, error="missing_credentials")
        return {"error": "Airtable credentials not configured."}

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            record_invocation("airtable_list_records", success=False, error=f"http_{response.status_code}")
            return {"error": response.text}

        data = response.json()
        return {
            "count": len(data.get("records", [])),
            "records": data.get("records", [])
        }


# ── Trello ──
@mcp.tool()
async def trello_list_boards() -> dict:
    """List all Trello boards for the authenticated user."""
    if err := guarded_tool("trello_list_boards"):
        return err

    api_key = os.getenv("TRELLO_API_KEY")
    token = os.getenv("TRELLO_TOKEN")

    if not api_key or not token:
        record_invocation("trello_list_boards", success=False, error="missing_credentials")
        return {"error": "Trello credentials not configured."}

    url = "https://api.trello.com/1/members/me/boards"
    params = {"key": api_key, "token": token}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

        if response.status_code != 200:
            record_invocation("trello_list_boards", success=False, error=f"http_{response.status_code}")
            return {"error": response.text}

        boards = response.json()
        return {
            "count": len(boards),
            "boards": [{"id": b["id"], "name": b["name"]} for b in boards]
        }


# ── Task Manager ──
@mcp.tool()
async def get_all_tasks() -> dict:
    """Get all tasks from the Task Manager app."""
    if err := guarded_tool("get_all_tasks"):
        return err

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/tasks")
        response.raise_for_status()
        tasks = response.json()
        if not tasks:
            return {"message": "No tasks found.", "tasks": []}
        return {"tasks": tasks, "count": len(tasks)}


@mcp.tool()
async def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
    """
    Create a new task in the Task Manager.

    Args:
        title: The task title (required)
        description: Optional task description
        priority: 'low', 'medium', or 'high' (default: medium)
    """
    if err := guarded_tool("create_task"):
        return err

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/tasks",
            json={"title": title, "description": description, "priority": priority}
        )
        response.raise_for_status()
        return {"message": "Task created successfully!", "task": response.json()}


@mcp.tool()
async def complete_task(task_id: str) -> dict:
    """
    Mark a task as completed.

    Args:
        task_id: The ID of the task to complete
    """
    if err := guarded_tool("complete_task"):
        return err

    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{BACKEND_URL}/tasks/{task_id}",
            json={"completed": True}
        )
        if response.status_code == 404:
            return {"error": f"Task with ID '{task_id}' not found."}
        response.raise_for_status()
        return {"message": "Task marked as completed!", "task": response.json()}


@mcp.tool()
async def update_task(
    task_id: str,
    title: str = None,
    description: str = None,
    priority: str = None
) -> dict:
    """
    Update an existing task's details.

    Args:
        task_id: The ID of the task to update
        title: New title (optional)
        description: New description (optional)
        priority: New priority - 'low', 'medium', or 'high' (optional)
    """
    if err := guarded_tool("update_task"):
        return err

    updates = {}
    if title:       updates["title"] = title
    if description: updates["description"] = description
    if priority:    updates["priority"] = priority

    async with httpx.AsyncClient() as client:
        response = await client.put(f"{BACKEND_URL}/tasks/{task_id}", json=updates)
        if response.status_code == 404:
            return {"error": f"Task with ID '{task_id}' not found."}
        response.raise_for_status()
        return {"message": "Task updated!", "task": response.json()}


@mcp.tool()
async def delete_task(task_id: str) -> dict:
    """
    Delete a task permanently.

    Args:
        task_id: The ID of the task to delete
    """
    if err := guarded_tool("delete_task"):
        return err

    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{BACKEND_URL}/tasks/{task_id}")
        if response.status_code == 404:
            return {"error": f"Task with ID '{task_id}' not found."}
        response.raise_for_status()
        return {"message": f"Task {task_id} deleted successfully!"}


@mcp.tool()
async def get_task_stats() -> dict:
    """Get a summary of all tasks — total, completed, pending, and high priority count."""
    if err := guarded_tool("get_task_stats"):
        return err

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/tasks/stats/summary")
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def get_pending_tasks() -> dict:
    """Get only the tasks that are not yet completed."""
    if err := guarded_tool("get_pending_tasks"):
        return err

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/tasks")
        response.raise_for_status()
        all_tasks = response.json()
        pending = [t for t in all_tasks if not t["completed"]]
        return {"pending_tasks": pending, "count": len(pending)}


@mcp.tool()
async def get_high_priority_tasks() -> dict:
    """Get all high priority tasks."""
    if err := guarded_tool("get_high_priority_tasks"):
        return err

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BACKEND_URL}/tasks")
        response.raise_for_status()
        all_tasks = response.json()
        high = [t for t in all_tasks if t["priority"] == "high"]
        return {"high_priority_tasks": high, "count": len(high)}


# ════════════════════════════════════════════════
# ── METRICS TOOL ──
# ════════════════════════════════════════════════

@mcp.tool()
async def get_usage_metrics() -> dict:
    """
    Get MCP server usage metrics.
    Shows total invocations, per-tool breakdown,
    error counts, rate limit hits, and the last 10 calls.
    """
    if err := guarded_tool("get_usage_metrics"):
        return err

    with metrics_lock:
        return {
            "rate_limit_config": f"{RATE_LIMIT} requests/min (sliding window)",
            "total_invocations": metrics["total_invocations"],
            "rate_limit_hits": metrics["rate_limit_hits"],
            "per_tool_calls": dict(metrics["per_tool"]),
            "per_tool_errors": dict(metrics["per_tool_errors"]),
            "recent_invocations": metrics["invocation_log"][-10:],
            "note": "Metrics reset on server restart. Use Redis for persistence."
        }


@mcp.tool()
async def reset_usage_metrics() -> dict:
    """
    Reset all usage metrics back to zero.
    Useful for starting a fresh monitoring window.
    """
    if err := guarded_tool("reset_usage_metrics"):
        return err

    with metrics_lock:
        metrics["total_invocations"] = 0
        metrics["per_tool"] = defaultdict(int)
        metrics["per_tool_errors"] = defaultdict(int)
        metrics["rate_limit_hits"] = 0
        metrics["invocation_log"] = []

    return {"message": "Metrics reset successfully.", "timestamp": datetime.utcnow().isoformat() + "Z"}


# ════════════════════════════════════════════════
# ── ENTRY POINT ──
# ════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"Starting MCP server — Rate limit: {RATE_LIMIT} req/min")
    mcp.run(transport="stdio")
