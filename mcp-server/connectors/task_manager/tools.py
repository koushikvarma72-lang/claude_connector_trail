from mcp.server.fastmcp import FastMCP

from connectors.task_manager.client import (
    complete_task as complete_task_request,
    create_task as create_task_request,
    delete_task as delete_task_request,
    get_task_stats as get_task_stats_request,
    get_tasks,
    update_task as update_task_request,
)
from core.guard import guarded_tool


def register_task_manager_tools(mcp: FastMCP) -> None:
    @mcp.tool()
    async def get_all_tasks() -> dict:
        """Get all tasks from the Task Manager app."""
        if err := guarded_tool("get_all_tasks"):
            return err

        response = await get_tasks()
        response.raise_for_status()
        tasks = response.json()
        if not tasks:
            return {"message": "No tasks found.", "tasks": []}
        return {"tasks": tasks, "count": len(tasks)}

    @mcp.tool()
    async def create_task(title: str, description: str = "", priority: str = "medium") -> dict:
        """Create a new task in the Task Manager."""
        if err := guarded_tool("create_task"):
            return err

        response = await create_task_request(title=title, description=description, priority=priority)
        response.raise_for_status()
        return {"message": "Task created successfully!", "task": response.json()}

    @mcp.tool()
    async def complete_task(task_id: str) -> dict:
        """Mark a task as completed."""
        if err := guarded_tool("complete_task"):
            return err

        response = await complete_task_request(task_id=task_id)
        if response.status_code == 404:
            return {"error": f"Task with ID '{task_id}' not found."}
        response.raise_for_status()
        return {"message": "Task marked as completed!", "task": response.json()}

    @mcp.tool()
    async def update_task(
        task_id: str,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
    ) -> dict:
        """Update an existing task's details."""
        if err := guarded_tool("update_task"):
            return err

        response = await update_task_request(
            task_id=task_id,
            title=title,
            description=description,
            priority=priority,
        )
        if response.status_code == 404:
            return {"error": f"Task with ID '{task_id}' not found."}
        response.raise_for_status()
        return {"message": "Task updated!", "task": response.json()}

    @mcp.tool()
    async def delete_task(task_id: str) -> dict:
        """Delete a task permanently."""
        if err := guarded_tool("delete_task"):
            return err

        response = await delete_task_request(task_id=task_id)
        if response.status_code == 404:
            return {"error": f"Task with ID '{task_id}' not found."}
        response.raise_for_status()
        return {"message": f"Task {task_id} deleted successfully!"}

    @mcp.tool()
    async def get_task_stats() -> dict:
        """Get a summary of all tasks."""
        if err := guarded_tool("get_task_stats"):
            return err

        response = await get_task_stats_request()
        response.raise_for_status()
        return response.json()

    @mcp.tool()
    async def get_pending_tasks() -> dict:
        """Get only tasks that are not yet completed."""
        if err := guarded_tool("get_pending_tasks"):
            return err

        response = await get_tasks()
        response.raise_for_status()
        all_tasks = response.json()
        pending = [t for t in all_tasks if not t["completed"]]
        return {"pending_tasks": pending, "count": len(pending)}

    @mcp.tool()
    async def get_high_priority_tasks() -> dict:
        """Get all high priority tasks."""
        if err := guarded_tool("get_high_priority_tasks"):
            return err

        response = await get_tasks()
        response.raise_for_status()
        all_tasks = response.json()
        high = [t for t in all_tasks if t["priority"] == "high"]
        return {"high_priority_tasks": high, "count": len(high)}
