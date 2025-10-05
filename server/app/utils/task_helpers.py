from datetime import datetime
from app.db.models import TaskStatus, AnalysisTask


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
    
    elapsed = datetime.utcnow() - task.started_at
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