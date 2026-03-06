import httpx

from connectors.task_manager.config import BACKEND_URL


async def get_tasks() -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.get(f"{BACKEND_URL}/tasks")


async def create_task(title: str, description: str, priority: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.post(
            f"{BACKEND_URL}/tasks",
            json={"title": title, "description": description, "priority": priority},
        )


async def complete_task(task_id: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.put(f"{BACKEND_URL}/tasks/{task_id}", json={"completed": True})


async def update_task(
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
) -> httpx.Response:
    updates = {}
    if title:
        updates["title"] = title
    if description:
        updates["description"] = description
    if priority:
        updates["priority"] = priority

    async with httpx.AsyncClient() as client:
        return await client.put(f"{BACKEND_URL}/tasks/{task_id}", json=updates)


async def delete_task(task_id: str) -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.delete(f"{BACKEND_URL}/tasks/{task_id}")


async def get_task_stats() -> httpx.Response:
    async with httpx.AsyncClient() as client:
        return await client.get(f"{BACKEND_URL}/tasks/stats/summary")
