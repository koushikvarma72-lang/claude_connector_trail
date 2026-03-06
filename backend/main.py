from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
import uuid
import os

app = FastAPI(title="Task Manager API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tasks_db: dict = {}

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Optional[Literal["low", "medium", "high"]] = "medium"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    completed: Optional[bool] = None

class Task(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    completed: bool
    created_at: str

@app.get("/")
def root():
    return {"message": "Task Manager API is running!"}

@app.get("/tasks", response_model=List[Task])
def get_all_tasks():
    return list(tasks_db.values())

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    task_id = str(uuid.uuid4())[:8]
    new_task = {
        "id": task_id,
        "title": task.title,
        "description": task.description or "",
        "priority": task.priority or "medium",
        "completed": False,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    tasks_db[task_id] = new_task
    return new_task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, updates: TaskUpdate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    task = tasks_db[task_id]
    if updates.title is not None: task["title"] = updates.title
    if updates.description is not None: task["description"] = updates.description
    if updates.priority is not None: task["priority"] = updates.priority
    if updates.completed is not None: task["completed"] = updates.completed
    tasks_db[task_id] = task
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"message": f"Task {task_id} deleted"}

@app.get("/tasks/stats/summary")
def get_stats():
    all_tasks = list(tasks_db.values())
    return {
        "total": len(all_tasks),
        "completed": len([t for t in all_tasks if t["completed"]]),
        "pending": len([t for t in all_tasks if not t["completed"]]),
        "high_priority": len([t for t in all_tasks if t["priority"] == "high"]),
    }

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)

