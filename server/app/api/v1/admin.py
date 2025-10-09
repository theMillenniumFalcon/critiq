"""Admin API endpoints for system monitoring and management."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.services.vector_cache import vector_cache
from app.utils.redis_client import redis_client
from app.services.github_service import GitHubService
from app.db.database import get_db
from app.db.models import AnalysisTask, TaskStatus
from app.utils.logging import get_logger

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

logger = get_logger(__name__)


@router.get("/health", tags=["Admin"])
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check for all system components.
    
    This endpoint checks the status of Redis, GitHub API, Vector Cache,
    and the database to provide a complete system health overview.
    """
    try:
        logger.info("Starting detailed health check")
        
        health_status = {
            "api": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "components": {}
        }
        
        # Check Redis
        try:
            redis_healthy = redis_client.ping()
            health_status["components"]["redis"] = {
                "status": "healthy" if redis_healthy else "unhealthy",
                "response_time": "< 1ms"
            }
            logger.info("Redis health check completed")
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            health_status["components"]["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check GitHub API
        try:
            github_service = GitHubService()
            github_health = await github_service.health_check()
            health_status["components"]["github"] = github_health
            logger.info("GitHub API health check completed")
        except Exception as e:
            logger.error(f"GitHub API health check failed: {e}")
            health_status["components"]["github"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Vector Cache
        try:
            cache_stats = vector_cache.get_cache_statistics()
            health_status["components"]["vector_cache"] = {
                "status": "healthy",
                "total_entries": cache_stats.get("total_entries", 0),
                "hit_rate": cache_stats.get("hit_rate", "0%")
            }
            logger.info("Vector cache health check completed")
        except Exception as e:
            logger.error(f"Vector cache health check failed: {e}")
            health_status["components"]["vector_cache"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Check Database
        try:
            # Simple query to test database connectivity
            result = await db.execute(select(func.count()).select_from(AnalysisTask))
            task_count = result.scalar()
            health_status["components"]["database"] = {
                "status": "healthy",
                "total_tasks": task_count
            }
            logger.info("Database health check completed")
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            health_status["components"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
        
        # Determine overall status
        component_statuses = [
            comp.get("status", "unhealthy") 
            for comp in health_status["components"].values()
        ]
        
        if all(status == "healthy" for status in component_statuses):
            health_status["status"] = "healthy"
        elif any(status == "healthy" for status in component_statuses):
            health_status["status"] = "degraded"
        else:
            health_status["status"] = "unhealthy"
        
        logger.info(f"Health check completed with status: {health_status['status']}")
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )


@router.get("/cache/stats", tags=["Admin"])
async def get_cache_statistics():
    """
    Get vector cache usage statistics.
    
    This endpoint provides comprehensive statistics about the vector cache,
    including total entries, cache size, hit rate, and breakdowns by language
    and analysis type.
    """
    try:
        logger.info("Fetching cache statistics")
        
        stats = vector_cache.get_cache_statistics()
        
        logger.info(f"Cache statistics retrieved: {stats.get('total_entries', 0)} entries")
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache stats: {str(e)}"
        )


@router.post("/cache/cleanup", tags=["Admin"])
async def cleanup_cache(days_old: int = 30):
    """
    Clean up old cache entries.
    
    This endpoint removes cache entries older than the specified number of days
    to free up storage space and maintain cache performance.
    
    Args:
        days_old: Number of days threshold for cleanup (default: 30)
    """
    try:
        logger.info(f"Starting cache cleanup for entries older than {days_old} days")
        
        removed_count = vector_cache.cleanup_old_entries(days_old)
        
        logger.info(f"Cache cleanup completed: {removed_count} entries removed")
        
        return {
            "message": f"Successfully cleaned up {removed_count} old cache entries",
            "removed_entries": removed_count,
            "days_threshold": days_old
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup cache: {str(e)}"
        )


@router.get("/tasks/stats", tags=["Admin"])
async def get_task_statistics(db: AsyncSession = Depends(get_db)):
    """
    Get analysis task statistics.
    
    This endpoint provides comprehensive statistics about analysis tasks,
    including counts by status, recent task information, and performance metrics
    such as average processing time.
    """
    try:
        logger.info("Fetching task statistics")
        
        # Count tasks by status
        status_counts = {}
        for status in TaskStatus:
            result = await db.execute(
                select(func.count(AnalysisTask.id)).where(
                    AnalysisTask.status == status
                )
            )
            status_counts[status.value] = result.scalar()
        
        logger.info(f"Task status counts calculated: {sum(status_counts.values())} total tasks")
        
        # Get recent task metrics
        recent_tasks_result = await db.execute(
            select(AnalysisTask).order_by(AnalysisTask.created_at.desc()).limit(10)
        )
        recent_tasks = recent_tasks_result.scalars().all()
        
        # Calculate average processing time for completed tasks
        completed_tasks_result = await db.execute(
            select(AnalysisTask).where(
                AnalysisTask.status == TaskStatus.COMPLETED,
                AnalysisTask.started_at.isnot(None),
                AnalysisTask.completed_at.isnot(None)
            ).limit(50)
        )
        completed_tasks = completed_tasks_result.scalars().all()
        
        avg_processing_time = 0
        if completed_tasks:
            total_time = sum(
                (task.completed_at - task.started_at).total_seconds()
                for task in completed_tasks
                if task.started_at and task.completed_at
            )
            avg_processing_time = total_time / len(completed_tasks)
        
        logger.info(f"Average processing time calculated: {avg_processing_time:.2f} seconds")
        
        return {
            "status_counts": status_counts,
            "total_tasks": sum(status_counts.values()),
            "recent_tasks": [
                {
                    "task_id": task.task_id,
                    "status": task.status.value,
                    "repo_url": task.repo_url,
                    "pr_number": task.pr_number,
                    "created_at": task.created_at.isoformat(),
                    "processing_time": (
                        (task.completed_at - task.started_at).total_seconds()
                        if task.started_at and task.completed_at
                        else None
                    )
                }
                for task in recent_tasks
            ],
            "metrics": {
                "average_processing_time_seconds": round(avg_processing_time, 2),
                "average_processing_time_minutes": round(avg_processing_time / 60, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get task statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task stats: {str(e)}"
        )


@router.get("/system/info", tags=["Admin"])
async def get_system_info():
    """
    Get system information and configuration.
    
    This endpoint provides details about the system version, environment,
    enabled features, and configuration settings including supported languages
    and caching parameters.
    """
    try:
        logger.info("Fetching system information")
        
        system_info = {
            "version": "1.0.0",
            "environment": "development",  # This could be set from env var
            "features": {
                "vector_caching": bool(vector_cache.openai_client),
                "github_integration": True,
                "multiple_analysis_types": True,
                "async_processing": True
            },
            "configuration": {
                "embedding_model": vector_cache.embedding_model,
                "vector_dimension": vector_cache.vector_dimension,
                "similarity_threshold": vector_cache.similarity_threshold,
                "supported_languages": [
                    "python", "javascript", "typescript", "java", "cpp", "c",
                    "csharp", "go", "rust", "php", "ruby", "swift", "kotlin"
                ]
            }
        }
        
        logger.info("System information retrieved successfully")
        
        return system_info
        
    except Exception as e:
        logger.error(f"Failed to get system information: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system info: {str(e)}"
        )