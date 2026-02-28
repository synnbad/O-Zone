"""
Map Stations Router

Provides global station data for map visualization.
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src import demo_data
from src.models import GeoBounds

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stations/map")
async def get_map_stations(
    north: Optional[float] = Query(None, description="North boundary"),
    south: Optional[float] = Query(None, description="South boundary"),
    east: Optional[float] = Query(None, description="East boundary"),
    west: Optional[float] = Query(None, description="West boundary")
):
    """
    Get monitoring stations for map visualization.
    
    Args:
        north, south, east, west: Optional bounding box coordinates
        
    Returns:
        List of stations with coordinates and current AQI
    """
    try:
        logger.info(f"Map stations request: bounds=({north},{south},{east},{west})")
        
        # Create bounds if provided
        bounds = None
        if all(v is not None for v in [north, south, east, west]):
            bounds = GeoBounds(
                north=north,
                south=south,
                east=east,
                west=west
            )
        
        # Get demo stations (using demo data for reliability)
        stations = demo_data.get_demo_global_stations(bounds=bounds)
        
        # Format response
        return {
            "stations": [
                {
                    "id": station.station_id,
                    "name": station.name,
                    "country": station.country,
                    "coordinates": {
                        "latitude": station.coordinates[0],
                        "longitude": station.coordinates[1]
                    },
                    "current_aqi": station.current_aqi,
                    "aqi_category": station.aqi_category,
                    "aqi_color": station.aqi_color,
                    "last_updated": station.last_updated.isoformat() if station.last_updated else None
                }
                for station in stations
            ],
            "metadata": {
                "count": len(stations),
                "source": "demo",
                "bounds": {
                    "north": north,
                    "south": south,
                    "east": east,
                    "west": west
                } if bounds else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting map stations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting map stations: {str(e)}")
