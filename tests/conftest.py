"""
Shared fixtures and mocks for O-Zone MVP tests.

This module provides reusable test fixtures for OpenAQ and Bedrock API mocking,
as well as common test data generators.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, MagicMock
import json

from src.models import Location, Measurement, AQIResult, OverallAQI


# ============================================================================
# Location Fixtures
# ============================================================================

@pytest.fixture
def sample_location():
    """Create a sample Location object for testing."""
    return Location(
        name="San Francisco",
        coordinates=(37.7749, -122.4194),
        country="US",
        providers=["PurpleAir", "AirNow"]
    )


@pytest.fixture
def sample_location_beijing():
    """Create a sample Beijing Location object for testing."""
    return Location(
        name="Beijing",
        coordinates=(39.9042, 116.4074),
        country="CN",
        providers=["CNEMC"]
    )


# ============================================================================
# Measurement Fixtures
# ============================================================================

@pytest.fixture
def sample_measurement_pm25(sample_location):
    """Create a sample PM2.5 measurement."""
    return Measurement(
        pollutant="PM2.5",
        value=35.4,
        unit="μg/m³",
        timestamp=datetime.now(timezone.utc),
        location=sample_location
    )


@pytest.fixture
def sample_measurements_all_pollutants(sample_location):
    """Create measurements for all six pollutants."""
    now = datetime.now(timezone.utc)
    return [
        Measurement("PM2.5", 35.4, "μg/m³", now, sample_location),
        Measurement("PM10", 54.0, "μg/m³", now, sample_location),
        Measurement("CO", 4.4, "ppm", now, sample_location),
        Measurement("NO2", 53.0, "ppb", now, sample_location),
        Measurement("O3", 54.0, "ppb", now, sample_location),
        Measurement("SO2", 35.0, "ppb", now, sample_location),
    ]


@pytest.fixture
def stale_measurement(sample_location):
    """Create a measurement older than 3 hours."""
    old_time = datetime.now(timezone.utc) - timedelta(hours=4)
    return Measurement(
        pollutant="PM2.5",
        value=25.0,
        unit="μg/m³",
        timestamp=old_time,
        location=sample_location
    )


# ============================================================================
# AQI Result Fixtures
# ============================================================================

@pytest.fixture
def sample_aqi_result():
    """Create a sample AQI result."""
    return AQIResult(
        pollutant="PM2.5",
        concentration=35.4,
        aqi=100,
        category="Moderate",
        color="#FFFF00"
    )


@pytest.fixture
def sample_overall_aqi(sample_location, sample_aqi_result):
    """Create a sample OverallAQI object."""
    return OverallAQI(
        aqi=100,
        category="Moderate",
        color="#FFFF00",
        dominant_pollutant="PM2.5",
        individual_results=[sample_aqi_result],
        timestamp=datetime.now(timezone.utc),
        location=sample_location
    )


# ============================================================================
# OpenAQ API Mocks
# ============================================================================

@pytest.fixture
def mock_openaq_location_response():
    """Mock OpenAQ API location search response."""
    return {
        "results": [
            {
                "id": 12345,
                "name": "San Francisco",
                "locality": "San Francisco",
                "country": {"code": "US", "name": "United States"},
                "coordinates": {"latitude": 37.7749, "longitude": -122.4194},
                "providers": [{"name": "PurpleAir"}, {"name": "AirNow"}]
            }
        ]
    }


@pytest.fixture
def mock_openaq_measurements_response():
    """Mock OpenAQ API measurements response."""
    now = datetime.now(timezone.utc).isoformat()
    return {
        "results": [
            {
                "parameter": {"name": "pm25"},
                "value": 35.4,
                "unit": "μg/m³",
                "date": {"utc": now},
                "location": {
                    "name": "San Francisco",
                    "coordinates": {"latitude": 37.7749, "longitude": -122.4194},
                    "country": {"code": "US"}
                }
            },
            {
                "parameter": {"name": "pm10"},
                "value": 54.0,
                "unit": "μg/m³",
                "date": {"utc": now},
                "location": {
                    "name": "San Francisco",
                    "coordinates": {"latitude": 37.7749, "longitude": -122.4194},
                    "country": {"code": "US"}
                }
            }
        ]
    }


@pytest.fixture
def mock_openaq_empty_response():
    """Mock OpenAQ API empty response."""
    return {"results": []}


@pytest.fixture
def mock_openaq_error_response():
    """Mock OpenAQ API error response."""
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }


# ============================================================================
# Bedrock API Mocks
# ============================================================================

@pytest.fixture
def mock_bedrock_client():
    """Mock boto3 Bedrock client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_bedrock_response():
    """Mock Bedrock API response with Claude output."""
    recommendation = {
        "safety_assessment": "Moderate Risk",
        "recommendation_text": "Air quality is moderate. Sensitive individuals should consider reducing prolonged outdoor activities.",
        "precautions": [
            "Consider wearing a mask if you have respiratory sensitivities",
            "Monitor symptoms and move indoors if you experience discomfort"
        ],
        "time_windows": [
            {
                "start_time": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
                "end_time": (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat(),
                "expected_aqi_range": [50, 75],
                "confidence": "Medium"
            }
        ],
        "reasoning": "Current AQI is 100 (Moderate) with PM2.5 as the dominant pollutant."
    }
    
    return {
        "body": Mock(read=lambda: json.dumps({
            "content": [{"text": json.dumps(recommendation)}]
        }).encode())
    }


@pytest.fixture
def mock_bedrock_malformed_response():
    """Mock Bedrock API response with malformed JSON."""
    return {
        "body": Mock(read=lambda: b'{"content": [{"text": "This is not valid JSON for a recommendation"}]}')
    }


# ============================================================================
# Helper Functions
# ============================================================================

def create_mock_measurements_with_aqis(aqi_values: list[int], location: Location = None) -> list[Measurement]:
    """
    Create mock measurements that will produce specific AQI values.
    
    Args:
        aqi_values: List of desired AQI values
        location: Location object (creates default if None)
        
    Returns:
        List of Measurement objects
    """
    if location is None:
        location = Location("Test City", (37.7, -122.4), "US", ["test"])
    
    pollutants = ['PM2.5', 'PM10', 'CO', 'NO2', 'O3', 'SO2']
    measurements = []
    now = datetime.now(timezone.utc)
    
    # Map AQI values to approximate concentrations
    aqi_to_concentration = {
        'PM2.5': lambda aqi: 12.0 if aqi <= 50 else 35.4 if aqi <= 100 else 55.4,
        'PM10': lambda aqi: 54.0 if aqi <= 50 else 154.0 if aqi <= 100 else 254.0,
        'CO': lambda aqi: 4.4 if aqi <= 50 else 9.4 if aqi <= 100 else 12.4,
        'NO2': lambda aqi: 53.0 if aqi <= 50 else 100.0 if aqi <= 100 else 360.0,
        'O3': lambda aqi: 54.0 if aqi <= 50 else 70.0 if aqi <= 100 else 85.0,
        'SO2': lambda aqi: 35.0 if aqi <= 50 else 75.0 if aqi <= 100 else 185.0,
    }
    
    for i, aqi in enumerate(aqi_values):
        if i >= len(pollutants):
            break
        pollutant = pollutants[i]
        concentration = aqi_to_concentration[pollutant](aqi)
        unit = "μg/m³" if pollutant in ['PM2.5', 'PM10'] else "ppm" if pollutant == 'CO' else "ppb"
        
        measurements.append(Measurement(
            pollutant=pollutant,
            value=concentration,
            unit=unit,
            timestamp=now,
            location=location
        ))
    
    return measurements


# ============================================================================
# Chatbot Integration Test Fixtures
# ============================================================================

@pytest.fixture
def mock_data_fetcher():
    """Mock data_fetcher module for integration tests."""
    from unittest.mock import patch
    
    # Patch at the source module level
    with patch('src.data_fetcher.get_location') as mock_get_location, \
         patch('src.data_fetcher.get_current_measurements') as mock_get_current, \
         patch('src.data_fetcher.get_historical_measurements') as mock_get_historical:
        
        # Default behavior: return valid location
        mock_get_location.return_value = Location(
            name="San Francisco",
            coordinates=(37.7749, -122.4194),
            country="US",
            providers=["PurpleAir"]
        )
        
        # Default behavior: return valid measurements
        now = datetime.now(timezone.utc)
        default_location = mock_get_location.return_value
        mock_get_current.return_value = [
            Measurement("PM2.5", 35.4, "μg/m³", now, default_location),
            Measurement("PM10", 54.0, "μg/m³", now, default_location),
        ]
        
        # Default behavior: return empty historical data
        mock_get_historical.return_value = {}
        
        yield {
            'get_location': mock_get_location,
            'get_current_measurements': mock_get_current,
            'get_historical_measurements': mock_get_historical
        }


@pytest.fixture
def mock_aqi_calculator():
    """Mock aqi_calculator module for integration tests."""
    from unittest.mock import patch
    
    with patch('src.aqi_calculator.calculate_overall_aqi') as mock_calc:
        # Default behavior: return moderate AQI
        mock_calc.return_value = OverallAQI(
            aqi=100,
            category="Moderate",
            color="#FFFF00",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 35.4, 100, "Moderate", "#FFFF00")
            ],
            timestamp=datetime.now(timezone.utc),
            location=Location("San Francisco", (37.7749, -122.4194), "US", ["PurpleAir"])
        )
        
        yield mock_calc


