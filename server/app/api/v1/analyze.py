from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.schemas import AnalyzeRequest, AnalyzeResponse, TaskStatusResponse, AnalysisResults
from app.db.database import get_db
from app.db.models import TaskStatus, AnalysisTask
from app.utils.logging import get_logger
from sqlalchemy import select
from app.utils.task_helpers import get_current_stage, estimate_completion_time
from app.celery_app import analyze_task

router = APIRouter(prefix="/api/v1")

logger = get_logger(__name__)

@router.post("/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
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

        # Start Celery task
        celery_task = analyze_task.delay(
            task_id=task_id,
            repo_url=str(request.repo_url),
            pr_number=request.pr_number,
            github_token=request.github_token,
            analysis_types=request.analysis_types or ["style", "bug", "security", "performance"]
        )
        
        logger.info(f"Celery task {celery_task.id} started for PR analysis {task_id}")

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


@router.get("/status/{task_id}", response_model=TaskStatusResponse, tags=["Analysis"])
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


@router.get("/results/{task_id}", response_model=AnalysisResults, tags=["Analysis"])
async def results(task_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve the analysis results for a completed task.
    
    Returns detailed analysis results including issues found, suggestions,
    and summary statistics.
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
        
        if task.status != TaskStatus.COMPLETED:
            raise HTTPException(
                status_code=400,
                detail=f"Task {task_id} is not completed. Current status: {task.status.value}"
            )
        
        if not task.results:
            raise HTTPException(
                status_code=404,
                detail=f"No results found for task {task_id}"
            )
        
        # Return structured results
        return AnalysisResults(
            task_id=task_id,
            status=task.status,
            repository=task.repo_url,
            pr_number=task.pr_number,
            files=task.results.get("files", []),
            summary=task.results.get("summary", {}),
            metadata=task.results.get("metadata", {}),
            created_at=task.created_at,
            completed_at=task.completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results for task {task_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve results: {str(e)}"
        )
