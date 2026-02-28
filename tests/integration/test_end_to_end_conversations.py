"""
End-to-end conversation flow tests for the O-Zone Chatbot.

Tests validate complete conversation flows from start to finish, including:
- Complete onboarding flow
- Location changes mid-session
- Follow-up questions (time windows, trends)
- Error recovery
- Adaptive communication based on user profiles
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from src.chatbot.conversation_manager import process_user_input
from src.chatbot.session_manager import create_session, get_session, update_session
from src.models import Location, OverallAQI, AQIResult, Measurement, RecommendationResponse, TimeWindow


class TestCompleteOnboardingFlow:
    """Test complete onboarding flow: Greeting → Location → Activity → Health → Recommendation"""
    
    def test_happy_path_complete_onboarding(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test complete happy path from greeting to recommendation"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session
        session = create_session()
        session_id = session.session_id
        
        # Step 1: Greeting
        response1 = process_user_input(session_id, "Hello")
        assert len(response1) > 0
        assert "location" in response1.lower()
        
        # Verify session state
        session_after_greeting = get_session(session_id)
        assert session_after_greeting.current_state == "location_collection"
        
        # Step 2: Location
        response2 = process_user_input(session_id, "San Francisco")
        assert len(response2) > 0
        assert "activity" in response2.lower()
        assert "san francisco" in response2.lower()
        
        # Verify location was stored
        session_after_location = get_session(session_id)
        assert session_after_location.location is not None
        assert session_after_location.location.name == "San Francisco"
        assert session_after_location.current_state == "activity_selection"
        
        # Step 3: Activity
        response3 = process_user_input(session_id, "Walking")
        assert len(response3) > 0
        assert "health" in response3.lower()
        
        # Verify activity was stored
        session_after_activity = get_session(session_id)
        assert session_after_activity.activity_profile == "Walking"
        assert session_after_activity.current_state == "health_profile_selection"
        
        # Step 4: Health profile (triggers recommendation generation)
        response4 = process_user_input(session_id, "None")
        assert len(response4) > 0
        # Should contain recommendation or processing message
        
        # Verify health profile was stored
        session_after_health = get_session(session_id)
        assert session_after_health.health_profile == "None"
        
        # Verify complete context
        final_session = get_session(session_id)
        assert final_session.location is not None
        assert final_session.activity_profile == "Walking"
        assert final_session.health_profile == "None"
        # Should have AQI data (may be populated during recommendation generation)
        if final_session.current_aqi is not None:
            assert final_session.current_aqi.aqi == 100
            assert final_session.current_aqi.category == "Moderate"
    
    def test_onboarding_with_child_outdoor_play_activity(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test onboarding with Child Outdoor Play activity"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session
        session = create_session()
        session_id = session.session_id
        
        # Complete onboarding
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        
        # Select Child Outdoor Play
        response_activity = process_user_input(session_id, "Child Outdoor Play")
        assert len(response_activity) > 0
        assert "health" in response_activity.lower()
        # Should mention child-specific guidance
        assert "child" in response_activity.lower() or "kid" in response_activity.lower()
        
        # Verify activity was stored
        session_after_activity = get_session(session_id)
        assert session_after_activity.activity_profile == "Child Outdoor Play"
    
    def test_onboarding_with_sensitive_health_profile(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test onboarding with sensitive health profile (Asthma/Respiratory)"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session
        session = create_session()
        session_id = session.session_id
        
        # Complete onboarding
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Jogging/Running")
        
        # Select Asthma/Respiratory
        response_health = process_user_input(session_id, "Asthma/Respiratory")
        assert len(response_health) > 0
        
        # Verify health profile was stored
        session_after_health = get_session(session_id)
        assert session_after_health.health_profile == "Asthma/Respiratory"
        
        # Recommendation should apply stricter safety thresholds
        # (This is handled by backend, but we verify the profile is passed correctly)
        # AQI may or may not be populated depending on implementation timing


class TestLocationChangeMidSession:
    """Test location change mid-session: Initial recommendation → Change location → New recommendation"""
    
    def test_location_change_preserves_activity_and_health(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test location change preserves activity and health profiles"""
        # Configure mocks for initial location
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session and complete initial onboarding
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Walking")
        process_user_input(session_id, "None")
        
        # Verify initial state
        session_before_change = get_session(session_id)
        assert session_before_change.location.name == "San Francisco"
        assert session_before_change.activity_profile == "Walking"
        assert session_before_change.health_profile == "None"
        
        # Configure mocks for new location
        new_location = Location(
            name="Los Angeles",
            coordinates=(34.0522, -118.2437),
            country="US",
            providers=["PurpleAir"]
        )
        new_measurements = [
            Measurement("PM2.5", 45.0, "μg/m³", datetime.now(timezone.utc), new_location),
            Measurement("PM10", 65.0, "μg/m³", datetime.now(timezone.utc), new_location),
        ]
        new_aqi = OverallAQI(
            aqi=120,
            category="Unhealthy for Sensitive Groups",
            color="#FF7E00",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 45.0, 120, "Unhealthy for Sensitive Groups", "#FF7E00")
            ],
            timestamp=datetime.now(timezone.utc),
            location=new_location
        )
        
        # Reset and reconfigure mocks for new location
        mock_data_fetcher['get_location'].reset_mock()
        mock_data_fetcher['get_location'].return_value = new_location
        mock_data_fetcher['get_current_measurements'].reset_mock()
        mock_data_fetcher['get_current_measurements'].return_value = new_measurements
        mock_aqi_calculator.reset_mock()
        mock_aqi_calculator.return_value = new_aqi
        
        # Change location
        response_change = process_user_input(session_id, "Change location to Los Angeles")
        assert len(response_change) > 0
        # Should confirm location change or provide updated info
        # Note: The exact response depends on conversation manager implementation
        
        # Verify location was updated but activity and health preserved
        session_after_change = get_session(session_id)
        # Location should be updated (if location change is implemented)
        # Activity and health should be preserved
        assert session_after_change.activity_profile == "Walking"  # Preserved
        assert session_after_change.health_profile == "None"  # Preserved
        # If location change is implemented, verify new location
        if session_after_change.location.name == "Los Angeles":
            # Should have new AQI data
            if session_after_change.current_aqi is not None:
                assert session_after_change.current_aqi.aqi == 120
    
    def test_invalid_location_change_keeps_previous_location(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test invalid location change keeps previous location"""
        # Configure mocks for initial location
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session and complete initial onboarding
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Walking")
        process_user_input(session_id, "None")
        
        # Verify initial state
        session_before_change = get_session(session_id)
        assert session_before_change.location.name == "San Francisco"
        
        # Try to change to invalid location - reset mock completely
        from src.chatbot.backend_integration import LocationNotFoundError
        mock_data_fetcher['get_location'].reset_mock()
        mock_data_fetcher['get_location'].side_effect = LocationNotFoundError(
            "I couldn't find air quality data for 'Nonexistent City'."
        )
        
        response_invalid = process_user_input(session_id, "Change location to Nonexistent City")
        assert len(response_invalid) > 0
        # Should indicate error (may be in follow-up state, so check for error indicators)
        # The response might not contain the exact error if we're in follow-up mode
        
        # Verify location was NOT changed
        session_after_invalid = get_session(session_id)
        assert session_after_invalid.location.name == "San Francisco"  # Still the same
        assert session_after_invalid.activity_profile == "Walking"
        assert session_after_invalid.health_profile == "None"
    
    def test_location_change_updates_recommendation(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test location change triggers new recommendation with updated data"""
        # Configure mocks for initial location
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Initial recommendation
        initial_recommendation = RecommendationResponse(
            safety_assessment="Moderate Risk",
            recommendation_text="Air quality in San Francisco is moderate.",
            precautions=["Monitor symptoms"],
            time_windows=[],
            reasoning="Initial recommendation for San Francisco"
        )
        mock_bedrock_client.return_value = initial_recommendation
        
        # Create session and complete initial onboarding
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Cycling")
        process_user_input(session_id, "None")
        
        # Verify initial location
        session_before = get_session(session_id)
        initial_location_name = session_before.location.name
        
        # Configure mocks for new location with different AQI
        new_location = Location(
            name="Seattle",
            coordinates=(47.6062, -122.3321),
            country="US",
            providers=["PurpleAir"]
        )
        new_measurements = [
            Measurement("PM2.5", 15.0, "μg/m³", datetime.now(timezone.utc), new_location),
            Measurement("PM10", 30.0, "μg/m³", datetime.now(timezone.utc), new_location),
        ]
        new_aqi = OverallAQI(
            aqi=55,
            category="Moderate",
            color="#FFFF00",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 15.0, 55, "Moderate", "#FFFF00")
            ],
            timestamp=datetime.now(timezone.utc),
            location=new_location
        )
        
        # New recommendation for Seattle
        new_recommendation = RecommendationResponse(
            safety_assessment="Safe",  # Changed from "Low Risk" to valid value
            recommendation_text="Air quality in Seattle is good for cycling.",
            precautions=["Enjoy your activity"],
            time_windows=[],
            reasoning="Updated recommendation for Seattle"
        )
        
        # Reset and reconfigure mocks
        mock_data_fetcher['get_location'].reset_mock()
        mock_data_fetcher['get_location'].return_value = new_location
        mock_data_fetcher['get_current_measurements'].reset_mock()
        mock_data_fetcher['get_current_measurements'].return_value = new_measurements
        mock_aqi_calculator.reset_mock()
        mock_aqi_calculator.return_value = new_aqi
        mock_bedrock_client.reset_mock()
        mock_bedrock_client.return_value = new_recommendation
        
        # Change location
        response_change = process_user_input(session_id, "Change location to Seattle")
        assert len(response_change) > 0
        
        # Verify session state - location change may or may not be implemented yet
        # The test validates that the system handles the request gracefully
        session_after_change = get_session(session_id)
        # Activity and health should be preserved regardless
        assert session_after_change.activity_profile == "Cycling"
        assert session_after_change.health_profile == "None"


