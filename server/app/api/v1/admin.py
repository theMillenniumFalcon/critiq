"""Admin API endpoints for system monitoring and management."""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from app.services.vector_cache import vector_cache
from app.utils.redis_client import redis_client
from app.services.github_service import GitHubService
from app.db.database import get_db
from app.db.models import AnalysisTask
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