from fastapi import APIRouter
from .sh_response import Respons
from ..configs.settings import db_settings
from ..configs.database import DatabaseManager
from ..configs.logging import get_logger

health_check_router = APIRouter(tags=["Health Path"])
logger = get_logger("health")

@health_check_router.get("/health", response_model=Respons[dict])
async def health():
    """Health check endpoint."""
    try:
        # Basic application health
        app_health = {
            "status": "healthy",
            "app_name": db_settings.APP_NAME,
            "version": db_settings.APP_VERSION,
            "environment": db_settings.ENVIRONMENT,
            "debug": db_settings.DEBUG
        }
        
        # Database health check
        db_health = DatabaseManager.health_check()
        
        # Overall health status
        overall_status = "healthy" if db_health["status"] == "healthy" else "degraded"
        
        health_data = {
            "overall_status": overall_status,
            "application": app_health,
            "database": db_health
        }
        
        logger.info(f"Health check completed with status: {overall_status}")
        
        return Respons[dict](
            details=f"Health check successful - Status: {overall_status}",
            data=[health_data],
            success=True,
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Respons[dict](
            details="Health check failed",
            error=str(e),
            data=[],
            success=False,
            status_code=500
        )

@health_check_router.get("/health/db", response_model=Respons[dict])
async def database_health():
    """Database-specific health check endpoint."""
    try:
        db_health = DatabaseManager.health_check()
        
        if db_health["status"] == "healthy":
            return Respons[dict](
                details="Database health check successful",
                data=[db_health],
                success=True,
                status_code=200
            )
        else:
            return Respons[dict](
                details="Database health check failed",
                error=db_health.get("error", "Unknown database error"),
                data=[db_health],
                success=False,
                status_code=503
            )
            
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return Respons[dict](
            details="Database health check failed",
            error=str(e),
            data=[],
            success=False,
            status_code=500
        )