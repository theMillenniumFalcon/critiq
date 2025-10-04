from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uuid

router = APIRouter(prefix="/api/v1")

class AnalyzeRequest(BaseModel):
    repo_url: str
    pr_number: int


class AnalyzeResponse(BaseModel):
    task_id: str
    status: str


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_pr(request: Request, body: AnalyzeRequest):
    """Create a simple analysis task (in-memory) and return a task id.

    This is a stub that enqueues no real work; Celery integration comes later.
    """
    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "repo_url": body.repo_url,
        "pr_number": body.pr_number,
        "status": "queued",
        "results": None,
    }

    # store in app state tasks dict
    request.app.state.tasks[task_id] = task

    return {"task_id": task_id, "status": "queued"}


@router.get("/status/{task_id}")
async def status(task_id: str, request: Request):
    tasks: Dict[str, Any] = request.app.state.tasks
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return {"task_id": task_id, "status": task.get("status")}


@router.get("/results/{task_id}")
async def results(task_id: str, request: Request):
    tasks: Dict[str, Any] = request.app.state.tasks
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    if task.get("results") is None:
        return {"task_id": task_id, "results": None}
    return {"task_id": task_id, "results": task.get("results")}