@pytest.fixture
def mock_bedrock_client():
    """Mock bedrock_client module for integration tests."""
    from unittest.mock import patch
    from src.models import RecommendationResponse, TimeWindow
    
    with patch('src.bedrock_client.get_recommendation') as mock_get_rec:
        # Default behavior: return valid recommendation
        mock_get_rec.return_value = RecommendationResponse(
            safety_assessment="Moderate Risk",
            recommendation_text="Air quality is moderate. Sensitive individuals should consider reducing prolonged outdoor activities.",
            precautions=[
                "Consider wearing a mask if you have respiratory sensitivities",
                "Monitor symptoms and move indoors if you experience discomfort"
            ],
            time_windows=[
                TimeWindow(
                    start_time=datetime.now(timezone.utc) + timedelta(hours=2),
                    end_time=datetime.now(timezone.utc) + timedelta(hours=5),
                    expected_aqi_range=(50, 75),
                    confidence="Medium"
                )
            ],
            reasoning="Current AQI is 100 (Moderate) with PM2.5 as the dominant pollutant."
        )
        
        yield mock_get_rec


# ============================================================================
# Common Response Pattern Fixtures
# ============================================================================

@pytest.fixture
def valid_location_response():
    """Fixture for valid location resolution scenario."""
    return {
        'location': Location(
            name="San Francisco",
            coordinates=(37.7749, -122.4194),
            country="US",
            providers=["PurpleAir", "AirNow"]
        ),
        'measurements': [
            Measurement("PM2.5", 35.4, "μg/m³", datetime.now(timezone.utc), None),
            Measurement("PM10", 54.0, "μg/m³", datetime.now(timezone.utc), None),
        ],
        'overall_aqi': OverallAQI(
            aqi=100,
            category="Moderate",
            color="#FFFF00",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 35.4, 100, "Moderate", "#FFFF00")
            ],
            timestamp=datetime.now(timezone.utc),
            location=None
        )
    }


