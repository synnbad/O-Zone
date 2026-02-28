"""
Configuration module for O-Zone MVP.

This module centralizes all system parameters including API endpoints,
cache settings, AQI breakpoint tables, and UI configuration options.
"""

import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass


class Config:
    """Central configuration for O-Zone MVP."""
    
    # API Configuration
    OPENAQ_API_BASE_URL = "https://api.openaq.org/v3"
    OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "")
    
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "")  # For temporary credentials
    BEDROCK_MODEL_ID = "global.anthropic.claude-opus-4-6-v1"  # Claude Opus 4.6 - Global inference profile
    
    # Cache Configuration
    CACHE_TTL_SECONDS = 900  # 15 minutes
    DATA_FRESHNESS_HOURS = 3  # Max age for "current" data
    GLOBE_CACHE_TTL_SECONDS = 3600  # 1 hour for global station data
    
    # AQI Breakpoint Tables (EPA Standard)
    # Format: (concentration_low, concentration_high, aqi_low, aqi_high)
    AQI_BREAKPOINTS: Dict[str, List[Tuple[float, float, int, int]]] = {
        'PM2.5': [  # μg/m³
            (0.0, 12.0, 0, 50),
            (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150),
            (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300),
            (250.5, 500.4, 301, 500),
        ],
        'PM10': [  # μg/m³
            (0.0, 54.0, 0, 50),
            (55.0, 154.0, 51, 100),
            (155.0, 254.0, 101, 150),
            (255.0, 354.0, 151, 200),
            (355.0, 424.0, 201, 300),
            (425.0, 604.0, 301, 500),
        ],
        'CO': [  # ppm
            (0.0, 4.4, 0, 50),
            (4.5, 9.4, 51, 100),
            (9.5, 12.4, 101, 150),
            (12.5, 15.4, 151, 200),
            (15.5, 30.4, 201, 300),
            (30.5, 50.4, 301, 500),
        ],
        'NO2': [  # ppb
            (0.0, 53.0, 0, 50),
            (54.0, 100.0, 51, 100),
            (101.0, 360.0, 101, 150),
            (361.0, 649.0, 151, 200),
            (650.0, 1249.0, 201, 300),
            (1250.0, 2049.0, 301, 500),
        ],
        'O3': [  # ppb (8-hour average)
            (0.0, 54.0, 0, 50),
            (55.0, 70.0, 51, 100),
            (71.0, 85.0, 101, 150),
            (86.0, 105.0, 151, 200),
            (106.0, 200.0, 201, 300),
        ],
        'SO2': [  # ppb
            (0.0, 35.0, 0, 50),
            (36.0, 75.0, 51, 100),
            (76.0, 185.0, 101, 150),
            (186.0, 304.0, 151, 200),
            (305.0, 604.0, 201, 300),
            (605.0, 1004.0, 301, 500),
        ],
    }
    
    # AQI Categories with colors
    AQI_CATEGORIES: Dict[str, Tuple[int, int, str, str]] = {
        'Good': (0, 50, '#00E400', 'green'),
        'Moderate': (51, 100, '#FFFF00', 'yellow'),
        'Unhealthy for Sensitive Groups': (101, 150, '#FF7E00', 'orange'),
        'Unhealthy': (151, 200, '#FF0000', 'red'),
        'Very Unhealthy': (201, 300, '#8F3F97', 'purple'),
        'Hazardous': (301, 500, '#7E0023', 'maroon'),
    }
    
    # Globe Visualization Configuration
    GLOBE_LIBRARY = "pydeck"
    GLOBE_INITIAL_ZOOM = 2  # Global view
    GLOBE_MAX_ZOOM = 15  # City level
    GLOBE_CLUSTER_THRESHOLDS = {
        "low_zoom": (0, 5, 100),    # zoom 0-5: cluster 100+ stations
        "medium_zoom": (6, 10, 50),  # zoom 6-10: cluster 50+ stations
        "high_zoom": (11, 15, 10)    # zoom 11-15: cluster 10+ stations
    }
    GLOBE_MARKER_SIZE_SCALE = 100
    GLOBE_ANIMATION_DURATION_MS = 500
    
    # UI Configuration
    ACTIVITY_OPTIONS = [
        "Walking",
        "Jogging/Running",
        "Cycling",
        "Outdoor Study/Work",
        "Sports Practice",
        "Child Outdoor Play"
    ]
    
    HEALTH_SENSITIVITY_OPTIONS = [
        "None",
        "Allergies",
        "Asthma/Respiratory",
        "Child/Elderly",
        "Pregnant"
    ]
    
    @staticmethod
    def validate() -> None:
        """
        Validates all configuration values at startup.
        
        Raises:
            ConfigurationError: If configuration is invalid
        """
        errors = []
        
        # AWS credentials are optional - app will work without AI recommendations
        # Just log warnings instead of errors
        if not Config.AWS_REGION:
            print("⚠️  Warning: AWS_REGION not set. AI recommendations will use fallback mode.")
        
        if not Config.AWS_ACCESS_KEY_ID:
            print("⚠️  Warning: AWS_ACCESS_KEY_ID not set. AI recommendations will use fallback mode.")
        
        if not Config.AWS_SECRET_ACCESS_KEY:
            print("⚠️  Warning: AWS_SECRET_ACCESS_KEY not set. AI recommendations will use fallback mode.")
        
        # Note: OPENAQ_API_KEY is optional as OpenAQ has a free tier without key
        
        # Validate breakpoint table structure
        for pollutant, breakpoints in Config.AQI_BREAKPOINTS.items():
            if not breakpoints:
                errors.append(f"AQI breakpoints for {pollutant} cannot be empty")
            
            # Check that breakpoints are sorted and non-overlapping
            for i in range(len(breakpoints) - 1):
                current = breakpoints[i]
                next_bp = breakpoints[i + 1]
                if current[1] >= next_bp[0]:
                    errors.append(f"Overlapping breakpoints for {pollutant}: {current} and {next_bp}")
        
        # Validate AQI categories
        if len(Config.AQI_CATEGORIES) == 0:
            errors.append("AQI_CATEGORIES cannot be empty")
        
        if errors:
            raise ConfigurationError(
                f"Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            )
    
    @staticmethod
    def get_aqi_color(aqi: int) -> str:
        """
        Get the color code for a given AQI value.
        
        Args:
            aqi: AQI value (0-500)
            
        Returns:
            Hex color code
        """
        for category, (low, high, color, _) in Config.AQI_CATEGORIES.items():
            if low <= aqi <= high:
                return color
        
        # Default to hazardous color for values > 500
        return Config.AQI_CATEGORIES['Hazardous'][2]
    
    @staticmethod
    def get_aqi_category_name(aqi: int) -> str:
        """
        Get the category name for a given AQI value.
        
        Args:
            aqi: AQI value (0-500)
            
        Returns:
            Category name
        """
        for category, (low, high, _, __) in Config.AQI_CATEGORIES.items():
            if low <= aqi <= high:
                return category
        
        # Default to hazardous for values > 500
        return 'Hazardous'
