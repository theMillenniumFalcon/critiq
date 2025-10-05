from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import uuid
from app.schemas import AnalyzeRequest, AnalyzeResponse, TaskStatusResponse
from app.db.database import get_db
from app.db.models import TaskStatus, AnalysisTask
from app.utils.logging import get_logger
from sqlalchemy import select
from app.utils.task_helpers import get_current_stage, estimate_completion_time

router = APIRouter(prefix="/api/v1")

logger = get_logger(__name__)

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest, db: AsyncSession = Depends(get_db)):
    """
    Submit a GitHub pull request for analysis.
    
    This endpoint accepts a GitHub repository URL and PR number, then starts
    an asynchronous analysis task using Celery.
    """
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        logger.info(f"Starting PR analysis for {request.repo_url}/pull/{request.pr_number}")
        
        # Create task record in database
        task = AnalysisTask(
            task_id=task_id,
            repo_url=str(request.repo_url),
            pr_number=request.pr_number,
            status=TaskStatus.PENDING,
            metadata={
                "analysis_types": request.analysis_types,
                "priority": request.priority,
                "github_token_provided": request.github_token is not None
            }
        )

        db.session.add(task)
        await db.session.commit()
        await db.session.refresh(task)

        return AnalyzeResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message=f"Analysis started for PR #{request.pr_number}",
            estimated_completion_time="5-10 minutes"
        )
        
    except Exception as e:
        logger.error(f"Failed to start PR analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )


@router.get("/status/{task_id}")
async def get_status(task_id: str, db: AsyncSession = Depends(get_db)):
    """
    Check the status of an analysis task.
    
    Returns current progress, status, and estimated completion time.
    """
    try:
        # Query task from database
        result = await db.execute(
            select(AnalysisTask).where(AnalysisTask.task_id == task_id)
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )
        
        # Calculate progress
        progress_percentage = 0
        if task.total_files > 0:
            progress_percentage = (task.processed_files / task.total_files) * 100
        
        progress_info = {
            "percentage": round(progress_percentage, 2),
            "current_stage": get_current_stage(task.status),
            "files_processed": task.processed_files,
            "total_files": task.total_files
        }
        
        # Estimate completion time
        estimated_completion = None
        if task.status == TaskStatus.PROCESSING and task.started_at:
            estimated_completion = estimate_completion_time(task)
        
        return TaskStatusResponse(
            task_id=task_id,
            status=task.status,
            progress=progress_info,
            current_file=task.current_file,
            processed_files=task.processed_files,
            total_files=task.total_files,
            created_at=task.created_at,
            started_at=task.started_at,
            estimated_completion=estimated_completion,
            error_message=task.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status for {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve task status: {str(e)}"
        )


@router.get("/results/{task_id}")
async def results(task_id: str, request: Request):
    tasks: Dict[str, Any] = request.app.state.tasks
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    if task.get("results") is None:
        return {"task_id": task_id, "results": None}
    return {"task_id": task_id, "results": task.get("results")}