@pytest.fixture
def no_data_response():
    """Fixture for no data available scenario."""
    return {
        'location': Location(
            name="Remote Village",
            coordinates=(45.0, -120.0),
            country="US",
            providers=[]
        ),
        'measurements': [],
        'overall_aqi': None
    }


@pytest.fixture
def stale_data_response():
    """Fixture for stale data scenario."""
    old_time = datetime.now(timezone.utc) - timedelta(hours=4)
    return {
        'location': Location(
            name="Small Town",
            coordinates=(40.0, -110.0),
            country="US",
            providers=["LocalMonitor"]
        ),
        'measurements': [
            Measurement("PM2.5", 25.0, "μg/m³", old_time, None),
        ],
        'overall_aqi': OverallAQI(
            aqi=75,
            category="Moderate",
            color="#FFFF00",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 25.0, 75, "Moderate", "#FFFF00")
            ],
            timestamp=old_time,
            location=None
        )
    }


@pytest.fixture
def hazardous_aqi_response():
    """Fixture for hazardous air quality scenario."""
    return {
        'location': Location(
            name="Polluted City",
            coordinates=(39.9, 116.4),
            country="CN",
            providers=["CNEMC"]
        ),
        'measurements': [
            Measurement("PM2.5", 250.0, "μg/m³", datetime.now(timezone.utc), None),
            Measurement("PM10", 350.0, "μg/m³", datetime.now(timezone.utc), None),
        ],
        'overall_aqi': OverallAQI(
            aqi=350,
            category="Hazardous",
            color="#7E0023",
            dominant_pollutant="PM2.5",
            individual_results=[
                AQIResult("PM2.5", 250.0, 350, "Hazardous", "#7E0023")
            ],
            timestamp=datetime.now(timezone.utc),
            location=None
        )
    }


# ============================================================================
# User Profile Fixtures
# ============================================================================

@pytest.fixture
def basic_user_profile():
    """User profile for basic education level."""
    from src.chatbot.session_manager import UserProfile
    return UserProfile(
        age_group="adult",
        education_level="basic",
        technical_expertise="none",
        communication_preference="balanced",
        occupation_category="general",
        inferred=False
    )


