"""
Locations Router

Handles location search and AQI data retrieval.
"""

import sys
import os
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_fetcher import get_location, get_current_measurements
from src.aqi_calculator import calculate_overall_aqi
from src import demo_data

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/locations/search")
async def search_locations(q: str = Query(..., description="Location query (city name or coordinates)")):
    """
    Search for locations by name or coordinates.
    
    Args:
        q: Location query string
        
    Returns:
        List of matching locations with basic info
    """
    try:
        logger.info(f"Location search: {q}")
        
        # Try to get location
        location = get_location(q)
        
        if not location:
            # Return empty results
            return {
                "results": [],
                "metadata": {
                    "source": "api",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "query": q
                }
            }
        
        # Determine data source
        source = "demo" if "Demo Data" in location.providers else "api"
        
        # Return location result
        return {
            "results": [{
                "id": f"{location.name}_{location.country}".replace(" ", "_").lower(),
                "name": location.name,
                "country": location.country,
                "coordinates": {
                    "latitude": location.coordinates[0],
                    "longitude": location.coordinates[1]
                },
                "providers": location.providers
            }],
            "metadata": {
                "source": source,
                "timestamp": datetime.now(UTC).isoformat(),
                "query": q
            }
        }
        
    except Exception as e:
        logger.error(f"Error searching locations: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching locations: {str(e)}")


@router.get("/locations/{location_id}/aqi")
async def get_location_aqi(location_id: str):
    """
    Get current AQI data for a location.
    
    Args:
        location_id: Location identifier
        
    Returns:
        AQI data with pollutant breakdown
    """
    try:
        logger.info(f"AQI request for location: {location_id}")
        
        # Parse location_id back to location name
        # Format: "san_francisco_united_states" -> "San Francisco"
        location_name = location_id.replace("_", " ").title()
        
        # Get location
        location = get_location(location_name)
        
        if not location:
            raise HTTPException(status_code=404, detail=f"Location not found: {location_name}")
        
        # Get current measurements
        measurements = get_current_measurements(location)
        
        if not measurements:
            raise HTTPException(status_code=404, detail=f"No air quality data available for {location.name}")
        
        # Calculate AQI
        overall_aqi = calculate_overall_aqi(measurements)
        
        # Determine data source
        source = "demo" if "Demo Data" in location.providers else "api"
        
        # Format response
        return {
            "location": {
                "id": location_id,
                "name": location.name,
                "country": location.country,
                "coordinates": {
                    "latitude": location.coordinates[0],
                    "longitude": location.coordinates[1]
                }
            },
            "overall": {
                "aqi": overall_aqi.aqi,
                "category": overall_aqi.category,
                "color": overall_aqi.color,
                "dominant_pollutant": overall_aqi.dominant_pollutant,
                "timestamp": overall_aqi.timestamp.isoformat()
            },
            "pollutants": [
                {
                    "name": result.pollutant,
                    "aqi": result.aqi,
                    "category": result.category,
                    "color": result.color,
                    "value": result.concentration,
                    "unit": "µg/m³"  # Standard unit for air quality
                }
                for result in overall_aqi.individual_results
            ],
            "metadata": {
                "source": source
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting AQI data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting AQI data: {str(e)}")


from datetime import datetime, UTC
