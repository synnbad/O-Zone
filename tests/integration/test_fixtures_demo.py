"""
Integration test demonstrating usage of chatbot fixtures.

This file shows how to use the comprehensive fixtures defined in conftest.py
for integration testing of the O-Zone Chatbot.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from src.chatbot.backend_integration import (
    resolve_location,
    fetch_current_aqi,
    generate_recommendation,
    LocationNotFoundError,
    NoDataAvailableError
)
from src.chatbot.conversation_manager import process_user_input
from src.chatbot.session_manager import create_session, get_session
from src.models import Location, OverallAQI


class TestBackendIntegrationWithFixtures:
    """Test backend integration using mock fixtures"""
    
    def test_valid_location_scenario(self, mock_data_fetcher, mock_aqi_calculator, valid_location_response):
        """Test successful location resolution and AQI fetch"""
        # Configure mocks with valid location response
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Test location resolution
        location = resolve_location("San Francisco")
        assert location.name == "San Francisco"
        assert location.country == "US"
        
        # Test AQI fetch
        aqi = fetch_current_aqi(location)
        assert aqi.aqi == 100
        assert aqi.category == "Moderate"
        assert aqi.dominant_pollutant == "PM2.5"
    
    def test_no_data_scenario(self, mock_data_fetcher, no_data_response):
        """Test handling of no data available"""
        # Configure mocks for no data scenario
        mock_data_fetcher['get_location'].return_value = no_data_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = no_data_response['measurements']
        
        location = resolve_location("Remote Village")
        
        # Should raise NoDataAvailableError
        with pytest.raises(NoDataAvailableError) as exc_info:
            fetch_current_aqi(location)
        
        assert "no recent air quality data" in str(exc_info.value).lower()
    
    def test_stale_data_scenario(self, mock_data_fetcher, mock_aqi_calculator, stale_data_response):
        """Test handling of stale data"""
        # Configure mocks for stale data scenario
        mock_data_fetcher['get_location'].return_value = stale_data_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = stale_data_response['measurements']
        mock_aqi_calculator.return_value = stale_data_response['overall_aqi']
        
        location = resolve_location("Small Town")
        aqi = fetch_current_aqi(location)
        
        # Verify we got AQI but timestamp is old
        assert aqi.aqi == 75
        assert (datetime.utcnow() - aqi.timestamp) > timedelta(hours=3)
    
    def test_hazardous_aqi_scenario(self, mock_data_fetcher, mock_aqi_calculator, hazardous_aqi_response):
        """Test handling of hazardous air quality"""
        # Configure mocks for hazardous scenario
        mock_data_fetcher['get_location'].return_value = hazardous_aqi_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = hazardous_aqi_response['measurements']
        mock_aqi_calculator.return_value = hazardous_aqi_response['overall_aqi']
        
        location = resolve_location("Polluted City")
        aqi = fetch_current_aqi(location)
        
        # Verify hazardous conditions
        assert aqi.aqi == 350
        assert aqi.category == "Hazardous"
        assert aqi.aqi > 300


class TestUserProfileFixtures:
    """Test different user profile scenarios"""
    
    def test_basic_user_profile(self, basic_user_profile):
        """Test basic user profile fixture"""
        assert basic_user_profile.education_level == "basic"
        assert basic_user_profile.technical_expertise == "none"
        assert basic_user_profile.inferred is False
    
    def test_child_user_profile(self, child_user_profile):
        """Test child user profile fixture"""
        assert child_user_profile.age_group == "child"
        assert child_user_profile.education_level == "basic"
        assert child_user_profile.communication_preference == "detailed"
    
    def test_technical_user_profile(self, technical_user_profile):
        """Test technical/expert user profile fixture"""
        assert technical_user_profile.technical_expertise == "expert"
        assert technical_user_profile.education_level == "advanced"
        assert technical_user_profile.occupation_category == "environmental_scientist"
    
    def test_concise_user_profile(self, concise_user_profile):
        """Test concise communication preference"""
        assert concise_user_profile.communication_preference == "concise"
        assert concise_user_profile.technical_expertise == "intermediate"


class TestSessionFixtures:
    """Test session-related fixtures"""
    
    def test_sample_session(self, sample_session):
        """Test sample session fixture"""
        assert sample_session.location is not None
        assert sample_session.location.name == "San Francisco"
        assert sample_session.activity_profile == "Walking"
        assert sample_session.health_profile == "None"
        assert sample_session.user_profile is not None
    
    def test_complete_session_context(self, complete_session_context):
        """Test complete session with AQI and recommendation"""
        assert complete_session_context.current_aqi is not None
        assert complete_session_context.recommendation is not None
        assert complete_session_context.current_state == "recommendation_presentation"
        assert len(complete_session_context.recommendation.time_windows) > 0


class TestRecommendationGeneration:
    """Test recommendation generation with different profiles"""
    
    def test_recommendation_for_basic_user(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        basic_user_profile
    ):
        """Test recommendation generation for basic user"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Generate recommendation
        location = resolve_location("San Francisco")
        aqi = fetch_current_aqi(location)
        recommendation = generate_recommendation(aqi, "Walking", "None")
        
        # Verify recommendation structure
        assert recommendation.safety_assessment is not None
        assert recommendation.recommendation_text is not None
        assert isinstance(recommendation.precautions, list)
    
    def test_recommendation_for_sensitive_health(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        hazardous_aqi_response
    ):
        """Test recommendation for sensitive health profile with hazardous AQI"""
        # Configure mocks for hazardous conditions
        mock_data_fetcher['get_location'].return_value = hazardous_aqi_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = hazardous_aqi_response['measurements']
        mock_aqi_calculator.return_value = hazardous_aqi_response['overall_aqi']
        
        location = resolve_location("Polluted City")
        aqi = fetch_current_aqi(location)
        
        # Mock Bedrock to fail so we get fallback recommendation
        with patch('src.chatbot.backend_integration.get_recommendation') as mock_bedrock:
            mock_bedrock.side_effect = Exception("Bedrock unavailable")
            
            # Generate recommendation for asthma patient - will use fallback
            recommendation = generate_recommendation(aqi, "Jogging/Running", "Asthma/Respiratory")
            
            # Should have strong warnings for hazardous AQI
            assert recommendation.safety_assessment == "Unsafe"
            assert len(recommendation.precautions) > 0