@pytest.fixture
def child_user_profile():
    """User profile for child age group."""
    from src.chatbot.session_manager import UserProfile
    return UserProfile(
        age_group="child",
        education_level="basic",
        technical_expertise="none",
        communication_preference="detailed",
        occupation_category="general",
        inferred=False
    )


@pytest.fixture
def technical_user_profile():
    """User profile for technical/expert user."""
    from src.chatbot.session_manager import UserProfile
    return UserProfile(
        age_group="adult",
        education_level="advanced",
        technical_expertise="expert",
        communication_preference="detailed",
        occupation_category="environmental_scientist",
        inferred=False
    )


@pytest.fixture
def sensitive_health_profile():
    """User profile with health sensitivity."""
    from src.chatbot.session_manager import UserProfile
    return UserProfile(
        age_group="adult",
        education_level="high_school",
        technical_expertise="basic",
        communication_preference="balanced",
        occupation_category="general",
        inferred=False
    )


@pytest.fixture
def concise_user_profile():
    """User profile preferring concise communication."""
    from src.chatbot.session_manager import UserProfile
    return UserProfile(
        age_group="adult",
        education_level="college",
        technical_expertise="intermediate",
        communication_preference="concise",
        occupation_category="general",
        inferred=False
    )


# ============================================================================
# Session Fixtures
# ============================================================================

@pytest.fixture
def sample_session():
    """Create a sample session with basic context."""
    from src.chatbot.session_manager import create_session, UserProfile
    
    session = create_session()
    session.location = Location(
        name="San Francisco",
        coordinates=(37.7749, -122.4194),
        country="US",
        providers=["PurpleAir"]
    )
    session.activity_profile = "Walking"
    session.health_profile = "None"
    session.user_profile = UserProfile(
        age_group="adult",
        education_level="high_school",
        technical_expertise="basic",
        communication_preference="balanced",
        occupation_category="general",
        inferred=False
    )
    
    return session


@pytest.fixture
def complete_session_context(sample_session, valid_location_response):
    """Create a session with complete context including AQI and recommendation."""
    from src.models import RecommendationResponse, TimeWindow
    
    sample_session.current_aqi = valid_location_response['overall_aqi']
    sample_session.recommendation = RecommendationResponse(
        safety_assessment="Moderate Risk",
        recommendation_text="Air quality is moderate. Consider reducing prolonged outdoor activities.",
        precautions=["Monitor symptoms", "Take breaks if needed"],
        time_windows=[
            TimeWindow(
                start_time=datetime.now(timezone.utc) + timedelta(hours=2),
                end_time=datetime.now(timezone.utc) + timedelta(hours=5),
                expected_aqi_range=(50, 75),
                confidence="Medium"
            )
        ],
        reasoning="AQI is 100 (Moderate)"
    )
    sample_session.current_state = "recommendation_presentation"
    
    return sample_session


# ============================================================================
# Time Mocking Fixtures
# ============================================================================

@pytest.fixture
def frozen_time():
    """Freeze time for session expiration tests."""
    try:
        from freezegun import freeze_time
        with freeze_time("2024-01-15 12:00:00"):
            yield datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    except ImportError:
        # If freezegun not installed, just yield current time
        yield datetime.now(timezone.utc)


@pytest.fixture
def time_travel():
    """Fixture that allows time travel for testing session expiration."""
    try:
        from freezegun import freeze_time
        
        class TimeTraveler:
            def __init__(self):
                self.frozen = None
            
            def freeze(self, time_str):
                """Freeze time at specified datetime string."""
                if self.frozen:
                    self.frozen.stop()
                self.frozen = freeze_time(time_str)
                self.frozen.start()
                return datetime.fromisoformat(time_str.replace(' ', 'T'))
            
            def advance(self, **kwargs):
                """Advance time by specified timedelta."""
                if self.frozen:
                    self.frozen.stop()
                current = datetime.now(timezone.utc)
                new_time = current + timedelta(**kwargs)
                self.frozen = freeze_time(new_time)
                self.frozen.start()
                return new_time
            
            def stop(self):
                """Stop time freezing."""
                if self.frozen:
                    self.frozen.stop()
        
        traveler = TimeTraveler()
        yield traveler
        traveler.stop()
        
    except ImportError:
        # If freezegun not installed, provide a no-op implementation
        class NoOpTimeTraveler:
            def freeze(self, time_str):
                return datetime.now(timezone.utc)
            
            def advance(self, **kwargs):
                return datetime.now(timezone.utc)
            
            def stop(self):
                pass
        
        yield NoOpTimeTraveler()


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_sessions():
    """Automatically clean up session store after each test."""
    yield
    # Clean up session store
    from src.chatbot import session_manager
    session_manager._session_store.clear()
