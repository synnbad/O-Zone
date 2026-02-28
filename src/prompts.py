"""
Prompt templates for O-Zone MVP.

This module defines prompt templates for AI-powered recommendations
via Amazon Bedrock.
"""

RECOMMENDATION_PROMPT_TEMPLATE = """You are an air quality expert providing personalized outdoor activity recommendations.

Current Air Quality Data:
- Overall AQI: {aqi} ({category})
- Dominant Pollutant: {dominant_pollutant} (AQI: {dominant_aqi})
- Individual Pollutants: {individual_pollutants}
- Location: {location}
- Timestamp: {timestamp}

User Profile:
- Planned Activity: {activity}
- Health Sensitivity: {health_sensitivity}

{historical_context}

Provide a recommendation in JSON format with these fields:
- safety_assessment: "Safe", "Moderate Risk", or "Unsafe"
- recommendation_text: Clear guidance paragraph (2-3 sentences)
- precautions: List of specific precautions (empty array if safe)
- time_windows: List of optimal time windows in next 24h (if applicable, empty array if none)
- reasoning: Brief explanation of your assessment (1-2 sentences)

For time_windows, each should have:
- start_time: ISO 8601 datetime string
- end_time: ISO 8601 datetime string
- expected_aqi_range: [min, max] array of integers
- confidence: "High", "Medium", or "Low"

Consider:
1. Activity intensity and duration
2. Health sensitivity level
3. Current and predicted AQI trends
4. Specific pollutant risks

Return ONLY valid JSON, no additional text."""


def format_recommendation_prompt(
    overall_aqi,
    activity: str,
    health_sensitivity: str,
    historical_data: dict = None
) -> str:
    """
    Format the recommendation prompt with actual data.
    
    Args:
        overall_aqi: OverallAQI object
        activity: Activity profile
        health_sensitivity: Health sensitivity level
        historical_data: Optional dict of historical measurements
        
    Returns:
        Formatted prompt string
    """
    # Format individual pollutants
    individual_pollutants = ", ".join([
        f"{r.pollutant}: {r.aqi} ({r.category})"
        for r in overall_aqi.individual_results
    ])
    
    # Format historical context if available
    if historical_data and any(historical_data.values()):
        historical_context = "Historical Trends (last 24 hours):\n"
        for pollutant, measurements in historical_data.items():
            if measurements:
                values = [m.value for m in measurements]
                avg_value = sum(values) / len(values)
                trend = "increasing" if values[-1] > values[0] else "decreasing"
                historical_context += f"- {pollutant}: Average {avg_value:.1f}, {trend}\n"
    else:
        historical_context = "Historical Trends: No historical data available for this location."
    
    return RECOMMENDATION_PROMPT_TEMPLATE.format(
        aqi=overall_aqi.aqi,
        category=overall_aqi.category,
        dominant_pollutant=overall_aqi.dominant_pollutant,
        dominant_aqi=max(r.aqi for r in overall_aqi.individual_results),
        individual_pollutants=individual_pollutants,
        location=f"{overall_aqi.location.name}, {overall_aqi.location.country}",
        timestamp=overall_aqi.timestamp.strftime("%Y-%m-%d %H:%M UTC"),
        activity=activity,
        health_sensitivity=health_sensitivity,
        historical_context=historical_context
    )
