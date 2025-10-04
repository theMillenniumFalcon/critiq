from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/admin")


@router.get("/tasks")
async def list_tasks(request: Request):
    tasks: Dict[str, Any] = request.app.state.tasks
    return {"tasks": list(tasks.values())}


@router.post("/tasks/{task_id}/complete")
async def complete_task(task_id: str, request: Request):
    tasks: Dict[str, Any] = request.app.state.tasks
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")

    # fake a completed analysis
    task["status"] = "completed"
    task["results"] = {"summary": "no issues (dev stub)"}
    tasks[task_id] = task
    return {"task_id": task_id, "status": "completed"}
