"""
Health Check Router

Provides health check endpoint for monitoring.
"""

from fastapi import APIRouter
from datetime import datetime, UTC

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and timestamp.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0",
        "service": "O-Zone API"
    }
