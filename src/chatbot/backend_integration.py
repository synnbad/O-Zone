"""
Backend Integration Module for O-Zone Chatbot

Provides unified interface to O-Zone MVP backend services.
Translates backend errors to user-friendly messages and implements fallback logic.
"""

import logging
from typing import Optional

from src.models import Location, OverallAQI, RecommendationResponse, Measurement
from src.data_fetcher import get_location, get_current_measurements, get_historical_measurements
from src.aqi_calculator import calculate_overall_aqi
from src.bedrock_client import get_recommendation

logger = logging.getLogger(__name__)


class LocationNotFoundError(Exception):
    """Raised when location cannot be resolved"""
    pass


class NoDataAvailableError(Exception):
    """Raised when no air quality data is available"""
    pass


def resolve_location(location_query: str) -> Location:
    """
    Resolve location query to Location object using data_fetcher.
    
    Translates backend errors to chatbot-friendly LocationNotFoundError with suggestions.
    
    Args:
        location_query: User's location input (city name, coordinates, etc.)
        
    Returns:
        Location object with name, coordinates, country, and providers
        
    Raises:
        LocationNotFoundError: If location cannot be resolved, with user-friendly message
    """
    try:
        location = get_location(location_query)
        
        if location is None:
            logger.warning(f"Location not found: '{location_query}'")
            raise LocationNotFoundError(
                f"I couldn't find air quality data for '{location_query}'. "
                f"This could mean the location name might be misspelled or there are no monitoring stations in that area. "
                f"Please try a nearby larger city or check the spelling."
            )
        
        logger.info(f"Resolved location: {location.name}, {location.country}")
        return location
        
    except LocationNotFoundError:
        # Re-raise our custom error
        raise
    except Exception as e:
        logger.error(f"Location resolution failed for '{location_query}': {e}")
        raise LocationNotFoundError(
            f"I'm having trouble looking up '{location_query}' right now. "
            f"Please try again in a moment, or try a different location."
        ) from e


