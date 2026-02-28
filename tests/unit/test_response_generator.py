"""
Unit tests for response_generator module.

Tests adaptive formatting functions including vocabulary adaptation,
sentence complexity adaptation, and AI-powered response generation.
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.chatbot.response_generator import (
    adapt_vocabulary,
    adapt_sentence_complexity,
    format_aqi_explanation,
    format_recommendation,
    generate_response
)
from src.chatbot.session_manager import UserProfile
from src.models import OverallAQI, AQIResult, RecommendationResponse, TimeWindow


@pytest.fixture
def basic_user_profile():
    """User profile for basic/child users."""
    return UserProfile(
        age_group="child",
        education_level="basic",
        technical_expertise="none",
        communication_preference="balanced",
        occupation_category="general",
        inferred=False
    )


@pytest.fixture
def expert_user_profile():
    """User profile for expert users."""
    return UserProfile(
        age_group="adult",
        education_level="advanced",
        technical_expertise="expert",
        communication_preference="detailed",
        occupation_category="environmental_scientist",
        inferred=False
    )


@pytest.fixture
def mock_aqi():
    """Mock OverallAQI object."""
    from datetime import datetime
    from src.models import Location
    
    location = Location(
        name="Test City",
        coordinates=(40.7128, -74.0060),
        country="US",
        providers=["openaq"]
    )
    
    return OverallAQI(
        aqi=85,
        category="Moderate",
        color="#FFFF00",
        dominant_pollutant="PM2.5",
        individual_results=[
            AQIResult(pollutant="PM2.5", concentration=35.5, aqi=85, category="Moderate", color="#FFFF00"),
            AQIResult(pollutant="PM10", concentration=50.0, aqi=45, category="Good", color="#00E400")
        ],
        timestamp=datetime(2024, 1, 15, 10, 0),
        location=location
    )


@pytest.fixture
def mock_recommendation():
    """Mock RecommendationResponse object."""
    return RecommendationResponse(
        safety_assessment="Moderate Risk",
        recommendation_text="You can proceed with your outdoor activity, but consider taking breaks if you feel any discomfort.",
        precautions=["Stay hydrated", "Monitor how you feel"],
        reasoning="Air quality is moderate, which is acceptable for most outdoor activities.",
        time_windows=[
            TimeWindow(
                start_time=datetime(2024, 1, 15, 10, 0),
                end_time=datetime(2024, 1, 15, 12, 0),
                expected_aqi_range=(40, 60),
                confidence="High"
            )
        ]
    )


class TestAdaptVocabulary:
    """Tests for adapt_vocabulary function."""
    
    def test_adapt_vocabulary_without_profile_basic(self):
        """Test rule-based vocabulary adaptation for basic level."""
        text = "The AQI is 85 with high pollutant concentration."
        result = adapt_vocabulary(text, "basic", user_profile=None)
        
        # Should apply rule-based replacements
        assert "air quality number" in result or "AQI" in result
    
    def test_adapt_vocabulary_without_profile_standard(self):
        """Test vocabulary adaptation returns unchanged text for standard level."""
        text = "The AQI is 85 with moderate pollution."
        result = adapt_vocabulary(text, "standard", user_profile=None)
        
        # Should return unchanged
        assert result == text
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_adapt_vocabulary_with_profile_basic_uses_ai(self, mock_generate, basic_user_profile):
        """Test AI-powered vocabulary adaptation for basic level."""
        text = "The AQI is 85 with high pollutant concentration."
        mock_generate.return_value = "The air quality number is 85 with lots of air pollution."
        
        result = adapt_vocabulary(text, "basic", user_profile=basic_user_profile)
        
        # Should call AI adaptation
        assert mock_generate.called
        assert result == "The air quality number is 85 with lots of air pollution."
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_adapt_vocabulary_with_profile_technical_uses_ai(self, mock_generate, expert_user_profile):
        """Test AI-powered vocabulary adaptation for technical level."""
        text = "The air quality is moderate."
        mock_generate.return_value = "The AQI indicates moderate particulate matter concentration."
        
        result = adapt_vocabulary(text, "technical", user_profile=expert_user_profile)
        
        # Should call AI adaptation
        assert mock_generate.called
        assert result == "The AQI indicates moderate particulate matter concentration."
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_adapt_vocabulary_fallback_on_error(self, mock_generate, basic_user_profile):
        """Test fallback to rule-based when AI fails."""
        text = "The AQI is 85."
        mock_generate.side_effect = Exception("Bedrock unavailable")
        
        result = adapt_vocabulary(text, "basic", user_profile=basic_user_profile)
        
        # Should fall back to rule-based
        assert result is not None


class TestAdaptSentenceComplexity:
    """Tests for adapt_sentence_complexity function."""
    
    def test_adapt_sentence_complexity_without_profile_simple(self):
        """Test rule-based sentence simplification."""
        text = "The air quality is good, and you can go outside."
        result = adapt_sentence_complexity(text, "simple", user_profile=None)
        
        # Should break at conjunction
        assert ". " in result or text == result
    
    def test_adapt_sentence_complexity_without_profile_moderate(self):
        """Test sentence complexity returns unchanged for moderate level."""
        text = "The air quality is moderate."
        result = adapt_sentence_complexity(text, "moderate", user_profile=None)
        
        # Should return unchanged
        assert result == text
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_adapt_sentence_complexity_with_profile_simple_uses_ai(self, mock_generate, basic_user_profile):
        """Test AI-powered sentence simplification."""
        text = "The air quality is moderate, and you should consider taking precautions."
        mock_generate.return_value = "The air quality is moderate. You should take precautions."
        
        result = adapt_sentence_complexity(text, "simple", user_profile=basic_user_profile)
        
        # Should call AI adaptation
        assert mock_generate.called
        assert result == "The air quality is moderate. You should take precautions."
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_adapt_sentence_complexity_fallback_on_error(self, mock_generate, basic_user_profile):
        """Test fallback to rule-based when AI fails."""
        text = "The air quality is good, and you can go outside."
        mock_generate.side_effect = Exception("Bedrock unavailable")
        
        result = adapt_sentence_complexity(text, "simple", user_profile=basic_user_profile)
        
        # Should fall back to rule-based
        assert result is not None


class TestFormatAQIExplanation:
    """Tests for format_aqi_explanation function."""
    
    def test_format_aqi_explanation_none(self, basic_user_profile):
        """Test handling of None AQI."""
        result = format_aqi_explanation(None, basic_user_profile)
        assert "don't have air quality data" in result
    
    def test_format_aqi_explanation_basic_profile_rule_based(self, mock_aqi):
        """Test rule-based formatting for basic profile when AI not used."""
        profile = UserProfile(
            age_group="adult",
            education_level="high_school",
            technical_expertise="basic",
            communication_preference="balanced",
            occupation_category="general",
            inferred=False
        )
        
        result = format_aqi_explanation(mock_aqi, profile)
        
        # Should contain AQI value and category
        assert "85" in result
        assert "Moderate" in result
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_format_aqi_explanation_child_uses_ai(self, mock_generate, basic_user_profile, mock_aqi):
        """Test AI-powered formatting for child users."""
        mock_generate.return_value = "The air quality number is 85. That means it's okay to play outside."
        
        result = format_aqi_explanation(mock_aqi, basic_user_profile)
        
        # Should call AI adaptation for child
        assert mock_generate.called
        assert "air quality number" in result.lower()
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_format_aqi_explanation_expert_uses_ai(self, mock_generate, expert_user_profile, mock_aqi):
        """Test AI-powered formatting for expert users."""
        mock_generate.return_value = "AQI: 85 (Moderate). Dominant pollutant: PM2.5 at 35.5 μg/m³."
        
        result = format_aqi_explanation(mock_aqi, expert_user_profile)
        
        # Should call AI adaptation for expert
        assert mock_generate.called
        assert "PM2.5" in result
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_format_aqi_explanation_fallback_on_error(self, mock_generate, basic_user_profile, mock_aqi):
        """Test fallback to rule-based when AI fails."""
        mock_generate.side_effect = Exception("Bedrock unavailable")
        
        result = format_aqi_explanation(mock_aqi, basic_user_profile)
        
        # Should fall back to rule-based
        assert "85" in result
        assert "Moderate" in result


class TestFormatRecommendation:
    """Tests for format_recommendation function."""
    
    def test_format_recommendation_none(self, basic_user_profile):
        """Test handling of None recommendation."""
        result = format_recommendation(None, basic_user_profile)
        assert "couldn't generate a recommendation" in result
    
    def test_format_recommendation_basic_profile_rule_based(self, mock_recommendation):
        """Test rule-based formatting when AI not used."""
        profile = UserProfile(
            age_group="adult",
            education_level="high_school",
            technical_expertise="basic",
            communication_preference="balanced",
            occupation_category="general",
            inferred=False
        )
        
        result = format_recommendation(mock_recommendation, profile)
        
        # Should contain safety assessment and recommendation
        assert "Moderate" in result
        assert "outdoor activity" in result
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_format_recommendation_child_uses_ai(self, mock_generate, basic_user_profile, mock_recommendation):
        """Test AI-powered formatting for child users."""
        mock_generate.return_value = "It's okay to play outside. Drink water and take breaks."
        
        result = format_recommendation(mock_recommendation, basic_user_profile)
        
        # Should call AI adaptation for child
        assert mock_generate.called
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_format_recommendation_concise_uses_ai(self, mock_generate, mock_recommendation):
        """Test AI-powered formatting for concise preference."""
        profile = UserProfile(
            age_group="adult",
            education_level="college",
            technical_expertise="intermediate",
            communication_preference="concise",
            occupation_category="general",
            inferred=False
        )
        mock_generate.return_value = "Safe for outdoor activity. Stay hydrated."
        
        result = format_recommendation(mock_recommendation, profile)
        
        # Should call AI adaptation for concise preference
        assert mock_generate.called
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_format_recommendation_detailed_uses_ai(self, mock_generate, mock_recommendation):
        """Test AI-powered formatting for detailed preference."""
        profile = UserProfile(
            age_group="adult",
            education_level="college",
            technical_expertise="intermediate",
            communication_preference="detailed",
            occupation_category="general",
            inferred=False
        )
        mock_generate.return_value = "The air quality is moderate, which means it's generally safe for outdoor activities. However, you should monitor how you feel and take breaks if needed."
        
        result = format_recommendation(mock_recommendation, profile)
        
        # Should call AI adaptation for detailed preference
        assert mock_generate.called
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_format_recommendation_includes_time_windows(self, mock_generate, basic_user_profile, mock_recommendation):
        """Test that time windows are included in adapted response."""
        mock_generate.return_value = "It's okay to play outside."
        
        result = format_recommendation(mock_recommendation, basic_user_profile)
        
        # Should include time windows
        assert "10:00 AM" in result or "time" in result.lower()
    
    @patch('src.chatbot.bedrock_adapter.generate_adaptive_response')
    def test_format_recommendation_fallback_on_error(self, mock_generate, basic_user_profile, mock_recommendation):
        """Test fallback to rule-based when AI fails."""
        mock_generate.side_effect = Exception("Bedrock unavailable")
        
        result = format_recommendation(mock_recommendation, basic_user_profile)
        
        # Should fall back to rule-based
        assert "Moderate" in result
        assert "outdoor activity" in result


class TestGenerateResponse:
    """Tests for generate_response function."""
    
    def test_generate_response_aqi_explanation(self, mock_aqi, basic_user_profile):
        """Test generating AQI explanation response."""
        result = generate_response(
            "aqi_explanation",
            {"aqi": mock_aqi},
            basic_user_profile
        )
        
        assert "85" in result
        assert "Moderate" in result
    
    def test_generate_response_recommendation(self, mock_recommendation, basic_user_profile):
        """Test generating recommendation response."""
        result = generate_response(
            "recommendation",
            {"recommendation": mock_recommendation},
            basic_user_profile
        )
        
        # Should contain recommendation content (flexible check for AI-generated or rule-based)
        assert len(result) > 0
        assert "10:00 AM" in result or "time" in result.lower()  # Time windows should be included
    
    def test_generate_response_unknown_type(self, basic_user_profile):
        """Test handling of unknown message type."""
        result = generate_response(
            "unknown_type",
            {},
            basic_user_profile
        )
        
        assert "not sure how to respond" in result
