"""
Recommendations Router

Generates AI-powered activity recommendations based on AQI.
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

from src.data_fetcher import get_location, get_current_measurements, get_historical_measurements
from src.aqi_calculator import calculate_overall_aqi
from src.bedrock_client import get_recommendation

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/recommendations")
async def get_recommendations(
    location: str = Query(..., description="Location name"),
    activity: str = Query(..., description="Activity type"),
    health: str = Query("None", description="Health sensitivity")
):
    """
    Get AI-powered activity recommendations.
    
    Args:
        location: Location name
        activity: Activity type (e.g., Walking, Running, Cycling)
        health: Health sensitivity (e.g., None, Asthma, Allergies)
        
    Returns:
        Recommendation with safety assessment and precautions
    """
    try:
        logger.info(f"Recommendation request: location={location}, activity={activity}, health={health}")
        
        # Get location
        location_obj = get_location(location)
        if not location_obj:
            raise HTTPException(status_code=404, detail=f"Location not found: {location}")
        
        # Get current measurements
        measurements = get_current_measurements(location_obj)
        if not measurements:
            raise HTTPException(status_code=404, detail=f"No air quality data available for {location}")
        
        # Calculate AQI
        overall_aqi = calculate_overall_aqi(measurements)
        
        # Get historical data (optional)
        try:
            historical_data = get_historical_measurements(location_obj, hours=24)
        except:
            historical_data = None
        
        # Generate recommendation
        recommendation = get_recommendation(
            overall_aqi=overall_aqi,
            activity=activity,
            health_sensitivity=health,
            historical_data=historical_data
        )
        
        # Determine source
        import os
        has_bedrock = bool(os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'))
        source = "ai" if has_bedrock else "rule-based"
        
        # Format response
        return {
            "safety_assessment": recommendation.safety_assessment,
            "recommendation_text": recommendation.recommendation_text,
            "precautions": recommendation.precautions,
            "time_windows": [
                {
                    "start_time": tw.start_time.isoformat(),
                    "end_time": tw.end_time.isoformat(),
                    "expected_aqi_range": tw.expected_aqi_range,
                    "confidence": tw.confidence
                }
                for tw in recommendation.time_windows
            ] if recommendation.time_windows else [],
            "reasoning": recommendation.reasoning if hasattr(recommendation, 'reasoning') else "",
            "metadata": {
                "source": source,
                "location": location_obj.name,
                "current_aqi": overall_aqi.aqi
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")