def fetch_current_aqi(location: Location) -> OverallAQI:
    """
    Fetch current AQI for location by calling data_fetcher and aqi_calculator.
    
    Args:
        location: Location object
        
    Returns:
        OverallAQI object with current air quality assessment
        
    Raises:
        NoDataAvailableError: If no measurements available, with user-friendly message
    """
    try:
        # Get current measurements from data fetcher
        measurements = get_current_measurements(location)
        
        if not measurements:
            logger.warning(f"No measurements available for {location.name}")
            raise NoDataAvailableError(
                f"I found {location.name}, but there's no recent air quality data available. "
                f"This sometimes happens with monitoring stations that update infrequently. "
                f"You could try a nearby larger city or check back in a few hours."
            )
        
        # Calculate overall AQI
        overall_aqi = calculate_overall_aqi(measurements)
        logger.info(f"Fetched AQI for {location.name}: {overall_aqi.aqi} ({overall_aqi.category})")
        return overall_aqi
        
    except NoDataAvailableError:
        # Re-raise our custom error
        raise
    except ValueError as e:
        # Handle AQI calculation errors
        logger.error(f"Error calculating AQI for {location.name}: {e}")
        raise NoDataAvailableError(
            f"I encountered an issue processing the air quality data for {location.name}. "
            f"Please try a different location or try again later."
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error fetching AQI for {location.name}: {e}")
        raise NoDataAvailableError(
            f"I'm having trouble retrieving air quality data for {location.name} right now. "
            f"Please try again in a moment."
        ) from e


def fetch_historical_data(location: Location, hours: int = 24) -> dict[str, list[Measurement]]:
    """
    Retrieve historical measurements for trend analysis.
    
    Args:
        location: Location object
        hours: Number of hours of historical data to retrieve (24 or 168 for 7 days)
        
    Returns:
        Dictionary mapping pollutant names to lists of Measurement objects
        Returns empty dict if no historical data available
    """
    try:
        historical_data = get_historical_measurements(location, hours)
        
        if historical_data:
            total_measurements = sum(len(measurements) for measurements in historical_data.values())
            logger.info(f"Fetched {hours}h historical data for {location.name}: {total_measurements} measurements")
        else:
            logger.info(f"No historical data available for {location.name}")
        
        return historical_data
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {location.name}: {e}")
        # Return empty dict instead of raising - historical data is optional
        return {}


def generate_recommendation(
    overall_aqi: OverallAQI,
    activity: str,
    health_sensitivity: str,
    historical_data: Optional[dict] = None
) -> RecommendationResponse:
    """
    Generate AI-powered recommendation using bedrock_client.
    
    Implements fallback logic when Bedrock is unavailable.
    
    Args:
        overall_aqi: Current air quality assessment
        activity: User's planned activity (Walking, Jogging/Running, etc.)
        health_sensitivity: User's health sensitivity level (None, Allergies, etc.)
        historical_data: Optional historical measurements for trend analysis
        
    Returns:
        RecommendationResponse with safety assessment, guidance, precautions, and time windows
    """
    try:
        recommendation = get_recommendation(
            overall_aqi=overall_aqi,
            activity=activity,
            health_sensitivity=health_sensitivity,
            historical_data=historical_data
        )
        logger.info(f"Generated AI recommendation for {activity} with {health_sensitivity} sensitivity")
        return recommendation
        
    except Exception as e:
        logger.warning(f"Bedrock recommendation failed, using fallback: {e}")
        return generate_fallback_recommendation(overall_aqi, activity, health_sensitivity)


def generate_fallback_recommendation(
    overall_aqi: OverallAQI,
    activity: str,
    health_sensitivity: str
) -> RecommendationResponse:
    """
    Generate rule-based recommendation when AI is unavailable.
    
    Uses AQI thresholds and health profile to provide basic safety guidance.
    
    Args:
        overall_aqi: Current air quality assessment
        activity: User's planned activity
        health_sensitivity: User's health sensitivity level
        
    Returns:
        RecommendationResponse with rule-based guidance
    """
    aqi = overall_aqi.aqi
    category = overall_aqi.category
    dominant = overall_aqi.dominant_pollutant
    
    # Activity intensity mapping
    high_intensity = activity in ["Jogging/Running", "Cycling", "Sports Practice"]
    moderate_intensity = activity in ["Walking", "Child Outdoor Play"]
    low_intensity = activity in ["Outdoor Study/Work"]
    
    # Health sensitivity factor
    sensitive = health_sensitivity != "None"
    very_sensitive = health_sensitivity in ["Asthma/Respiratory", "Pregnant", "Child/Elderly"]
    
    # Generate recommendation based on AQI and user profile
    if aqi <= 50:  # Good
        safety_assessment = "Safe"
        recommendation_text = (
            f"Air quality is excellent (AQI {aqi}). "
            f"Perfect conditions for all outdoor activities including {activity.lower()}. "
            f"No health concerns for any group."
        )
        precautions = []
    
    elif aqi <= 100:  # Moderate
        if very_sensitive and high_intensity:
            safety_assessment = "Moderate Risk"
            recommendation_text = (
                f"Air quality is moderate (AQI {aqi}). "
                f"Given your {health_sensitivity.lower()} sensitivity and high-intensity activity ({activity.lower()}), "
                f"consider reducing duration or intensity. Monitor how you feel."
            )
            precautions = [
                "Consider shorter duration or lower intensity",
                "Take breaks if you experience any discomfort",
                "Have medication readily available if applicable"
            ]
        else:
            safety_assessment = "Safe"
            recommendation_text = (
                f"Air quality is acceptable (AQI {aqi}). "
                f"Most people can enjoy {activity.lower()} without concerns. "
                f"Sensitive individuals should monitor symptoms."
            )
            precautions = ["Monitor for any unusual symptoms"] if sensitive else []
    
    elif aqi <= 150:  # Unhealthy for Sensitive Groups
        if very_sensitive:
            safety_assessment = "Unsafe"
            recommendation_text = (
                f"Air quality is unhealthy for sensitive groups (AQI {aqi}). "
                f"With {health_sensitivity.lower()} sensitivity, consider postponing {activity.lower()} "
                f"or moving indoors. The dominant pollutant is {dominant}."
            )
            precautions = [
                "Consider rescheduling outdoor activities",
                "If you must go out, reduce intensity and duration significantly",
                "Wear a mask (N95 or KN95) if available",
                "Have medication readily available",
                "Monitor symptoms closely and move indoors if discomfort occurs"
            ]
        elif high_intensity:
            safety_assessment = "Moderate Risk"
            recommendation_text = (
                f"Air quality is unhealthy for sensitive groups (AQI {aqi}). "
                f"High-intensity activities like {activity.lower()} may cause discomfort. "
                f"Consider reducing intensity or duration."
            )
            precautions = [
                "Reduce activity intensity and duration",
                "Take frequent breaks",
                "Stay hydrated",
                "Move indoors if you experience any discomfort"
            ]
        else:
            safety_assessment = "Moderate Risk"
            recommendation_text = (
                f"Air quality is moderate (AQI {aqi}). "
                f"General population can continue {activity.lower()} with minor adjustments. "
                f"Sensitive groups should take precautions."
            )
            precautions = [
                "Limit prolonged outdoor exertion",
                "Monitor for symptoms like coughing or shortness of breath"
            ]
    
    elif aqi <= 200:  # Unhealthy
        safety_assessment = "Unsafe"
        if high_intensity:
            recommendation_text = (
                f"Air quality is unhealthy (AQI {aqi}). "
                f"High-intensity activities like {activity.lower()} are not recommended. "
                f"Everyone may experience health effects. Consider indoor alternatives."
            )
            precautions = [
                "Strongly consider moving activity indoors",
                "If you must go out, significantly reduce intensity and duration",
                "Wear a high-quality mask (N95 or KN95)",
                "Avoid prolonged outdoor exposure",
                "Monitor symptoms and seek medical attention if needed"
            ]
        else:
            recommendation_text = (
                f"Air quality is unhealthy (AQI {aqi}). "
                f"Limit outdoor time for {activity.lower()}. "
                f"Everyone should reduce prolonged or heavy exertion."
            )
            precautions = [
                "Limit outdoor time to essential activities only",
                "Wear a mask if going outside",
                "Keep windows closed",
                "Use air purifiers indoors if available"
            ]
    
    elif aqi <= 300:  # Very Unhealthy
        safety_assessment = "Unsafe"
        recommendation_text = (
            f"Air quality is very unhealthy (AQI {aqi}). "
            f"Outdoor activities like {activity.lower()} should be avoided. "
            f"Health alert: everyone may experience serious health effects."
        )
        precautions = [
            "Avoid all outdoor activities",
            "Stay indoors with windows and doors closed",
            "Use air purifiers if available",
            "Wear N95/KN95 masks if you must go outside",
            "Seek medical attention if experiencing symptoms",
            "Check on vulnerable family members and neighbors"
        ]
    
    else:  # Hazardous (>300)
        safety_assessment = "Unsafe"
        recommendation_text = (
            f"Air quality is hazardous (AQI {aqi}). "
            f"Emergency conditions. All outdoor activities including {activity.lower()} must be avoided. "
            f"Everyone is at risk of serious health effects."
        )
        precautions = [
            "DO NOT go outside unless absolutely necessary",
            "Stay indoors with all windows and doors sealed",
            "Use air purifiers on high settings",
            "Wear N95/KN95 masks even indoors if air quality is poor",
            "Seek immediate medical attention for any respiratory symptoms",
            "Follow local emergency guidelines and evacuation orders if issued",
            "Keep emergency contacts readily available"
        ]
    
    logger.info(f"Generated fallback recommendation: {safety_assessment} for AQI {aqi}")
    
    return RecommendationResponse(
        safety_assessment=safety_assessment,
        recommendation_text=recommendation_text,
        precautions=precautions,
        time_windows=[],  # No predictions without AI
        reasoning=f"Rule-based recommendation for AQI {aqi} ({category}), activity: {activity}, sensitivity: {health_sensitivity}"
    )
