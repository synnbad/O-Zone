"""
O-Zone API - Main Application

FastAPI application providing REST API for air quality data, recommendations, and chatbot.
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from dotenv import load_dotenv

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
    return {
        "message": "O-Zone API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

# Lambda handler for AWS deployment
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
