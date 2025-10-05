from datetime import datetime
from typing import Optional, Dict, Any
from app.db.models import TaskStatus, AnalysisTask
from app.utils.logging import get_logger

logger = get_logger(__name__)

def get_current_stage(status: TaskStatus) -> str:
    """Get human-readable current stage description."""
    stage_map = {
        TaskStatus.PENDING: "Queued for processing",
        TaskStatus.PROCESSING: "Analyzing code",
        TaskStatus.COMPLETED: "Analysis complete",
        TaskStatus.FAILED: "Analysis failed"
    }
    return stage_map.get(status, "Unknown")


def estimate_completion_time(task: AnalysisTask) -> str:
    """Estimate remaining completion time based on progress."""
    if not task.started_at or task.total_files == 0:
        return "Calculating..."
    
    elapsed = datetime.now(datetime.timezone.utc) - task.started_at
    if task.processed_files == 0:
        return "5-10 minutes"
    
    avg_time_per_file = elapsed.total_seconds() / task.processed_files
    remaining_files = task.total_files - task.processed_files
    estimated_seconds = remaining_files * avg_time_per_file
    
    if estimated_seconds < 60:
        return f"{int(estimated_seconds)} seconds"
    elif estimated_seconds < 3600:
        return f"{int(estimated_seconds / 60)} minutes"
    else:
        return f"{int(estimated_seconds / 3600)} hours"
    

def update_task_status(
    task_id: str,
    status: str,
    results: Optional[Dict[str, Any]] = None,
    error_message: Optional[str] = None,
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    current_file: Optional[str] = None,
    processed_files: Optional[int] = None,
    total_files: Optional[int] = None
):
    """Update task status in database."""
    try:
        from app.db.database import get_db_session
        from app.db.models import AnalysisTask
        
        with get_db_session() as db:
            task = db.query(AnalysisTask).filter(
                AnalysisTask.task_id == task_id
            ).first()
            
            if task:
                task.status = status
                task.updated_at = datetime.now(datetime.timezone.utc)
                
                if results is not None:
                    task.results = results
                if error_message is not None:
                    task.error_message = error_message
                if started_at is not None:
                    task.started_at = started_at
                if completed_at is not None:
                    task.completed_at = completed_at
                if current_file is not None:
                    task.current_file = current_file
                if processed_files is not None:
                    task.processed_files = processed_files
                if total_files is not None:
                    task.total_files = total_files
                
                db.commit()
                logger.info(f"Updated task {task_id} status to {status}")
            else:
                logger.warning(f"Task {task_id} not found in database")
                
    except Exception as e:
        logger.error(f"Failed to update task {task_id} status: {e}")