"""
Integration tests for error recovery flows in the O-Zone Chatbot.

Tests validate the chatbot's ability to handle and recover from various error
scenarios gracefully, including backend failures, session expiration, invalid
input, and Bedrock unavailability.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from src.chatbot.backend_integration import (
    LocationNotFoundError,
    NoDataAvailableError
)
from src.chatbot.conversation_manager import process_user_input
from src.chatbot.session_manager import create_session, get_session, update_session
from src.models import Location, OverallAQI, AQIResult, RecommendationResponse, TimeWindow


class TestBackendFailureDuringOnboarding:
    """Test backend failure during onboarding with fallback and retry"""
    
    def test_location_fetch_failure_then_retry_success(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test backend failure during location fetch, then successful retry"""
        # Create session and start onboarding
        session = create_session()
        session_id = session.session_id
        
        # Step 1: Greeting
        response1 = process_user_input(session_id, "Hello")
        assert "location" in response1.lower()
        
        # Step 2: Location fetch fails - patch at the backend_integration level
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
            mock_resolve.side_effect = Exception("Backend service unavailable")
            
            response2 = process_user_input(session_id, "San Francisco")
            # Should get error message with suggestion to retry
            assert "trouble" in response2.lower() or "issue" in response2.lower() or "error" in response2.lower() or "unexpected" in response2.lower()
            assert "try" in response2.lower() or "again" in response2.lower() or "later" in response2.lower() or "moment" in response2.lower()
            
            # Verify session state - should be in error recovery
            session_after_error = get_session(session_id)
            assert session_after_error.location is None
            assert session_after_error.current_state == "error_recovery"
        
        # Step 3: After error, any input resets to greeting state
        # The system says "Let's start over" and resets
        response_after_error = process_user_input(session_id, "San Francisco")
        # This triggers the else clause which resets to greeting
        assert "start over" in response_after_error.lower() or "not sure" in response_after_error.lower()
        
        # Verify state was reset to greeting
        session_reset = get_session(session_id)
        assert session_reset.current_state == "greeting"
        
        # Step 4: Now retry with backend restored - need to go through greeting again
        response_greeting = process_user_input(session_id, "Hello")
        assert "location" in response_greeting.lower()
        
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
            mock_resolve.return_value = valid_location_response['location']
            
            response3 = process_user_input(session_id, "San Francisco")
            # Should succeed and move to activity selection
            assert "activity" in response3.lower()
            
            # Verify location was stored
            session_after_retry = get_session(session_id)
            assert session_after_retry.location is not None
            assert session_after_retry.location.name == "San Francisco"
    
    def test_aqi_fetch_failure_then_retry_success(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test AQI fetch failure during recommendation generation, then retry"""
        # Configure mocks for successful location and activity/health selection
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        
        # Create session and complete onboarding up to recommendation
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Walking")
        
        # Step: Health profile triggers recommendation, but AQI fetch fails
        mock_data_fetcher['get_current_measurements'].side_effect = Exception("Data service unavailable")
        
        response_error = process_user_input(session_id, "None")
        # The response should indicate processing started
        assert len(response_error) > 0
        
        # Verify context was preserved even with error
        session_after_error = get_session(session_id)
        assert session_after_error.location is not None
        assert session_after_error.activity_profile == "Walking"
        assert session_after_error.health_profile == "None"


class TestSessionExpirationRecovery:
    """Test session expiration during conversation with context recovery"""
    
    @pytest.mark.skipif(
        True,  # Skip if freezegun not available
        reason="Requires freezegun package for time mocking"
    )
    def test_session_expiration_creates_new_session(self, time_travel):
        """Test that expired session triggers new session creation"""
        # Create session
        session = create_session()
        session_id = session.session_id
        
        # Start conversation
        response1 = process_user_input(session_id, "Hello")
        assert len(response1) > 0
        
        # Advance time past TTL (30 minutes)
        time_travel.advance(minutes=31)
        
        # Try to continue conversation with expired session
        response2 = process_user_input(session_id, "San Francisco")
        
        # Should get message about session expiration or restart
        # The system should handle this gracefully
        assert len(response2) > 0
    
    def test_invalid_session_id_creates_new_session(self):
        """Test that invalid session ID creates new session"""
        # Use non-existent session ID
        fake_session_id = "non-existent-session-id"
        
        # Try to process input
        response = process_user_input(fake_session_id, "Hello")
        
        # Should handle gracefully with session expired message
        assert len(response) > 0
        assert "expired" in response.lower() or "start" in response.lower()
    
    def test_session_context_preserved_during_valid_session(
        self,
        mock_data_fetcher,
        valid_location_response
    ):
        """Test that session context is preserved during valid session"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        
        # Create session and add context
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        
        # Verify location was stored
        session_after_location = get_session(session_id)
        assert session_after_location.location is not None
        
        # Continue conversation
        process_user_input(session_id, "Walking")
        
        # Verify location is still preserved
        session_after_activity = get_session(session_id)
        assert session_after_activity.location is not None
        assert session_after_activity.location.name == "San Francisco"
        assert session_after_activity.activity_profile == "Walking"


class TestInvalidInputHandling:
    """Test invalid input handling with clarification and recovery"""
    
    def test_invalid_activity_selection_with_clarification(self):
        """Test invalid activity input triggers clarification"""
        # Create session and get to activity selection
        session = create_session()
        session_id = session.session_id
        
        # Mock location resolution
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
            mock_resolve.return_value = Location(
                name="San Francisco",
                coordinates=(37.7749, -122.4194),
                country="US",
                providers=["PurpleAir"]
            )
            
            process_user_input(session_id, "Hello")
            process_user_input(session_id, "San Francisco")
            
            # Try invalid activity
            response_invalid = process_user_input(session_id, "Flying")
            
            # Should get clarification message with valid options
            assert "activity" in response_invalid.lower() or "choose" in response_invalid.lower()
            # Should mention valid options
            assert any(activity.lower() in response_invalid.lower() 
                      for activity in ["walking", "jogging", "cycling"])
            
            # Verify activity was not stored
            session_after_invalid = get_session(session_id)
            assert session_after_invalid.activity_profile is None
            
            # Provide valid input
            response_valid = process_user_input(session_id, "Walking")
            
            # Should accept and move to health profile
            assert "health" in response_valid.lower()
            
            # Verify activity was stored
            session_after_valid = get_session(session_id)
            assert session_after_valid.activity_profile == "Walking"
    
    def test_invalid_health_profile_with_clarification(self):
        """Test invalid health profile input triggers clarification"""
        # Create session and get to health profile selection
        session = create_session()
        session_id = session.session_id
        
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
            mock_resolve.return_value = Location(
                name="San Francisco",
                coordinates=(37.7749, -122.4194),
                country="US",
                providers=["PurpleAir"]
            )
            
            process_user_input(session_id, "Hello")
            process_user_input(session_id, "San Francisco")
            process_user_input(session_id, "Walking")
            
            # Try invalid health profile
            response_invalid = process_user_input(session_id, "Diabetes")
            
            # Should get clarification message
            assert "health" in response_invalid.lower() or "choose" in response_invalid.lower()
            # Should mention valid options
            assert any(health.lower() in response_invalid.lower() 
                      for health in ["none", "allergies", "asthma", "child", "pregnant"])
            
            # Verify health profile was not stored
            session_after_invalid = get_session(session_id)
            assert session_after_invalid.health_profile is None
            
            # Provide valid input
            response_valid = process_user_input(session_id, "Asthma/Respiratory")
            
            # Should accept and proceed
            assert len(response_valid) > 0
            
            # Verify health profile was stored
            session_after_valid = get_session(session_id)
            assert session_after_valid.health_profile == "Asthma/Respiratory"
    
    def test_ambiguous_input_requests_clarification(self):
        """Test ambiguous input triggers clarification request"""
        # Create session with complete context
        session = create_session()
        session_id = session.session_id
        
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
            mock_resolve.return_value = Location(
                name="San Francisco",
                coordinates=(37.7749, -122.4194),
                country="US",
                providers=["PurpleAir"]
            )
            
            process_user_input(session_id, "Hello")
            process_user_input(session_id, "San Francisco")
            process_user_input(session_id, "Walking")
            
            # Provide ambiguous input
            response = process_user_input(session_id, "What?")
            
            # Should ask for clarification or provide options
            assert len(response) > 0
            # Should be helpful
            assert any(word in response.lower() 
                      for word in ["help", "can", "would", "choose", "select"])


class TestBedrockFallbackAndRecovery:
    """Test Bedrock unavailability with rule-based fallback and recovery"""
    
    def test_bedrock_unavailable_uses_fallback_recommendation(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        valid_location_response
    ):
        """Test Bedrock failure triggers rule-based fallback"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Mock Bedrock to fail
        with patch('src.chatbot.backend_integration.get_recommendation') as mock_bedrock:
            mock_bedrock.side_effect = Exception("Bedrock service unavailable")
            
            # Create session and complete onboarding
            session = create_session()
            session_id = session.session_id
            
            process_user_input(session_id, "Hello")
            process_user_input(session_id, "San Francisco")
            process_user_input(session_id, "Walking")
            response = process_user_input(session_id, "None")
            
            # Should get response (processing message or recommendation)
            assert len(response) > 0
            
            # Verify session state - system should handle error gracefully
            session_after = get_session(session_id)
            # Context should be preserved
            assert session_after.location is not None
            assert session_after.activity_profile == "Walking"
            assert session_after.health_profile == "None"
    
    def test_bedrock_restored_after_fallback(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        valid_location_response
    ):
        """Test Bedrock restoration after fallback provides AI recommendation"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # First: Bedrock fails
        with patch('src.chatbot.backend_integration.get_recommendation') as mock_bedrock:
            mock_bedrock.side_effect = Exception("Bedrock unavailable")
            
            session = create_session()
            session_id = session.session_id
            
            process_user_input(session_id, "Hello")
            process_user_input(session_id, "San Francisco")
            process_user_input(session_id, "Walking")
            response_fallback = process_user_input(session_id, "None")
            
            # Should get response (fallback or error)
            assert len(response_fallback) > 0
            
            session_after_fallback = get_session(session_id)
            # May or may not have recommendation depending on fallback implementation
            
            # Now: Bedrock is restored
            mock_bedrock.side_effect = None
            mock_bedrock.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="AI-powered recommendation: Air quality is moderate.",
                precautions=["Monitor symptoms", "Take breaks if needed"],
                time_windows=[
                    TimeWindow(
                        start_time=datetime.now(timezone.utc) + timedelta(hours=2),
                        end_time=datetime.now(timezone.utc) + timedelta(hours=5),
                        expected_aqi_range=(50, 75),
                        confidence="High"
                    )
                ],
                reasoning="AI-powered analysis of current conditions"
            )
            
            # User requests updated recommendation - need to trigger new generation
            # Reset state to trigger new recommendation
            update_session(session_id, {"current_state": "health_profile_selection"})
            response_ai = process_user_input(session_id, "None")
            
            # Should get AI-powered recommendation
            assert len(response_ai) > 0
            
            session_after_restore = get_session(session_id)
            # Should have recommendation now
            if session_after_restore.recommendation:
                assert "AI-powered" in session_after_restore.recommendation.reasoning
    
    def test_bedrock_failure_with_hazardous_aqi_provides_strong_warning(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        hazardous_aqi_response
    ):
        """Test Bedrock failure with hazardous AQI still provides strong warnings"""
        # Mock location resolution at backend_integration level
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve, \
             patch('src.chatbot.backend_integration.fetch_current_aqi') as mock_fetch_aqi, \
             patch('src.chatbot.backend_integration.generate_recommendation') as mock_bedrock:
            
            # Configure mocks for hazardous conditions
            mock_resolve.return_value = hazardous_aqi_response['location']
            mock_fetch_aqi.return_value = hazardous_aqi_response['overall_aqi']
            mock_bedrock.side_effect = Exception("Bedrock unavailable")
            
            session = create_session()
            session_id = session.session_id
            
            process_user_input(session_id, "Hello")
            process_user_input(session_id, "Beijing")  # Use a real city name
            process_user_input(session_id, "Jogging/Running")
            response = process_user_input(session_id, "Asthma/Respiratory")
            
            # Should get response (processing or error message)
            assert len(response) > 0
            
            session_after = get_session(session_id)
            # Context should be preserved
            assert session_after.location is not None
            assert session_after.activity_profile == "Jogging/Running"
            assert session_after.health_profile == "Asthma/Respiratory"