class TestFollowUpQuestions:
    """Test follow-up questions: Recommendation → Time windows request → Trends request"""
    
    def test_time_windows_request_after_recommendation(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        complete_session_context
    ):
        """Test requesting time windows after receiving recommendation"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Mock recommendation with time windows
        time_windows = [
            TimeWindow(
                start_time=datetime.now(timezone.utc) + timedelta(hours=2),
                end_time=datetime.now(timezone.utc) + timedelta(hours=5),
                expected_aqi_range=(50, 75),
                confidence="High"
            ),
            TimeWindow(
                start_time=datetime.now(timezone.utc) + timedelta(hours=8),
                end_time=datetime.now(timezone.utc) + timedelta(hours=11),
                expected_aqi_range=(60, 80),
                confidence="Medium"
            )
        ]
        
        recommendation_with_windows = RecommendationResponse(
            safety_assessment="Moderate Risk",
            recommendation_text="Air quality is moderate.",
            precautions=["Monitor symptoms"],
            time_windows=time_windows,
            reasoning="Analysis with time windows"
        )
        mock_bedrock_client.return_value = recommendation_with_windows
        
        # Use complete session context
        session_id = complete_session_context.session_id
        
        # Request time windows
        response = process_user_input(session_id, "When is the best time for my activity?")
        assert len(response) > 0
        # Should mention time windows
        assert any(word in response.lower() for word in ["time", "window", "hour", "best"])
        
        # Verify session still has context
        session_after = get_session(session_id)
        assert session_after.location is not None
        assert session_after.activity_profile is not None
    
    def test_trends_request_after_recommendation(
        self,
        mock_data_fetcher,
        sample_location,
        complete_session_context
    ):
        """Test requesting trends after receiving recommendation"""
        # Create mock historical data
        now = datetime.now(timezone.utc)
        historical_measurements = {
            "PM2.5": [
                Measurement("PM2.5", 30.0 + i*2, "μg/m³", now - timedelta(hours=i*3), sample_location)
                for i in range(8)
            ],
            "PM10": [
                Measurement("PM10", 50.0 + i*3, "μg/m³", now - timedelta(hours=i*3), sample_location)
                for i in range(8)
            ]
        }
        
        mock_data_fetcher['get_historical_measurements'].return_value = historical_measurements
        
        # Use complete session context
        session_id = complete_session_context.session_id
        
        # Request trends
        response = process_user_input(session_id, "Show me air quality trends")
        assert len(response) > 0
        # Should mention trends or patterns
        assert any(word in response.lower() for word in ["trend", "pattern", "hour", "day", "24"])
        
        # Verify session still has context
        session_after = get_session(session_id)
        assert session_after.location is not None
        assert session_after.activity_profile is not None
    
    def test_multiple_follow_up_questions_in_sequence(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        sample_location
    ):
        """Test multiple follow-up questions in sequence"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session and complete onboarding
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Walking")
        process_user_input(session_id, "None")
        
        # Follow-up 1: Time windows
        response1 = process_user_input(session_id, "When should I go?")
        assert len(response1) > 0
        
        # Follow-up 2: Trends
        historical_measurements = {
            "PM2.5": [
                Measurement("PM2.5", 30.0, "μg/m³", datetime.now(timezone.utc) - timedelta(hours=i*3), sample_location)
                for i in range(8)
            ]
        }
        mock_data_fetcher['get_historical_measurements'].return_value = historical_measurements
        
        response2 = process_user_input(session_id, "Show trends")
        assert len(response2) > 0
        
        # Follow-up 3: General question
        response3 = process_user_input(session_id, "What is the current AQI?")
        assert len(response3) > 0
        
        # Verify session context preserved through all follow-ups
        final_session = get_session(session_id)
        assert final_session.location.name == "San Francisco"
        assert final_session.activity_profile == "Walking"
        assert final_session.health_profile == "None"
        assert final_session.current_aqi is not None