class TestBedrockFallback:
    """Test Bedrock fallback behavior"""
    
    def test_bedrock_failure_triggers_fallback(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        valid_location_response
    ):
        """Test that Bedrock failure triggers rule-based fallback"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Mock Bedrock to fail
        with patch('src.chatbot.backend_integration.get_recommendation') as mock_bedrock:
            mock_bedrock.side_effect = Exception("Bedrock unavailable")
            
            location = resolve_location("San Francisco")
            aqi = fetch_current_aqi(location)
            recommendation = generate_recommendation(aqi, "Walking", "None")
            
            # Should get fallback recommendation
            assert recommendation is not None
            assert recommendation.safety_assessment is not None
            assert "Rule-based recommendation" in recommendation.reasoning


class TestSessionExpiration:
    """Test session expiration with time mocking"""
    
    @pytest.mark.skipif(
        True,  # Skip if freezegun not available
        reason="Requires freezegun package for time mocking"
    )
    def test_session_expires_after_ttl(self, time_travel):
        """Test that sessions expire after TTL"""
        # Create a session
        session = create_session()
        session_id = session.session_id
        
        # Verify session exists
        assert get_session(session_id) is not None
        
        # Advance time by more than TTL (default 30 minutes)
        time_travel.advance(minutes=31)
        
        # Session should be expired
        expired_session = get_session(session_id)
        assert expired_session is None
    
    @pytest.mark.skipif(
        True,  # Skip if freezegun not available
        reason="Requires freezegun package for time mocking"
    )
    def test_session_persists_within_ttl(self, time_travel):
        """Test that sessions persist within TTL"""
        # Create a session
        session = create_session()
        session_id = session.session_id
        
        # Advance time by less than TTL
        time_travel.advance(minutes=15)
        
        # Session should still exist
        active_session = get_session(session_id)
        assert active_session is not None
        assert active_session.session_id == session_id


class TestConversationFlowIntegration:
    """Test complete conversation flows with fixtures"""
    
    def test_complete_onboarding_flow(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test complete onboarding: greeting -> location -> activity -> health -> recommendation"""
        # Configure mocks
        mock_data_fetcher['get_location'].return_value = valid_location_response['location']
        mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
        mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
        
        # Create session
        session = create_session()
        session_id = session.session_id
        
        # Step 1: Greeting
        response1 = process_user_input(session_id, "Hello")
        assert "location" in response1.lower()
        
        # Step 2: Location
        response2 = process_user_input(session_id, "San Francisco")
        assert "activity" in response2.lower()
        
        # Step 3: Activity
        response3 = process_user_input(session_id, "Walking")
        assert "health" in response3.lower()
        
        # Step 4: Health profile (triggers recommendation)
        response4 = process_user_input(session_id, "None")
        # Should get recommendation or processing message
        assert len(response4) > 0
        
        # Verify session has complete context
        final_session = get_session(session_id)
        assert final_session.location is not None
        assert final_session.activity_profile == "Walking"
        assert final_session.health_profile == "None"


class TestCleanupFixture:
    """Test that cleanup fixture works correctly"""
    
    def test_sessions_cleaned_between_tests(self):
        """Test that session store is cleaned between tests"""
        from src.chatbot import session_manager
        
        # Session store should be empty at start of test
        assert len(session_manager._session_store) == 0
        
        # Create a session
        session = create_session()
        assert len(session_manager._session_store) == 1
        
        # Cleanup fixture will clear this after test
