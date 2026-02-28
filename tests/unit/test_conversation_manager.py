"""
Unit tests for conversation_manager.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.chatbot.conversation_manager import (
    handle_greeting,
    handle_location_collection,
    handle_activity_selection,
    handle_health_profile_selection,
    handle_recommendation_generation,
    handle_recommendation_presentation,
    handle_error_recovery,
    ConversationState
)
from src.chatbot.session_manager import SessionContext, UserProfile, create_session
from src.models import Location, OverallAQI, AQIResult, RecommendationResponse


@pytest.fixture
def mock_session():
    """Create a mock session for testing"""
    session = create_session()
    return session


@pytest.fixture
def mock_location():
    """Create a mock location"""
    return Location(
        name="Seattle",
        coordinates=(47.6062, -122.3321),
        country="US",
        providers=["openaq"]
    )


@pytest.fixture
def mock_aqi(mock_location):
    """Create a mock AQI"""
    return OverallAQI(
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
        location=mock_location
    )


@pytest.fixture
def mock_recommendation():
    """Create a mock recommendation"""
    return RecommendationResponse(
        safety_assessment="Safe",
        recommendation_text="Good conditions for outdoor activities",
        precautions=["Stay hydrated"],
        time_windows=[],
        reasoning="AQI is in acceptable range"
    )


def test_handle_greeting(mock_session):
    """Test greeting handler"""
    with patch('src.chatbot.conversation_manager.update_session') as mock_update:
        response = handle_greeting(mock_session)
        
        # Should update state to location collection
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        assert call_args[0] == mock_session.session_id
        assert call_args[1]["current_state"] == ConversationState.LOCATION_COLLECTION.value
        
        # Should return greeting template
        assert "O-Zone" in response or "air quality" in response.lower()


def test_handle_location_collection_success(mock_session, mock_location):
    """Test location collection with valid location"""
    with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve, \
         patch('src.chatbot.conversation_manager.update_session') as mock_update:
        
        mock_resolve.return_value = mock_location
        
        response = handle_location_collection(mock_session, "Seattle")
        
        # Should resolve location
        mock_resolve.assert_called_once_with("Seattle")
        
        # Should update session with location
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        assert call_args[1]["location"] == mock_location
        assert call_args[1]["current_state"] == ConversationState.ACTIVITY_SELECTION.value
        
        # Should confirm location
        assert "Seattle" in response
        assert "US" in response


def test_handle_location_collection_not_found(mock_session):
    """Test location collection with invalid location"""
    from src.chatbot.backend_integration import LocationNotFoundError
    
    with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
        mock_resolve.side_effect = LocationNotFoundError("Location not found")
        
        response = handle_location_collection(mock_session, "InvalidCity")
        
        # Should return error message
        assert "not found" in response.lower() or "couldn't find" in response.lower()


def test_handle_activity_selection_valid(mock_session):
    """Test activity selection with valid input"""
    with patch('src.chatbot.conversation_manager.update_session') as mock_update:
        response = handle_activity_selection(mock_session, "Walking")
        
        # Should update session with activity
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        assert call_args[1]["activity_profile"] == "Walking"
        assert call_args[1]["current_state"] == ConversationState.HEALTH_PROFILE_SELECTION.value
        
        # Should confirm activity and ask for health profile
        assert "Walking" in response
        assert "health" in response.lower()


def test_handle_activity_selection_invalid(mock_session):
    """Test activity selection with invalid input"""
    response = handle_activity_selection(mock_session, "InvalidActivity")
    
    # Should return error message with options
    assert "didn't recognize" in response.lower() or "choose from" in response.lower()


def test_handle_health_profile_selection_valid(mock_session):
    """Test health profile selection with valid input"""
    with patch('src.chatbot.conversation_manager.update_session') as mock_update:
        response = handle_health_profile_selection(mock_session, "None")
        
        # Should update session with health profile
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        assert call_args[1]["health_profile"] == "None"
        assert call_args[1]["current_state"] == ConversationState.RECOMMENDATION_GENERATION.value
        
        # Should confirm and indicate processing
        assert "thank" in response.lower() or "check" in response.lower()


def test_handle_recommendation_generation_success(mock_session, mock_location, mock_aqi, mock_recommendation):
    """Test recommendation generation with complete context"""
    # Set up session with required context
    mock_session.location = mock_location
    mock_session.activity_profile = "Walking"
    mock_session.health_profile = "None"
    
    with patch('src.chatbot.backend_integration.fetch_current_aqi') as mock_fetch_aqi, \
         patch('src.chatbot.backend_integration.fetch_historical_data') as mock_fetch_hist, \
         patch('src.chatbot.backend_integration.generate_recommendation') as mock_gen_rec, \
         patch('src.chatbot.conversation_manager.update_session') as mock_update, \
         patch('src.chatbot.conversation_manager.handle_recommendation_presentation') as mock_present:
        
        mock_fetch_aqi.return_value = mock_aqi
        mock_fetch_hist.return_value = {}
        mock_gen_rec.return_value = mock_recommendation
        mock_present.return_value = "Recommendation presented"
        
        response = handle_recommendation_generation(mock_session)
        
        # Should fetch AQI
        mock_fetch_aqi.assert_called_once_with(mock_location)
        
        # Should generate recommendation
        mock_gen_rec.assert_called_once()
        
        # Should update session
        assert mock_update.called
        
        # Should call presentation handler
        mock_present.assert_called_once()


def test_handle_recommendation_generation_missing_context(mock_session):
    """Test recommendation generation with missing context"""
    # Session has no location, activity, or health profile
    response = handle_recommendation_generation(mock_session)
    
    # Should return error message
    assert "need more information" in response.lower() or "start over" in response.lower()


def test_handle_recommendation_presentation(mock_session, mock_aqi, mock_recommendation):
    """Test recommendation presentation"""
    # Set up session with recommendation data
    mock_session.current_aqi = mock_aqi
    mock_session.recommendation = mock_recommendation
    
    with patch('src.chatbot.response_generator.format_aqi_explanation') as mock_format_aqi, \
         patch('src.chatbot.response_generator.format_recommendation') as mock_format_rec, \
         patch('src.chatbot.conversation_manager.update_session') as mock_update:
        
        mock_format_aqi.return_value = "AQI: 75 (Moderate)"
        mock_format_rec.return_value = "Safe for outdoor activities"
        
        response = handle_recommendation_presentation(mock_session)
        
        # Should format AQI and recommendation
        mock_format_aqi.assert_called_once()
        mock_format_rec.assert_called_once()
        
        # Should update state to follow-up
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        assert call_args[1]["current_state"] == ConversationState.FOLLOW_UP.value
        
        # Should include formatted data and follow-up options
        assert "AQI" in response or "75" in response
        assert "time windows" in response.lower() or "trends" in response.lower()


def test_handle_error_recovery_location_error(mock_session):
    """Test error recovery with location error"""
    from src.chatbot.backend_integration import LocationNotFoundError
    
    error = LocationNotFoundError("Location not found")
    
    with patch('src.chatbot.response_generator.format_error_message') as mock_format, \
         patch('src.chatbot.conversation_manager.update_session') as mock_update:
        
        mock_format.return_value = "Error: Location not found. Try a different location."
        
        response = handle_error_recovery(mock_session, error)
        
        # Should update state to error recovery
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        assert call_args[1]["current_state"] == ConversationState.ERROR_RECOVERY.value
        
        # Should format error message
        mock_format.assert_called_once()
        call_args = mock_format.call_args[0]
        assert call_args[0] == "LOCATION_ERROR"
        
        # Should return formatted error
        assert "Error" in response or "not found" in response.lower()


def test_handle_error_recovery_general_error(mock_session):
    """Test error recovery with general error"""
    error = Exception("Unexpected error")
    
    with patch('src.chatbot.response_generator.format_error_message') as mock_format, \
         patch('src.chatbot.conversation_manager.update_session') as mock_update:
        
        mock_format.return_value = "Error: Unexpected issue. Try again."
        
        response = handle_error_recovery(mock_session, error)
        
        # Should format as general error
        mock_format.assert_called_once()
        call_args = mock_format.call_args[0]
        assert call_args[0] == "GENERAL_ERROR"


# Tests for enhanced follow-up handler (Task 8.1)

def test_handle_follow_up_time_window_request(mock_session, mock_recommendation):
    """Test follow-up handler with time window request"""
    from src.chatbot.conversation_manager import handle_follow_up
    from src.models import TimeWindow
    
    # Set up session with recommendation containing time windows
    mock_session.recommendation = mock_recommendation
    mock_session.recommendation.time_windows = [
        TimeWindow(
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0),
            expected_aqi_range=(40, 60),
            confidence="High"
        )
    ]
    
    with patch('src.chatbot.response_generator.format_time_windows') as mock_format:
        mock_format.return_value = "Best time: 10:00 AM - 12:00 PM (AQI: 40-60)"
        
        response = handle_follow_up(mock_session, "When is the best time?")
        
        # Should format time windows
        mock_format.assert_called_once()
        assert "time" in response.lower()


def test_handle_follow_up_time_window_no_data(mock_session, mock_recommendation):
    """Test follow-up handler with time window request but no data"""
    from src.chatbot.conversation_manager import handle_follow_up
    
    # Set up session with recommendation but no time windows
    mock_session.recommendation = mock_recommendation
    mock_session.recommendation.time_windows = []
    
    response = handle_follow_up(mock_session, "Show me time windows")
    
    # Should inform user no time windows available
    assert "don't have" in response.lower() or "not available" in response.lower()


def test_handle_follow_up_trend_request_24h(mock_session, mock_location):
    """Test follow-up handler with 24-hour trend request"""
    from src.chatbot.conversation_manager import handle_follow_up
    from src.models import Measurement
    
    # Set up session with location
    mock_session.location = mock_location
    
    historical_data = {
        "PM2.5": [
            Measurement(
                pollutant="PM2.5",
                value=25.0,
                unit="µg/m³",
                timestamp=datetime(2024, 1, 1, 10, 0),
                location=mock_location
            )
        ]
    }
    
    with patch('src.chatbot.backend_integration.fetch_historical_data') as mock_fetch, \
         patch('src.chatbot.response_generator.format_trend_data') as mock_format:
        
        mock_fetch.return_value = historical_data
        mock_format.return_value = "24-hour trends: AQI varied from 50 to 75"
        
        response = handle_follow_up(mock_session, "Show me 24-hour trends")
        
        # Should fetch 24-hour data
        mock_fetch.assert_called_once_with(mock_location, hours=24)
        
        # Should format trend data
        mock_format.assert_called_once()
        assert "trend" in response.lower()


def test_handle_follow_up_trend_request_7day(mock_session, mock_location):
    """Test follow-up handler with 7-day trend request"""
    from src.chatbot.conversation_manager import handle_follow_up
    
    # Set up session with location
    mock_session.location = mock_location
    
    with patch('src.chatbot.backend_integration.fetch_historical_data') as mock_fetch, \
         patch('src.chatbot.response_generator.format_trend_data') as mock_format:
        
        mock_fetch.return_value = {"PM2.5": []}
        mock_format.return_value = "7-day trends: AQI stable"
        
        response = handle_follow_up(mock_session, "Show me 7 day trends")
        
        # Should fetch 7-day data (168 hours)
        mock_fetch.assert_called_once_with(mock_location, hours=168)


def test_handle_follow_up_trend_no_location(mock_session):
    """Test follow-up handler with trend request but no location"""
    from src.chatbot.conversation_manager import handle_follow_up
    
    # Session has no location
    response = handle_follow_up(mock_session, "Show me trends")
    
    # Should inform user location is needed
    assert "need a location" in response.lower() or "provide a location" in response.lower()


def test_handle_follow_up_location_change_with_new_location(mock_session, mock_location):
    """Test follow-up handler with location change including new location"""
    from src.chatbot.conversation_manager import handle_follow_up
    
    # Set up session with existing context
    mock_session.activity_profile = "Walking"
    mock_session.health_profile = "None"
    
    with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve, \
         patch('src.chatbot.conversation_manager.update_session') as mock_update, \
         patch('src.chatbot.conversation_manager.get_session') as mock_get, \
         patch('src.chatbot.conversation_manager.handle_recommendation_generation') as mock_gen:
        
        mock_resolve.return_value = mock_location
        mock_get.return_value = mock_session
        mock_gen.return_value = "New recommendation for Seattle"
        
        response = handle_follow_up(mock_session, "Change to Seattle")
        
        # Should resolve new location
        mock_resolve.assert_called_once_with("Seattle")
        
        # Should update session with new location
        assert mock_update.called
        update_call = mock_update.call_args[0][1]
        assert update_call["location"] == mock_location
        assert update_call["current_aqi"] is None  # Clear old AQI
        assert update_call["recommendation"] is None  # Clear old recommendation
        
        # Should generate new recommendation
        mock_gen.assert_called_once()


def test_handle_follow_up_location_change_prompt(mock_session):
    """Test follow-up handler with location change request without new location"""
    from src.chatbot.conversation_manager import handle_follow_up
    
    with patch('src.chatbot.conversation_manager.update_session') as mock_update:
        response = handle_follow_up(mock_session, "I want to change location")
        
        # Should update state to location collection
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        assert call_args[1]["current_state"] == ConversationState.LOCATION_COLLECTION.value
        
        # Should prompt for new location
        assert "new location" in response.lower() or "what" in response.lower()


def test_handle_follow_up_location_change_invalid(mock_session):
    """Test follow-up handler with invalid location change"""
    from src.chatbot.conversation_manager import handle_follow_up
    from src.chatbot.backend_integration import LocationNotFoundError
    
    # Set up session with existing location
    mock_session.location = Location("Portland", (0, 0), "US", [])
    
    with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
        mock_resolve.side_effect = LocationNotFoundError("Location not found")
        
        response = handle_follow_up(mock_session, "Change to InvalidCity")
        
        # Should keep previous location and return error
        assert mock_session.location.name == "Portland"
        assert "not found" in response.lower() or "couldn't find" in response.lower()


def test_handle_follow_up_goodbye(mock_session):
    """Test follow-up handler with goodbye"""
    from src.chatbot.conversation_manager import handle_follow_up
    
    with patch('src.chatbot.conversation_manager.update_session') as mock_update:
        response = handle_follow_up(mock_session, "Goodbye")
        
        # Should update state to goodbye
        mock_update.assert_called_once()
        call_args = mock_update.call_args[0]
        assert call_args[1]["current_state"] == ConversationState.GOODBYE.value
        
        # Should return farewell message
        assert "thank" in response.lower() or "bye" in response.lower()


def test_handle_follow_up_general_help(mock_session):
    """Test follow-up handler with unrecognized input"""
    from src.chatbot.conversation_manager import handle_follow_up
    
    response = handle_follow_up(mock_session, "What can you do?")
    
    # Should return help message with options
    assert "time windows" in response.lower()
    assert "trends" in response.lower()
    assert "location" in response.lower()
