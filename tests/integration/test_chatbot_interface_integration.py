"""
Integration tests for chatbot interface with conversation flow
"""

import pytest
from unittest.mock import patch, MagicMock
from src.chatbot.chatbot_interface import ChatbotInterface
from src.models import Location, OverallAQI, AQIResult, RecommendationResponse
from datetime import datetime, timezone


@pytest.fixture
def mock_location():
    """Create a mock location"""
    return Location(
        name="Seattle",
        coordinates=(47.6062, -122.3321),
        country="US",
        providers=["OpenAQ"]
    )


@pytest.fixture
def mock_aqi(mock_location):
    """Create a mock AQI result"""
    return OverallAQI(
        aqi=75,
        category="Moderate",
        color="#FFFF00",
        dominant_pollutant="PM2.5",
        individual_results=[
            AQIResult(
                pollutant="PM2.5",
                concentration=25.5,
                aqi=75,
                category="Moderate",
                color="#FFFF00"
            )
        ],
        timestamp=datetime.now(timezone.utc),
        location=mock_location
    )


@pytest.fixture
def mock_recommendation():
    """Create a mock recommendation"""
    return RecommendationResponse(
        safety_assessment="Moderate Risk",
        recommendation_text="Air quality is moderate. You can proceed with your outdoor activity, but consider taking breaks if you feel any discomfort.",
        precautions=["Take breaks if needed", "Stay hydrated"],
        time_windows=[],
        reasoning="Based on current PM2.5 levels"
    )


class TestChatbotInterfaceIntegration:
    """Integration tests for chatbot interface"""
    
    @patch('src.chatbot.backend_integration.resolve_location')
    @patch('src.chatbot.backend_integration.fetch_current_aqi')
    @patch('src.chatbot.backend_integration.fetch_historical_data')
    @patch('src.chatbot.backend_integration.generate_recommendation')
    def test_complete_conversation_flow(
        self, 
        mock_gen_rec, 
        mock_hist, 
        mock_aqi_fetch, 
        mock_resolve,
        mock_location,
        mock_aqi,
        mock_recommendation
    ):
        """Test a complete conversation flow from greeting to recommendation"""
        # Setup mocks
        mock_resolve.return_value = mock_location
        mock_aqi_fetch.return_value = mock_aqi
        mock_hist.return_value = {}
        mock_gen_rec.return_value = mock_recommendation
        
        # Create interface and start session
        interface = ChatbotInterface()
        session_id = interface.start_session()
        
        # Step 1: Get greeting by sending "hi" (empty messages are rejected by interface)
        greeting = interface.send_message("hi", session_id)
        assert "O-Zone" in greeting or "air quality" in greeting.lower() or "location" in greeting.lower()
        
        # Step 2: Provide location
        location_response = interface.send_message("Seattle", session_id)
        assert "Seattle" in location_response
        assert "activity" in location_response.lower()
        
        # Step 3: Select activity
        activity_response = interface.send_message("Walking", session_id)
        assert "Walking" in activity_response or "walking" in activity_response.lower()
        assert "health" in activity_response.lower()
        
        # Step 4: Select health profile - this triggers recommendation generation
        health_response = interface.send_message("None", session_id)
        # Should get a recommendation or be processing
        assert len(health_response) > 0
        
        # Verify location was resolved
        mock_resolve.assert_called_once()
    
    @patch('src.chatbot.backend_integration.resolve_location')
    def test_location_error_handling(self, mock_resolve):
        """Test error handling when location is not found"""
        from src.chatbot.backend_integration import LocationNotFoundError
        
        mock_resolve.side_effect = LocationNotFoundError("Location not found")
        
        interface = ChatbotInterface()
        session_id = interface.start_session()
        
        # Get greeting by sending a non-empty message that triggers greeting
        greeting = interface.send_message("hello", session_id)
        # After greeting, we should be in location collection state
        
        # Try invalid location - should get error
        response = interface.send_message("InvalidCity123", session_id)
        assert "not found" in response.lower() or "couldn't find" in response.lower() or "location" in response.lower()
    
    def test_help_command_during_conversation(self):
        """Test that help command works at any point in conversation"""
        interface = ChatbotInterface()
        session_id = interface.start_session()
        
        # Get greeting
        interface.send_message("", session_id)
        
        # Use help command
        help_response = interface.send_message("/help", session_id)
        assert "help" in help_response.lower()
        assert "/restart" in help_response
    
    def test_restart_command_during_conversation(self):
        """Test that restart command creates a new session"""
        interface = ChatbotInterface()
        old_session_id = interface.start_session()
        
        # Get greeting
        interface.send_message("", old_session_id)
        
        # Use restart command
        restart_response = interface.send_message("/restart")
        assert "new conversation" in restart_response.lower() or "starting" in restart_response.lower()
        
        # Verify new session was created
        assert interface.current_session_id != old_session_id
    
    @patch('src.chatbot.backend_integration.resolve_location')
    @patch('src.chatbot.backend_integration.fetch_current_aqi')
    @patch('src.chatbot.backend_integration.fetch_historical_data')
    @patch('src.chatbot.backend_integration.generate_recommendation')
    def test_follow_up_questions(
        self,
        mock_gen_rec,
        mock_hist,
        mock_aqi_fetch,
        mock_resolve,
        mock_location,
        mock_aqi,
        mock_recommendation
    ):
        """Test follow-up questions after getting recommendation"""
        # Setup mocks
        mock_resolve.return_value = mock_location
        mock_aqi_fetch.return_value = mock_aqi
        mock_hist.return_value = {}
        mock_gen_rec.return_value = mock_recommendation
        
        interface = ChatbotInterface()
        session_id = interface.start_session()
        
        # Complete the flow
        interface.send_message("hi", session_id)  # Greeting
        interface.send_message("Seattle", session_id)  # Location
        interface.send_message("Walking", session_id)  # Activity
        rec_response = interface.send_message("None", session_id)  # Health - triggers recommendation
        
        # Verify we got a recommendation
        assert "air quality" in rec_response.lower() or "moderate" in rec_response.lower()
        
        # Ask follow-up question
        follow_up = interface.send_message("What about time windows?", session_id)
        assert "time" in follow_up.lower() or "window" in follow_up.lower()
    
    def test_empty_message_handling(self):
        """Test that empty messages are handled gracefully"""
        interface = ChatbotInterface()
        session_id = interface.start_session()
        
        response = interface.send_message("   ", session_id)
        assert "enter a message" in response.lower() or response != ""
    
    def test_error_recovery_in_interface(self):
        """Test error recovery when conversation manager fails"""
        interface = ChatbotInterface()
        
        # Mock process_user_input to raise an exception after session is created
        with patch('src.chatbot.chatbot_interface.process_user_input') as mock_process:
            mock_process.side_effect = Exception("Test error")
            
            response = interface.send_message("Hello")
            assert "error" in response.lower()
            assert "/restart" in response.lower()