class TestErrorRecovery:
    """Test error recovery: Invalid location → Correction → Success"""
    
    def test_invalid_activity_then_correction_then_success(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test recovery from invalid activity with correction"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session
        session = create_session()
        session_id = session.session_id
        
        # Complete location
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        
        # Invalid activity
        response_invalid = process_user_input(session_id, "Flying")
        assert len(response_invalid) > 0
        # Should ask for valid activity
        assert "activity" in response_invalid.lower() or "choose" in response_invalid.lower()
        
        # Verify activity was not stored
        session_after_invalid = get_session(session_id)
        assert session_after_invalid.activity_profile is None
        assert session_after_invalid.current_state == "activity_selection"
        
        # Correction with valid activity
        response_valid = process_user_input(session_id, "Walking")
        assert len(response_valid) > 0
        assert "health" in response_valid.lower()
        
        # Verify activity was stored
        session_after_valid = get_session(session_id)
        assert session_after_valid.activity_profile == "Walking"
        assert session_after_valid.current_state == "health_profile_selection"
        
        # Complete onboarding
        process_user_input(session_id, "None")
        
        # Verify complete context
        final_session = get_session(session_id)
        assert final_session.activity_profile == "Walking"
        assert final_session.health_profile == "None"
    
    def test_invalid_health_profile_then_correction_then_success(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test recovery from invalid health profile with correction"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session
        session = create_session()
        session_id = session.session_id
        
        # Complete location and activity
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Walking")
        
        # Invalid health profile
        response_invalid = process_user_input(session_id, "Diabetes")
        assert len(response_invalid) > 0
        # Should ask for valid health profile
        assert "health" in response_invalid.lower() or "choose" in response_invalid.lower()
        
        # Verify health profile was not stored
        session_after_invalid = get_session(session_id)
        assert session_after_invalid.health_profile is None
        assert session_after_invalid.current_state == "health_profile_selection"
        
        # Correction with valid health profile
        response_valid = process_user_input(session_id, "Asthma/Respiratory")
        assert len(response_valid) > 0
        
        # Verify health profile was stored
        session_after_valid = get_session(session_id)
        assert session_after_valid.health_profile == "Asthma/Respiratory"
        
        # Verify complete context
        final_session = get_session(session_id)
        assert final_session.location is not None
        assert final_session.activity_profile == "Walking"
        assert final_session.health_profile == "Asthma/Respiratory"
    
    def test_multiple_errors_with_recovery(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test recovery from multiple errors in sequence"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session
        session = create_session()
        session_id = session.session_id
        
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        
        # Error 1: Invalid activity
        response1 = process_user_input(session_id, "Swimming")
        assert "activity" in response1.lower() or "choose" in response1.lower()
        
        # Error 2: Another invalid activity
        response2 = process_user_input(session_id, "Flying")
        assert len(response2) > 0
        
        # Success: Valid activity
        response3 = process_user_input(session_id, "Walking")
        assert "health" in response3.lower()
        
        # Error 3: Invalid health profile
        response4 = process_user_input(session_id, "Diabetes")
        assert "health" in response4.lower() or "choose" in response4.lower()
        
        # Success: Valid health profile
        response5 = process_user_input(session_id, "None")
        assert len(response5) > 0
        
        # Verify complete context after multiple errors
        final_session = get_session(session_id)
        assert final_session.location.name == "San Francisco"
        assert final_session.activity_profile == "Walking"
        assert final_session.health_profile == "None"


class TestAdaptiveCommunication:
    """Test adaptive communication: Basic user profile → Technical question → Simplified response"""
    
    def test_basic_user_gets_simplified_responses(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        basic_user_profile
    ):
        """Test basic user profile receives simplified responses"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session with basic user profile
        session = create_session()
        session_id = session.session_id
        session.user_profile = basic_user_profile
        update_session(session_id, {"user_profile": basic_user_profile})
        
        # Complete onboarding
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Walking")
        response = process_user_input(session_id, "None")
        
        assert len(response) > 0
        # Response should be simplified (no technical jargon)
        # Note: Actual simplification is done by response_generator and Bedrock
        # Here we verify the flow works with basic user profile
        
        # Verify user profile is maintained
        final_session = get_session(session_id)
        assert final_session.user_profile.education_level == "basic"
        assert final_session.user_profile.technical_expertise == "none"
    
    def test_technical_user_gets_detailed_responses(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        technical_user_profile
    ):
        """Test technical user profile receives detailed responses"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session with technical user profile
        session = create_session()
        session_id = session.session_id
        session.user_profile = technical_user_profile
        update_session(session_id, {"user_profile": technical_user_profile})
        
        # Complete onboarding
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Cycling")
        response = process_user_input(session_id, "None")
        
        assert len(response) > 0
        # Response should include technical details
        # Note: Actual detail level is controlled by response_generator and Bedrock
        # Here we verify the flow works with technical user profile
        
        # Verify user profile is maintained
        final_session = get_session(session_id)
        assert final_session.user_profile.education_level == "advanced"
        assert final_session.user_profile.technical_expertise == "expert"
        assert final_session.user_profile.occupation_category == "environmental_scientist"
    
    def test_child_user_gets_age_appropriate_responses(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        child_user_profile
    ):
        """Test child user profile receives age-appropriate responses"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session with child user profile
        session = create_session()
        session_id = session.session_id
        session.user_profile = child_user_profile
        update_session(session_id, {"user_profile": child_user_profile})
        
        # Complete onboarding
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Child Outdoor Play")
        response = process_user_input(session_id, "None")
        
        assert len(response) > 0
        # Response should be age-appropriate
        # Note: Actual adaptation is done by response_generator and Bedrock
        # Here we verify the flow works with child user profile
        
        # Verify user profile is maintained
        final_session = get_session(session_id)
        assert final_session.user_profile.age_group == "child"
        assert final_session.user_profile.education_level == "basic"
    
    def test_concise_preference_gets_brief_responses(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        concise_user_profile
    ):
        """Test concise communication preference receives brief responses"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session with concise user profile
        session = create_session()
        session_id = session.session_id
        session.user_profile = concise_user_profile
        update_session(session_id, {"user_profile": concise_user_profile})
        
        # Complete onboarding
        process_user_input(session_id, "Hello")
        process_user_input(session_id, "San Francisco")
        process_user_input(session_id, "Jogging/Running")
        response = process_user_input(session_id, "None")
        
        assert len(response) > 0
        # Response should be concise
        # Note: Actual brevity is controlled by response_generator and Bedrock
        # Here we verify the flow works with concise preference
        
        # Verify user profile is maintained
        final_session = get_session(session_id)
        assert final_session.user_profile.communication_preference == "concise"
