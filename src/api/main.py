"""
O-Zone API - Main Application

FastAPI application providing REST API for air quality data, recommendations, and chatbot.
"""

import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="O-Zone API",
    description="Air quality decision platform API with AI-powered recommendations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all API requests with timing information"""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Log response
    logger.info(
        f"Response: {request.method} {request.url.path} "
        f"- Status: {response.status_code} - Duration: {duration:.3f}s"
    )
    
    return response

# CORS configuration for demo (allow all origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from src.api.routers import health, locations, chat, recommendations, map_stations

# Register routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(locations.router, prefix="/api", tags=["Locations"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(recommendations.router, prefix="/api", tags=["Recommendations"])
app.include_router(map_stations.router, prefix="/api", tags=["Map"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint accessed")
    return {
        "message": "O-Zone API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

# Lambda handler for AWS deployment
handler = Mangum(app)

# Log startup
logger.info("O-Zone API initialized successfully")
logger.info(f"Environment: AWS_REGION={os.getenv('OZONE_AWS_REGION', os.getenv('AWS_REGION', 'not set'))}")
logger.info(f"OpenAQ API Key configured: {bool(os.getenv('OPENAQ_API_KEY'))}")
logger.info(f"AWS credentials configured: {bool(os.getenv('OZONE_AWS_ACCESS_KEY_ID', os.getenv('AWS_ACCESS_KEY_ID')))}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting development server on http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
