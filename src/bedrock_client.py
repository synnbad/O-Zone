"""
Bedrock Client module for O-Zone MVP.

This module handles AI-powered recommendations via Amazon Bedrock
using Claude 3.5 Sonnet.
"""

import boto3
import json
import time
from datetime import datetime, timedelta, UTC
from typing import Optional

from src.config import Config
from src.models import OverallAQI, RecommendationResponse, TimeWindow
from src.prompts import format_recommendation_prompt


def get_recommendation(
    overall_aqi: OverallAQI,
    activity: str,
    health_sensitivity: str,
    historical_data: Optional[dict] = None
) -> RecommendationResponse:
    """
    Generate AI-powered recommendation using Amazon Bedrock.
    
    Falls back to rule-based recommendations if AWS is not configured.
    
    Args:
        overall_aqi: Current air quality assessment
        activity: User's planned activity
        health_sensitivity: User's health sensitivity level
        historical_data: Optional historical measurements
        
    Returns:
        RecommendationResponse with AI-generated or fallback guidance
    """
    # Check if AWS credentials are configured
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
        print("ℹ️  Using fallback recommendations (AWS not configured)")
        return _get_fallback_recommendation(overall_aqi, activity, health_sensitivity)
    
    try:
        # Construct prompt
        prompt = _construct_prompt(overall_aqi, activity, health_sensitivity, historical_data)
        
        # Call Bedrock
        response_text = _call_bedrock(prompt)
        
        # Parse response
        recommendation = _parse_response(response_text)
        
        return recommendation
    
    except Exception as e:
        print(f"Error generating recommendation (first attempt): {e}")
        
        # Retry once
        try:
            time.sleep(1)
            prompt = _construct_prompt(overall_aqi, activity, health_sensitivity, historical_data)
            response_text = _call_bedrock(prompt)
            recommendation = _parse_response(response_text)
            return recommendation
        
        except Exception as retry_error:
            print(f"Error generating recommendation (retry): {retry_error}")
            
            # Return fallback response
            return _get_fallback_recommendation(overall_aqi, activity, health_sensitivity)


def _construct_prompt(
    overall_aqi: OverallAQI,
    activity: str,
    health_sensitivity: str,
    historical_data: Optional[dict]
) -> str:
    """Construct structured prompt for Claude."""
    return format_recommendation_prompt(
        overall_aqi,
        activity,
        health_sensitivity,
        historical_data
    )


def _call_bedrock(prompt: str) -> str:
    """
    Call Amazon Bedrock API with Claude 3.5 Sonnet.
    
    Args:
        prompt: Formatted prompt string
        
    Returns:
        Raw response text from Claude
        
    Raises:
        Exception: If Bedrock API call fails
    """
    try:
        # Initialize Bedrock client with credentials
        client_kwargs = {
            'service_name': 'bedrock-runtime',
            'region_name': Config.AWS_REGION,
        }
        
        # Add credentials if available
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            client_kwargs['aws_access_key_id'] = Config.AWS_ACCESS_KEY_ID
            client_kwargs['aws_secret_access_key'] = Config.AWS_SECRET_ACCESS_KEY
            
            # Add session token if present (for temporary credentials)
            if Config.AWS_SESSION_TOKEN:
                client_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
        
        bedrock = boto3.client(**client_kwargs)
        
        # Prepare request body
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.7,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Invoke model
        response = bedrock.invoke_model(
            modelId=Config.BEDROCK_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract text from Claude response
        if 'content' in response_body and len(response_body['content']) > 0:
            return response_body['content'][0]['text']
        else:
            raise Exception("Invalid response format from Bedrock")
    
    except Exception as e:
        raise Exception(f"Bedrock API call failed: {str(e)}")


def _parse_response(response_text: str) -> RecommendationResponse:
    """
    Parse Claude's JSON response into RecommendationResponse.
    
    Args:
        response_text: Raw text from Claude
        
    Returns:
        RecommendationResponse object
        
    Raises:
        Exception: If response is malformed
    """
    try:
        # Extract JSON from response (Claude might include extra text)
        response_text = response_text.strip()
        
        # Find JSON object in response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response")
        
        json_str = response_text[start_idx:end_idx]
        data = json.loads(json_str)
        
        # Validate required fields
        required_fields = [
            'safety_assessment',
            'recommendation_text',
            'precautions',
            'time_windows',
            'reasoning'
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Parse time windows
        time_windows = []
        for tw_data in data['time_windows']:
            try:
                time_window = TimeWindow(
                    start_time=datetime.fromisoformat(tw_data['start_time']),
                    end_time=datetime.fromisoformat(tw_data['end_time']),
                    expected_aqi_range=tuple(tw_data['expected_aqi_range']),
                    confidence=tw_data['confidence']
                )
                time_windows.append(time_window)
            except Exception as e:
                print(f"Warning: Could not parse time window: {e}")
                continue
        
        return RecommendationResponse(
            safety_assessment=data['safety_assessment'],
            recommendation_text=data['recommendation_text'],
            precautions=data['precautions'],
            time_windows=time_windows,
            reasoning=data['reasoning']
        )
    
    except Exception as e:
        raise Exception(f"Failed to parse Bedrock response: {str(e)}")


def _get_fallback_assessment(aqi: int) -> str:
    """Get fallback safety assessment based on AQI value."""
    if aqi <= 50:
        return "Safe"
    elif aqi <= 150:
        return "Moderate Risk"
    else:
        return "Unsafe"


def _get_fallback_recommendation(
    overall_aqi: OverallAQI,
    activity: str,
    health_sensitivity: str
) -> RecommendationResponse:
    """
    Generate rule-based recommendation when AWS is not available.
    
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
    
    # Determine safety assessment
    safety = _get_fallback_assessment(aqi)
    
    # Activity intensity mapping
    high_intensity = activity in ["Jogging/Running", "Cycling", "Sports Practice"]
    moderate_intensity = activity in ["Walking", "Child Outdoor Play"]
    low_intensity = activity in ["Outdoor Study/Work"]
    
    # Health sensitivity factor
    sensitive = health_sensitivity != "None"
    very_sensitive = health_sensitivity in ["Asthma/Respiratory", "Pregnant", "Child/Elderly"]
    
    # Generate recommendation text
    if aqi <= 50:  # Good
        recommendation_text = (
            f"Air quality is excellent (AQI {aqi}). "
            f"Perfect conditions for all outdoor activities including {activity.lower()}. "
            f"No health concerns for any group."
        )
        precautions = []
    
    elif aqi <= 100:  # Moderate
        if very_sensitive and high_intensity:
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
            recommendation_text = (
                f"Air quality is acceptable (AQI {aqi}). "
                f"Most people can enjoy {activity.lower()} without concerns. "
                f"Sensitive individuals should monitor symptoms."
            )
            precautions = ["Monitor for any unusual symptoms"] if sensitive else []
    
    elif aqi <= 150:  # Unhealthy for Sensitive Groups
        if very_sensitive:
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
    
    return RecommendationResponse(
        safety_assessment=safety,
        recommendation_text=recommendation_text,
        precautions=precautions,
        time_windows=[],  # No predictions without AI
        reasoning=f"Rule-based recommendation for AQI {aqi} ({category}), activity: {activity}, sensitivity: {health_sensitivity}"
    )

