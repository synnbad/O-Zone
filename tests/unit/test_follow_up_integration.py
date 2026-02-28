"""
Integration tests for enhanced follow-up handler (Task 8.1)
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.chatbot.conversation_manager import handle_follow_up
from src.chatbot.session_manager import create_session
from src.models import Location, OverallAQI, AQIResult, RecommendationResponse, TimeWindow, Measurement


@pytest.fixture
def session_with_recommendation():
    """Create a session with complete recommendation data"""
    session = create_session()
    
    location = Location(
        name="Seattle",
        coordinates=(47.6062, -122.3321),
        country="US",
        providers=["openaq"]
    )
    
    aqi = OverallAQI(
        aqi=75,
        category="Moderate",
        color="#FFFF00",
        dominant_pollutant="PM2.5",
        individual_results=[
            AQIResult(
                pollutant="PM2.5",
                concentration=25.0,
                aqi=75,
                category="Moderate",
                color="#FFFF00"
            )
        ],
        timestamp=datetime.now(),
        location=location
    )
    
    recommendation = RecommendationResponse(
        safety_assessment="Safe",
        recommendation_text="Good conditions for outdoor activities",
        precautions=["Stay hydrated"],
        time_windows=[
            TimeWindow(
                start_time=datetime(2024, 1, 1, 10, 0),
                end_time=datetime(2024, 1, 1, 12, 0),
                expected_aqi_range=(40, 60),
                confidence="High"
            ),
            TimeWindow(
                start_time=datetime(2024, 1, 1, 14, 0),
                end_time=datetime(2024, 1, 1, 16, 0),
                expected_aqi_range=(50, 70),
                confidence="Medium"
            )
        ],
        reasoning="AQI is in acceptable range"
    )
    
    session.location = location
    session.activity_profile = "Walking"
    session.health_profile = "None"
    session.current_aqi = aqi
    session.recommendation = recommendation
    
    return session


def test_complete_time_window_flow(session_with_recommendation):
    """Test complete flow for time window request"""
    response = handle_follow_up(session_with_recommendation, "When is the best time for my activity?")
    
    # Should include time window information
    assert "10:00 AM" in response or "10:00" in response
    assert "12:00 PM" in response or "12:00" in response
    assert "AQI" in response or "aqi" in response


def test_complete_trend_flow(session_with_recommendation):
    """Test complete flow for trend request"""
    historical_data = {
        "PM2.5": [
            Measurement(
                pollutant="PM2.5",
                value=25.0,
                unit="µg/m³",
                timestamp=datetime(2024, 1, 1, i, 0),
                location=session_with_recommendation.location
            )
            for i in range(24)
        ]
    }
    
    with patch('src.chatbot.backend_integration.fetch_historical_data') as mock_fetch:
        mock_fetch.return_value = historical_data
        
        response = handle_follow_up(session_with_recommendation, "Show me 24-hour trends")
        
        # Should include trend information
        assert "trend" in response.lower() or "hour" in response.lower()
        assert "AQI" in response or "Category" in response


def test_complete_location_change_flow(session_with_recommendation):
    """Test complete flow for location change"""
    new_location = Location(
        name="Portland",
        coordinates=(45.5152, -122.6784),
        country="US",
        providers=["openaq"]
    )
    
    new_aqi = OverallAQI(
        aqi=50,
        category="Good",
        color="#00E400",
        dominant_pollutant="PM2.5",
        individual_results=[],
        timestamp=datetime.now(),
        location=new_location
    )
    
    new_recommendation = RecommendationResponse(
        safety_assessment="Safe",
        recommendation_text="Excellent conditions",
        precautions=[],
        time_windows=[],
        reasoning="AQI is good"
    )
    
    with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve, \
         patch('src.chatbot.backend_integration.fetch_current_aqi') as mock_fetch_aqi, \
         patch('src.chatbot.backend_integration.fetch_historical_data') as mock_fetch_hist, \
         patch('src.chatbot.backend_integration.generate_recommendation') as mock_gen_rec:
        
        mock_resolve.return_value = new_location
        mock_fetch_aqi.return_value = new_aqi
        mock_fetch_hist.return_value = {}
        mock_gen_rec.return_value = new_recommendation
        
        response = handle_follow_up(session_with_recommendation, "Change to Portland")
        
        # Should resolve new location
        mock_resolve.assert_called_once_with("Portland")
        
        # Should fetch new AQI
        mock_fetch_aqi.assert_called_once()
        
        # Should generate new recommendation
        mock_gen_rec.assert_called_once()
        
        # Response should include new recommendation
        assert "AQI" in response or "air quality" in response.lower()


def test_multiple_follow_up_requests(session_with_recommendation):
    """Test handling multiple follow-up requests in sequence"""
    # First request: time windows
    response1 = handle_follow_up(session_with_recommendation, "When should I go out?")
    assert "time" in response1.lower() or "10:00" in response1
    
    # Second request: trends
    with patch('src.chatbot.backend_integration.fetch_historical_data') as mock_fetch:
        mock_fetch.return_value = {"PM2.5": []}
        response2 = handle_follow_up(session_with_recommendation, "Show me trends")
        # Should handle even with no data
        assert "trend" in response2.lower() or "available" in response2.lower()
    
    # Third request: help
    response3 = handle_follow_up(session_with_recommendation, "What else can you do?")
    assert "time windows" in response3.lower()
    assert "trends" in response3.lower()
    assert "location" in response3.lower()
