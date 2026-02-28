"""
Chatbot Configuration Module

Centralizes chatbot-specific configuration including session settings,
activity and health options, response templates, and vocabulary levels.
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class ChatbotConfig:
    """Configuration class for O-Zone Chatbot"""
    
    # Session Configuration
    SESSION_TTL_MINUTES = 30
    MAX_CONVERSATION_HISTORY = 50  # messages
    
    # Activity Options
    ACTIVITY_OPTIONS = [
        "Walking",
        "Jogging/Running",
        "Cycling",
        "Outdoor Study/Work",
        "Sports Practice",
        "Child Outdoor Play"
    ]
    
    # Health Sensitivity Options
    HEALTH_SENSITIVITY_OPTIONS = [
        "None",
        "Allergies",
        "Asthma/Respiratory",
        "Child/Elderly",
        "Pregnant"
    ]
    
    # Response Templates
    GREETING_TEMPLATE = """Hello! I'm the O-Zone Air Quality Assistant. I can help you make informed decisions about outdoor activities based on current air quality conditions.

I'll guide you through a few quick questions to provide personalized recommendations.

Let's start with your location. Where are you planning your outdoor activity?"""
    
    LOCATION_CONFIRMATION_TEMPLATE = """Great! I found {location_name} in {country}.

Now, what outdoor activity are you planning?
{activity_options}"""
    
    LOCATION_NOT_FOUND_MESSAGE = """I couldn't find air quality data for "{location}". This could mean:
- The location name might be misspelled
- There are no monitoring stations in that area

{suggestions}

Please try another location."""
    
    NO_DATA_AVAILABLE_MESSAGE = """I found your location, but there's no recent air quality data available. This sometimes happens with monitoring stations that update infrequently.

You could try:
- A nearby larger city
- Checking back in a few hours"""
    
    BEDROCK_UNAVAILABLE_MESSAGE = """I'm having trouble connecting to my AI recommendation engine right now, but I can still help you with basic guidance based on current air quality levels."""
    
    # Adaptive Communication Parameters
    VOCABULARY_LEVELS = {
        "basic": {
            "aqi": "air quality number",
            "pollutant": "air pollution",
            "concentration": "amount",
            "particulate_matter": "tiny particles in the air"
        },
        "technical": {
            "include_units": True,
            "include_pollutant_names": True,
            "include_concentrations": True
        }
    }
    
    @staticmethod
    def validate() -> None:
        """
        Validates configuration at startup.
        
        Raises:
            ValueError: If required configuration is missing or invalid
        """
        errors = []
        
        # Validate activity options
        if not ChatbotConfig.ACTIVITY_OPTIONS:
            errors.append("ACTIVITY_OPTIONS cannot be empty")
        
        # Validate health sensitivity options
        if not ChatbotConfig.HEALTH_SENSITIVITY_OPTIONS:
            errors.append("HEALTH_SENSITIVITY_OPTIONS cannot be empty")
        
        # Validate session TTL
        if ChatbotConfig.SESSION_TTL_MINUTES <= 0:
            errors.append("SESSION_TTL_MINUTES must be positive")
        
        # Check AWS configuration (warnings only, not errors)
        # The app can work without AWS credentials using fallback recommendations
        aws_region = os.getenv("AWS_REGION")
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if not aws_region:
            logger.warning("AWS_REGION not set. AI recommendations will use fallback mode.")
        
        if not aws_access_key:
            logger.warning("AWS_ACCESS_KEY_ID not set. AI recommendations will use fallback mode.")
        
        if not aws_secret_key:
            logger.warning("AWS_SECRET_ACCESS_KEY not set. AI recommendations will use fallback mode.")
        
        # OpenAQ API key is optional (free tier works without key)
        if not os.getenv("OPENAQ_API_KEY"):
            logger.info("OPENAQ_API_KEY not set. Using free tier access.")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Chatbot configuration validated successfully")
    
    @staticmethod
    def get_activity_options_text() -> str:
        """Returns formatted activity options for display"""
        return "\n".join(f"  {i+1}. {activity}" 
                        for i, activity in enumerate(ChatbotConfig.ACTIVITY_OPTIONS))
    
    @staticmethod
    def get_health_options_text() -> str:
        """Returns formatted health sensitivity options for display"""
        return "\n".join(f"  {i+1}. {health}" 
                        for i, health in enumerate(ChatbotConfig.HEALTH_SENSITIVITY_OPTIONS))