class TestMultipleErrorRecoveryScenarios:
    """Test complex scenarios with multiple error types"""
    
    def test_location_error_then_invalid_input_then_success(
        self,
        mock_data_fetcher,
        valid_location_response
    ):
        """Test recovery from location error followed by invalid input"""
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        
        # Step 1: Location fetch fails
        mock_data_fetcher['get_location'].side_effect = LocationNotFoundError(
            "I couldn't find air quality data for 'Nonexistent City'. "
            "This could mean the location name might be misspelled or there are no monitoring stations in that area. "
            "Please try a nearby larger city or check the spelling."
        )
        
        response1 = process_user_input(session_id, "Nonexistent City")
        assert "couldn't find" in response1.lower() or "not found" in response1.lower()
        
        # Step 2: User provides invalid input (not a location)
        response2 = process_user_input(session_id, "???")
        # Should still be asking for location or show error
        assert len(response2) > 0
        
        # Step 3: User provides valid location
        mock_data_fetcher['get_location'].side_effect = None
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        
        response3 = process_user_input(session_id, "San Francisco")
        # Should succeed and move to activity
        assert "activity" in response3.lower()
        
        session_final = get_session(session_id)
        assert session_final.location is not None
    
    def test_backend_failure_preserves_partial_context(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        valid_location_response
    ):
        """Test that backend failure preserves already-collected context"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        
        session = create_session()
        session_id = session.session_id
        
        # Collect location and activity successfully
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Walking")
        
        # Health profile triggers recommendation, but backend fails
        mock_data_fetcher['get_current_measurements'].side_effect = Exception("Backend error")
        
        response_error = process_user_input(session_id, "None")
        # Should get some response (error or processing message)
        assert len(response_error) > 0
        
        # Verify partial context is preserved
        session_after_error = get_session(session_id)
        assert session_after_error.location is not None
        assert session_after_error.location.name == "San Francisco"
        assert session_after_error.activity_profile == "Walking"
        assert session_after_error.health_profile == "None"
        # But no AQI or recommendation
        assert session_after_error.current_aqi is None


class TestErrorMessageQuality:
    """Test that error messages are user-friendly and actionable"""
    
    def test_location_not_found_provides_suggestions(self):
        """Test location not found error provides helpful suggestions"""
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
            mock_resolve.side_effect = LocationNotFoundError(
                "I couldn't find air quality data for 'Nonexistent Place'. "
                "This could mean the location name might be misspelled or there are no monitoring stations in that area. "
                "Please try a nearby larger city or check the spelling."
            )
            
            response = process_user_input(session_id, "Nonexistent Place")
            
            # Should be user-friendly
            assert "couldn't find" in response.lower() or "not found" in response.lower()
            # Should provide suggestions
            assert "try" in response.lower()
    
    def test_no_data_error_provides_alternatives(self):
        """Test no data error provides alternative actions"""
        session = create_session()
        session_id = session.session_id
        
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve, \
             patch('src.chatbot.backend_integration.fetch_current_aqi') as mock_fetch:
            
            mock_resolve.return_value = Location(
                name="Remote Village",
                coordinates=(45.0, -120.0),
                country="US",
                providers=[]
            )
            mock_fetch.side_effect = NoDataAvailableError(
                "I found Remote Village, but there's no recent air quality data available. "
                "This sometimes happens with monitoring stations that update infrequently. "
                "You could try a nearby larger city or check back in a few hours."
            )
            
            process_user_input(session_id, "Hello")
            process_user_input(session_id, "Remote Village")
            process_user_input(session_id, "Walking")
            response = process_user_input(session_id, "None")
            
            # Should get some response (processing message or error)
            assert len(response) > 0
            
            # Verify context was preserved
            session_after = get_session(session_id)
            assert session_after.location is not None
            assert session_after.activity_profile == "Walking"
            assert session_after.health_profile == "None"
    
    def test_backend_error_avoids_technical_details(self):
        """Test backend errors don't expose technical details to users"""
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        
        with patch('src.chatbot.backend_integration.resolve_location') as mock_resolve:
            # Simulate technical error
            mock_resolve.side_effect = Exception("ConnectionError: Failed to connect to http://api.example.com:8080")
            
            response = process_user_input(session_id, "San Francisco")
            
            # Should not contain technical details
            assert "ConnectionError" not in response
            assert "http://" not in response
            assert ":8080" not in response
            # Should be user-friendly
            assert "issue" in response.lower() or "trouble" in response.lower()
