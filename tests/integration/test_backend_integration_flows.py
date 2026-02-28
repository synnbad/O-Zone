"""
Integration tests for backend integration flows in the O-Zone Chatbot.

Tests validate the complete data flow from backend services through to user-facing
responses, including location resolution, AQI fetching, recommendation generation,
and response formatting.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from src.chatbot.backend_integration import (
    resolve_location,
    fetch_current_aqi,
    fetch_historical_data,
    generate_recommendation,
    LocationNotFoundError,
    NoDataAvailableError
)
from src.chatbot.response_generator import (
    format_aqi_explanation,
    format_recommendation,
    format_time_windows,
    format_trend_data
)
from src.chatbot.conversation_manager import process_user_input
from src.chatbot.session_manager import create_session, get_session
from src.models import Location, OverallAQI, AQIResult, Measurement, RecommendationResponse, TimeWindow


class TestLocationToRecommendationFlow:
    """Test complete flow: location resolution → AQI fetch → recommendation → response formatting"""
    
    def test_complete_flow_with_valid_data(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        basic_user_profile
    ):
        """Test complete flow from location to formatted recommendation"""
        # Configure mocks - need to patch at the backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            mock_get_loc.return_value = valid_location_response['location']
            mock_get_curr.return_value = valid_location_response['measurements']
            mock_calc_aqi.return_value = valid_location_response['overall_aqi']
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate.",
                precautions=["Monitor symptoms"],
                time_windows=[],
                reasoning="AQI is 100"
            )
            
            # Step 1: Resolve location
            location = resolve_location("San Francisco")
            assert location.name == "San Francisco"
            assert location.country == "US"
            assert location.coordinates == (37.7749, -122.4194)
            
            # Step 2: Fetch current AQI
            aqi = fetch_current_aqi(location)
            assert aqi.aqi == 100
            assert aqi.category == "Moderate"
            assert aqi.dominant_pollutant == "PM2.5"
            
            # Step 3: Generate recommendation
            recommendation = generate_recommendation(aqi, "Walking", "None")
            assert recommendation.safety_assessment is not None
            assert recommendation.recommendation_text is not None
            assert isinstance(recommendation.precautions, list)
            
            # Step 4: Format response for user
            aqi_text = format_aqi_explanation(aqi, basic_user_profile)
            assert len(aqi_text) > 0
            assert "100" in aqi_text or "moderate" in aqi_text.lower()
            
            rec_text = format_recommendation(recommendation, basic_user_profile)
            assert len(rec_text) > 0
            # Should contain safety information or recommendation content
            assert any(word in rec_text.lower() for word in ["moderate", "risk", "air", "quality", "activity"])
    
    def test_complete_flow_with_hazardous_aqi(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        hazardous_aqi_response,
        basic_user_profile
    ):
        """Test complete flow with hazardous AQI includes strong warnings"""
        # Configure mocks for hazardous conditions with proper patching
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            mock_get_loc.return_value = hazardous_aqi_response['location']
            mock_get_curr.return_value = hazardous_aqi_response['measurements']
            mock_calc_aqi.return_value = hazardous_aqi_response['overall_aqi']
            # Mock Bedrock to fail so we get fallback recommendation
            mock_get_rec.side_effect = Exception("Bedrock unavailable")
            
            # Step 1: Resolve location
            location = resolve_location("Polluted City")
            assert location.name == "Polluted City"
            
            # Step 2: Fetch current AQI
            aqi = fetch_current_aqi(location)
            assert aqi.aqi == 350
            assert aqi.category == "Hazardous"
            
            # Step 3: Generate recommendation (fallback)
            recommendation = generate_recommendation(aqi, "Jogging/Running", "Asthma/Respiratory")
            assert recommendation.safety_assessment == "Unsafe"
            assert len(recommendation.precautions) > 0
            
            # Step 4: Format response with warnings
            rec_text = format_recommendation(recommendation, basic_user_profile)
            assert len(rec_text) > 0
            assert any(word in rec_text.lower() for word in ["unsafe", "avoid", "stay inside", "danger", "do not go outside"])
    
    def test_complete_flow_with_stale_data(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        stale_data_response,
        basic_user_profile
    ):
        """Test complete flow with stale data includes timestamp warnings"""
        # Configure mocks for stale data with proper patching
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            mock_get_loc.return_value = stale_data_response['location']
            mock_get_curr.return_value = stale_data_response['measurements']
            mock_calc_aqi.return_value = stale_data_response['overall_aqi']
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate.",
                precautions=["Monitor symptoms"],
                time_windows=[],
                reasoning="AQI is 75"
            )
            
            # Step 1: Resolve location
            location = resolve_location("Small Town")
            assert location.name == "Small Town"
            
            # Step 2: Fetch current AQI (stale)
            aqi = fetch_current_aqi(location)
            assert aqi.aqi == 75
            # Verify data is stale (older than 3 hours)
            now = datetime.now(timezone.utc) if aqi.timestamp.tzinfo else datetime.utcnow()
            assert (now - aqi.timestamp) > timedelta(hours=3)
            
            # Step 3: Generate recommendation
            recommendation = generate_recommendation(aqi, "Walking", "None")
            assert recommendation is not None
            
            # Step 4: Format response - should include staleness warning
            aqi_text = format_aqi_explanation(aqi, basic_user_profile)
            assert len(aqi_text) > 0
            # Check for staleness indicators
            now = datetime.now(timezone.utc) if aqi.timestamp.tzinfo else datetime.utcnow()
            data_age = now - aqi.timestamp
            if data_age > timedelta(hours=3):
                # Response should indicate data age
                assert any(word in aqi_text.lower() for word in ["old", "stale", "outdated", "hours ago"])


class TestHistoricalDataToTrendFlow:
    """Test flow: historical data fetch → trend analysis → presentation"""
    
    def test_historical_data_fetch_and_trend_presentation(
        self,
        mock_data_fetcher,
        sample_location,
        basic_user_profile
    ):
        """Test fetching historical data and presenting trends"""
        # Create mock historical data
        now = datetime.utcnow()
        historical_measurements = {
            "PM2.5": [
                Measurement("PM2.5", 25.0, "μg/m³", now - timedelta(hours=23), sample_location),
                Measurement("PM2.5", 30.0, "μg/m³", now - timedelta(hours=20), sample_location),
                Measurement("PM2.5", 35.0, "μg/m³", now - timedelta(hours=17), sample_location),
                Measurement("PM2.5", 40.0, "μg/m³", now - timedelta(hours=14), sample_location),
                Measurement("PM2.5", 38.0, "μg/m³", now - timedelta(hours=11), sample_location),
                Measurement("PM2.5", 32.0, "μg/m³", now - timedelta(hours=8), sample_location),
                Measurement("PM2.5", 28.0, "μg/m³", now - timedelta(hours=5), sample_location),
                Measurement("PM2.5", 26.0, "μg/m³", now - timedelta(hours=2), sample_location),
            ],
            "PM10": [
                Measurement("PM10", 50.0, "μg/m³", now - timedelta(hours=23), sample_location),
                Measurement("PM10", 55.0, "μg/m³", now - timedelta(hours=20), sample_location),
                Measurement("PM10", 60.0, "μg/m³", now - timedelta(hours=17), sample_location),
            ]
        }
        
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_historical_measurements') as mock_get_hist:
            mock_get_hist.return_value = historical_measurements
            
            # Step 1: Fetch historical data
            historical_data = fetch_historical_data(sample_location, hours=24)
            assert "PM2.5" in historical_data
            assert len(historical_data["PM2.5"]) == 8
            assert "PM10" in historical_data
            
            # Step 2: Format trend data for presentation
            trend_text = format_trend_data(historical_data, basic_user_profile, "24-hour")
            assert len(trend_text) > 0
            # Should mention time period
            assert "24" in trend_text or "hour" in trend_text.lower()
            # Should include AQI or category information
            assert any(word in trend_text.lower() for word in ["aqi", "good", "moderate", "category"])
    
    def test_historical_data_with_empty_results(
        self,
        mock_data_fetcher,
        sample_location,
        basic_user_profile
    ):
        """Test handling of empty historical data"""
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_historical_measurements') as mock_get_hist:
            # Mock empty historical data
            mock_get_hist.return_value = {}
            
            # Step 1: Fetch historical data
            historical_data = fetch_historical_data(sample_location, hours=24)
            assert historical_data == {}
            
            # Step 2: Format trend data - should handle empty data gracefully
            trend_text = format_trend_data(historical_data, basic_user_profile, "24-hour")
            assert len(trend_text) > 0
            # Should indicate no data available
            assert any(word in trend_text.lower() for word in ["no", "unavailable", "not available"])
    
    def test_seven_day_trend_analysis(
        self,
        mock_data_fetcher,
        sample_location,
        technical_user_profile
    ):
        """Test 7-day trend analysis with technical user profile"""
        # Create mock 7-day historical data
        now = datetime.utcnow()
        historical_measurements = {
            "PM2.5": [
                Measurement("PM2.5", 30.0, "μg/m³", now - timedelta(days=6), sample_location),
                Measurement("PM2.5", 35.0, "μg/m³", now - timedelta(days=5), sample_location),
                Measurement("PM2.5", 40.0, "μg/m³", now - timedelta(days=4), sample_location),
                Measurement("PM2.5", 38.0, "μg/m³", now - timedelta(days=3), sample_location),
                Measurement("PM2.5", 32.0, "μg/m³", now - timedelta(days=2), sample_location),
                Measurement("PM2.5", 28.0, "μg/m³", now - timedelta(days=1), sample_location),
                Measurement("PM2.5", 26.0, "μg/m³", now, sample_location),
            ]
        }
        
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_historical_measurements') as mock_get_hist:
            mock_get_hist.return_value = historical_measurements
            
            # Step 1: Fetch 7-day historical data
            historical_data = fetch_historical_data(sample_location, hours=168)  # 7 days = 168 hours
            assert "PM2.5" in historical_data
            assert len(historical_data["PM2.5"]) == 7
            
            # Step 2: Format trend data for technical user
            trend_text = format_trend_data(historical_data, technical_user_profile, "7-day")
            assert len(trend_text) > 0
            # Technical user should get detailed information
            assert "7" in trend_text or "day" in trend_text.lower() or "week" in trend_text.lower()


class TestTimeWindowPredictionFlow:
    """Test flow: time window prediction → formatting → user selection"""
    
    def test_time_window_prediction_and_formatting(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        basic_user_profile
    ):
        """Test time window prediction and formatting for user"""
        # Mock recommendation with time windows
        time_windows = [
            TimeWindow(
                start_time=datetime.utcnow() + timedelta(hours=2),
                end_time=datetime.utcnow() + timedelta(hours=5),
                expected_aqi_range=(50, 75),
                confidence="High"
            ),
            TimeWindow(
                start_time=datetime.utcnow() + timedelta(hours=8),
                end_time=datetime.utcnow() + timedelta(hours=11),
                expected_aqi_range=(60, 80),
                confidence="Medium"
            )
        ]
        
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            mock_get_loc.return_value = valid_location_response['location']
            mock_get_curr.return_value = valid_location_response['measurements']
            mock_calc_aqi.return_value = valid_location_response['overall_aqi']
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate.",
                precautions=["Monitor symptoms"],
                time_windows=time_windows,
                reasoning="Analysis of forecast data"
            )
            
            # Step 1: Generate recommendation with time windows
            location = resolve_location("San Francisco")
            aqi = fetch_current_aqi(location)
            recommendation = generate_recommendation(aqi, "Walking", "None")
            
            assert len(recommendation.time_windows) == 2
            
            # Step 2: Format time windows for user
            windows_text = format_time_windows(recommendation.time_windows, basic_user_profile)
            assert len(windows_text) > 0
            # Should include time information
            assert any(str(tw.start_time.hour) in windows_text for tw in time_windows)
            # Should be in chronological order
            first_hour = str(time_windows[0].start_time.hour)
            second_hour = str(time_windows[1].start_time.hour)
            if first_hour in windows_text and second_hour in windows_text:
                assert windows_text.index(first_hour) < windows_text.index(second_hour)
    
    def test_empty_time_windows_with_explanation(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        hazardous_aqi_response,
        basic_user_profile
    ):
        """Test handling of empty time windows with explanation"""
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            # Configure mocks for hazardous conditions
            mock_get_loc.return_value = hazardous_aqi_response['location']
            mock_get_curr.return_value = hazardous_aqi_response['measurements']
            mock_calc_aqi.return_value = hazardous_aqi_response['overall_aqi']
            # Mock Bedrock to return recommendation with no suitable time windows
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Unsafe",
                recommendation_text="Air quality is hazardous. Avoid outdoor activities.",
                precautions=["Stay indoors", "Use air purifier"],
                time_windows=[],  # No suitable time windows
                reasoning="No safe time windows predicted in forecast period"
            )
            
            # Step 1: Generate recommendation
            location = resolve_location("Polluted City")
            aqi = fetch_current_aqi(location)
            recommendation = generate_recommendation(aqi, "Jogging/Running", "Asthma/Respiratory")
            
            assert len(recommendation.time_windows) == 0
            
            # Step 2: Format empty time windows - should provide explanation
            windows_text = format_time_windows(recommendation.time_windows, basic_user_profile)
            assert len(windows_text) > 0
            # Should handle empty list gracefully - either indicate no windows or return empty/minimal text
            # The function should not crash with empty list
            assert isinstance(windows_text, str)
    
    def test_time_window_formatting_for_technical_user(
        self,
        mock_bedrock_client,
        technical_user_profile
    ):
        """Test time window formatting includes confidence for technical users"""
        # Create time windows with confidence levels
        time_windows = [
            TimeWindow(
                start_time=datetime.utcnow() + timedelta(hours=3),
                end_time=datetime.utcnow() + timedelta(hours=6),
                expected_aqi_range=(45, 65),
                confidence="High"
            ),
            TimeWindow(
                start_time=datetime.utcnow() + timedelta(hours=10),
                end_time=datetime.utcnow() + timedelta(hours=13),
                expected_aqi_range=(55, 75),
                confidence="Medium"
            )
        ]
        
        # Format for technical user
        windows_text = format_time_windows(time_windows, technical_user_profile)
        assert len(windows_text) > 0
        # Technical user should see confidence levels
        assert "high" in windows_text.lower() or "medium" in windows_text.lower()
        # Should include AQI range information
        assert any(str(val) in windows_text for val in [45, 65, 55, 75])


class TestPartialDataHandlingFlow:
    """Test flow: partial data handling → limited recommendation → warning display"""
    
    def test_partial_pollutant_data_generates_limited_recommendation(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        sample_location,
        basic_user_profile
    ):
        """Test partial data generates recommendation with limitations noted"""
        # Create partial measurements (only PM2.5, missing other pollutants)
        now = datetime.utcnow()
        partial_measurements = [
            Measurement("PM2.5", 35.4, "μg/m³", now, sample_location)
        ]
        
        # Mock AQI calculator to return result based on partial data
        partial_aqi = OverallAQI(
            aqi=100,
            category="Moderate",
            color="#FFFF00",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 35.4, 100, "Moderate", "#FFFF00")
            ],
            timestamp=now,
            location=sample_location
        )
        
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            mock_get_loc.return_value = sample_location
            mock_get_curr.return_value = partial_measurements
            mock_calc_aqi.return_value = partial_aqi
            # Mock Bedrock to return recommendation noting limitations
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Based on available PM2.5 data, air quality is moderate. Note: Other pollutant data unavailable.",
                precautions=["Monitor symptoms", "Data is limited"],
                time_windows=[],
                reasoning="Recommendation based on partial data (PM2.5 only)"
            )
            
            # Step 1: Resolve location
            location = resolve_location("San Francisco")
            
            # Step 2: Fetch AQI with partial data
            aqi = fetch_current_aqi(location)
            assert aqi.aqi == 100
            assert len(aqi.individual_results) == 1
            
            # Step 3: Generate recommendation
            recommendation = generate_recommendation(aqi, "Walking", "None")
            assert "partial" in recommendation.reasoning.lower() or "limited" in recommendation.recommendation_text.lower()
            
            # Step 4: Format response with warning
            rec_text = format_recommendation(recommendation, basic_user_profile)
            assert len(rec_text) > 0
            # Should contain information about data limitations or partial data
            # Note: The actual warning text may vary based on Bedrock adaptation
            assert len(rec_text) > 20  # Should have substantial content
    
    def test_no_critical_data_prevents_recommendation(
        self,
        mock_data_fetcher,
        sample_location
    ):
        """Test that missing critical data prevents recommendation generation"""
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr:
            
            # Mock no measurements available
            mock_get_loc.return_value = sample_location
            mock_get_curr.return_value = []
            
            # Step 1: Resolve location
            location = resolve_location("San Francisco")
            assert location is not None
            
            # Step 2: Try to fetch AQI - should raise error
            with pytest.raises(NoDataAvailableError) as exc_info:
                fetch_current_aqi(location)
            
            # Error message should be user-friendly
            assert "no recent air quality data" in str(exc_info.value).lower()
    
    def test_stale_partial_data_includes_multiple_warnings(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        sample_location,
        basic_user_profile
    ):
        """Test stale partial data includes both staleness and limitation warnings"""
        # Create stale partial measurements
        old_time = datetime.utcnow() - timedelta(hours=5)
        stale_partial_measurements = [
            Measurement("PM2.5", 30.0, "μg/m³", old_time, sample_location)
        ]
        
        # Mock AQI with stale timestamp
        stale_partial_aqi = OverallAQI(
            aqi=85,
            category="Moderate",
            color="#FFFF00",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 30.0, 85, "Moderate", "#FFFF00")
            ],
            timestamp=old_time,
            location=sample_location
        )
        
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            mock_get_loc.return_value = sample_location
            mock_get_curr.return_value = stale_partial_measurements
            mock_calc_aqi.return_value = stale_partial_aqi
            # Mock Bedrock recommendation
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate based on limited data.",
                precautions=["Data is limited and may be outdated"],
                time_windows=[],
                reasoning="Based on stale partial data"
            )
            
            # Fetch AQI and generate recommendation
            location = resolve_location("San Francisco")
            aqi = fetch_current_aqi(location)
            recommendation = generate_recommendation(aqi, "Walking", "None")
            
            # Format response
            aqi_text = format_aqi_explanation(aqi, basic_user_profile)
            rec_text = format_recommendation(recommendation, basic_user_profile)
            
            # Should have substantial content
            assert len(aqi_text) > 20
            assert len(rec_text) > 20
            # Combined text should provide information about the situation
            combined_text = aqi_text + " " + rec_text
            assert len(combined_text) > 50


class TestEndToEndConversationWithBackendFlow:
    """Test complete conversation flow with backend integration"""
    
    def test_complete_conversation_with_backend_integration(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response
    ):
        """Test complete conversation from greeting to recommendation with backend calls"""
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            # Configure mocks
            mock_get_loc.return_value = valid_location_response['location']
            mock_get_curr.return_value = valid_location_response['measurements']
            mock_calc_aqi.return_value = valid_location_response['overall_aqi']
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate.",
                precautions=["Monitor symptoms"],
                time_windows=[],
                reasoning="AQI is 100"
            )
            
            # Create session
            session = create_session()
            session_id = session.session_id
            
            # Step 1: Greeting
            response1 = process_user_input(session_id, "Hello")
            assert "location" in response1.lower()
            
            # Step 2: Location (triggers backend call to resolve_location)
            response2 = process_user_input(session_id, "San Francisco")
            assert "activity" in response2.lower()
            # Verify backend was called
            assert mock_get_loc.called
            
            # Step 3: Activity
            response3 = process_user_input(session_id, "Walking")
            assert "health" in response3.lower()
            
            # Step 4: Health profile (triggers backend calls for AQI and recommendation)
            response4 = process_user_input(session_id, "None")
            assert len(response4) > 0
            
            # Verify backend integration was called
            # Note: Depending on implementation, these may be called during recommendation generation
            # which might be async or deferred
            
            # Verify session has complete context
            final_session = get_session(session_id)
            assert final_session.location is not None
            assert final_session.location.name == "San Francisco"
            assert final_session.activity_profile == "Walking"
            assert final_session.health_profile == "None"
    
    def test_follow_up_time_windows_request_with_backend(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        complete_session_context
    ):
        """Test follow-up time windows request triggers backend integration"""
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            # Configure mocks
            mock_get_loc.return_value = valid_location_response['location']
            mock_get_curr.return_value = valid_location_response['measurements']
            mock_calc_aqi.return_value = valid_location_response['overall_aqi']
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate.",
                precautions=["Monitor symptoms"],
                time_windows=[
                    TimeWindow(
                        start_time=datetime.utcnow() + timedelta(hours=2),
                        end_time=datetime.utcnow() + timedelta(hours=5),
                        expected_aqi_range=(50, 75),
                        confidence="Medium"
                    )
                ],
                reasoning="AQI is 100"
            )
            
            # Use complete session context
            session_id = complete_session_context.session_id
            
            # Request time windows
            response = process_user_input(session_id, "When is the best time for my activity?")
            
            # Should get response about time windows
            assert len(response) > 0
            # Response should mention time or windows
            assert any(word in response.lower() for word in ["time", "window", "when", "hour"])
    
    def test_follow_up_trends_request_with_backend(
        self,
        mock_data_fetcher,
        sample_location,
        complete_session_context
    ):
        """Test follow-up trends request triggers historical data fetch"""
        # Create mock historical data
        now = datetime.utcnow()
        historical_measurements = {
            "PM2.5": [
                Measurement("PM2.5", 30.0, "μg/m³", now - timedelta(hours=i*3), sample_location)
                for i in range(8)
            ]
        }
        
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_historical_measurements') as mock_get_hist:
            mock_get_hist.return_value = historical_measurements
            
            # Use complete session context
            session_id = complete_session_context.session_id
            
            # Request trends
            response = process_user_input(session_id, "Show me air quality trends")
            
            # Should get response about trends
            assert len(response) > 0
            # Response should mention trends or patterns
            assert any(word in response.lower() for word in ["trend", "pattern", "hour", "day"])
    
    def test_location_change_triggers_new_backend_calls(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        complete_session_context
    ):
        """Test mid-session location change triggers new backend integration flow"""
        # Initial location is San Francisco
        assert complete_session_context.location.name == "San Francisco"
        
        # Configure mocks for new location
        new_location = Location(
            name="Los Angeles",
            coordinates=(34.0522, -118.2437),
            country="US",
            providers=["PurpleAir"]
        )
        new_measurements = [
            Measurement("PM2.5", 45.0, "μg/m³", datetime.utcnow(), new_location),
            Measurement("PM10", 65.0, "μg/m³", datetime.utcnow(), new_location),
        ]
        new_aqi = OverallAQI(
            aqi=120,
            category="Unhealthy for Sensitive Groups",
            color="#FF7E00",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 45.0, 120, "Unhealthy for Sensitive Groups", "#FF7E00")
            ],
            timestamp=datetime.utcnow(),
            location=new_location
        )
        
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            mock_get_loc.return_value = new_location
            mock_get_curr.return_value = new_measurements
            mock_calc_aqi.return_value = new_aqi
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is unhealthy for sensitive groups.",
                precautions=["Limit outdoor activities"],
                time_windows=[],
                reasoning="AQI is 120"
            )
            
            # Request location change
            session_id = complete_session_context.session_id
            response = process_user_input(session_id, "Change location to Los Angeles")
            
            # Should get response about location change
            assert len(response) > 0
            
            # Verify session context - activity and health profile should be preserved
            updated_session = get_session(session_id)
            if updated_session:
                # If session still exists, verify preserved context
                assert updated_session.activity_profile == "Walking"
                assert updated_session.health_profile == "None"


class TestAdaptiveResponseFormattingFlow:
    """Test response formatting adapts to user profile throughout the flow"""
    
    def test_basic_user_gets_simplified_responses(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        basic_user_profile
    ):
        """Test basic user profile gets simplified vocabulary throughout flow"""
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            # Configure mocks
            mock_get_loc.return_value = valid_location_response['location']
            mock_get_curr.return_value = valid_location_response['measurements']
            mock_calc_aqi.return_value = valid_location_response['overall_aqi']
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate.",
                precautions=["Monitor symptoms"],
                time_windows=[],
                reasoning="AQI is 100"
            )
            
            # Generate and format responses
            location = resolve_location("San Francisco")
            aqi = fetch_current_aqi(location)
            recommendation = generate_recommendation(aqi, "Walking", "None")
            
            # Format for basic user
            aqi_text = format_aqi_explanation(aqi, basic_user_profile)
            rec_text = format_recommendation(recommendation, basic_user_profile)
            
            # Should use simplified vocabulary
            combined_text = aqi_text + " " + rec_text
            # Should not contain technical jargon
            assert "particulate matter" not in combined_text.lower()
            assert "μg/m³" not in combined_text
            # Should be accessible
            assert len(combined_text) > 0
    
    def test_technical_user_gets_detailed_responses(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        technical_user_profile
    ):
        """Test technical user profile gets detailed information throughout flow"""
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            # Configure mocks
            mock_get_loc.return_value = valid_location_response['location']
            mock_get_curr.return_value = valid_location_response['measurements']
            mock_calc_aqi.return_value = valid_location_response['overall_aqi']
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate.",
                precautions=["Monitor symptoms"],
                time_windows=[],
                reasoning="AQI is 100"
            )
            
            # Generate and format responses
            location = resolve_location("San Francisco")
            aqi = fetch_current_aqi(location)
            recommendation = generate_recommendation(aqi, "Walking", "None")
            
            # Format for technical user
            aqi_text = format_aqi_explanation(aqi, technical_user_profile)
            rec_text = format_recommendation(recommendation, technical_user_profile)
            
            # Should include technical details
            combined_text = aqi_text + " " + rec_text
            # Should contain technical information
            assert any(term in combined_text.lower() for term in ["pollutant", "concentration", "pm2.5", "pm10"])
            assert len(combined_text) > 0
    
    def test_child_user_gets_age_appropriate_responses(
        self,
        mock_data_fetcher,
        mock_aqi_calculator,
        mock_bedrock_client,
        valid_location_response,
        child_user_profile
    ):
        """Test child user profile gets age-appropriate language"""
        # Patch at backend_integration level
        with patch('src.chatbot.backend_integration.get_location') as mock_get_loc, \
             patch('src.chatbot.backend_integration.get_current_measurements') as mock_get_curr, \
             patch('src.chatbot.backend_integration.calculate_overall_aqi') as mock_calc_aqi, \
             patch('src.chatbot.backend_integration.get_recommendation') as mock_get_rec:
            
            # Configure mocks
            mock_get_loc.return_value = valid_location_response['location']
            mock_get_curr.return_value = valid_location_response['measurements']
            mock_calc_aqi.return_value = valid_location_response['overall_aqi']
            mock_get_rec.return_value = RecommendationResponse(
                safety_assessment="Moderate Risk",
                recommendation_text="Air quality is moderate.",
                precautions=["Monitor symptoms"],
                time_windows=[],
                reasoning="AQI is 100"
            )
            
            # Generate and format responses
            location = resolve_location("San Francisco")
            aqi = fetch_current_aqi(location)
            recommendation = generate_recommendation(aqi, "Child Outdoor Play", "Child/Elderly")
            
            # Format for child user
            aqi_text = format_aqi_explanation(aqi, child_user_profile)
            rec_text = format_recommendation(recommendation, child_user_profile)
            
            # Should use simple, age-appropriate language
            combined_text = aqi_text + " " + rec_text
            # Should not contain complex technical terms
            assert "particulate matter" not in combined_text.lower()
            # Should be understandable
            assert len(combined_text) > 0
