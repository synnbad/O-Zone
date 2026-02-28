"""
Shared fixtures and mocks for O-Zone MVP tests.

This module provides reusable test fixtures for OpenAQ and Bedrock API mocking,
as well as common test data generators.
"""

import pytest
from datetime import datetime, timedelta
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
        timestamp=datetime.utcnow(),
        location=sample_location
    )


@pytest.fixture
def sample_measurements_all_pollutants(sample_location):
    """Create measurements for all six pollutants."""
    now = datetime.utcnow()
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
    old_time = datetime.utcnow() - timedelta(hours=4)
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
        timestamp=datetime.utcnow(),
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
    now = datetime.utcnow().isoformat()
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
                "start_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
                "end_time": (datetime.utcnow() + timedelta(hours=5)).isoformat(),
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
    now = datetime.utcnow()
    
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
