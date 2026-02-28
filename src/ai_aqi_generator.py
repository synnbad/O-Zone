"""
AI-powered air quality data generation using Claude via AWS Bedrock.

Generates realistic AQI estimates based on location characteristics,
time of day, season, and known pollution patterns.
"""

import json
from datetime import datetime, timedelta, UTC
from typing import Optional
import boto3

from src.config import Config
from src.models import Location, Measurement


def generate_aqi_data(location: Location) -> Optional[list[Measurement]]:
    """
    Generate realistic air quality measurements using AI.
    
    Uses Claude to analyze the location and generate contextually appropriate
    AQI values based on:
    - Geographic location and climate
    - Urban vs rural characteristics
    - Known pollution patterns for the region
    - Time of day and season
    - Industrial activity typical for the area
    
    Args:
        location: Location object with name, country, and coordinates
        
    Returns:
        List of Measurement objects for 6 pollutants, or None if generation fails
    """
    # Check if AWS is configured
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
        print("AWS not configured, cannot generate AI AQI data")
        return None
    
    try:
        # Create Bedrock client
        session_kwargs = {
            'aws_access_key_id': Config.AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': Config.AWS_SECRET_ACCESS_KEY,
            'region_name': Config.AWS_REGION
        }
        if Config.AWS_SESSION_TOKEN:
            session_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
        
        bedrock = boto3.client('bedrock-runtime', **session_kwargs)
        
        # Get current time info
        now = datetime.now(UTC)
        hour = now.hour
        month = now.month
        
        # Determine season
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall"
        
        # Construct prompt
        prompt = f"""You are an air quality expert. Generate realistic air quality measurements for the following location.

Location: {location.name}, {location.country}
Coordinates: {location.coordinates[0]:.4f}, {location.coordinates[1]:.4f}
Current time: {hour}:00 UTC
Season: {season}

Consider:
- Geographic and climate characteristics of this location
- Urban/industrial vs rural nature of the area
- Typical pollution sources (traffic, industry, agriculture, wildfires, etc.)
- Time of day (rush hour, night, etc.)
- Seasonal patterns (heating in winter, wildfires in summer, etc.)
- Regional air quality trends

Generate realistic pollutant concentrations in standard units:
- PM2.5 (μg/m³): Fine particulate matter
- PM10 (μg/m³): Coarse particulate matter  
- CO (ppm): Carbon monoxide
- NO2 (ppb): Nitrogen dioxide
- O3 (ppb): Ozone
- SO2 (ppb): Sulfur dioxide

Respond with ONLY a JSON object in this exact format:
{{
    "pm25": 12.5,
    "pm10": 25.0,
    "co": 0.5,
    "no2": 15.0,
    "o3": 45.0,
    "so2": 5.0,
    "reasoning": "Brief explanation of why these values are realistic for this location"
}}

Make the values realistic and contextually appropriate. Consider that:
- Clean rural areas: PM2.5 < 10, low NO2/CO
- Typical urban: PM2.5 10-35, moderate NO2/CO
- Polluted urban: PM2.5 35-150, high NO2/CO
- Heavily polluted: PM2.5 > 150, very high NO2/CO"""

        # Call Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.3,  # Some variation but mostly consistent
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId=Config.BEDROCK_MODEL_ID,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        content = response_body['content'][0]['text']
        
        # Extract JSON from response
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        data = json.loads(content)
        
        # Create Measurement objects
        measurements = []
        pollutant_map = {
            'pm25': 'PM2.5',
            'pm10': 'PM10',
            'co': 'CO',
            'no2': 'NO2',
            'o3': 'O3',
            'so2': 'SO2'
        }
        
        for key, pollutant_name in pollutant_map.items():
            if key in data:
                measurement = Measurement(
                    pollutant=pollutant_name,
                    value=data[key],
                    unit='μg/m³' if 'pm' in key else 'ppm' if key == 'co' else 'ppb',
                    timestamp=now,
                    location=location
                )
                measurements.append(measurement)
        
        print(f"✓ AI generated AQI data for {location.name}, {location.country}")
        print(f"  Reasoning: {data.get('reasoning', 'N/A')}")
        
        return measurements
    
    except Exception as e:
        print(f"AI AQI generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_historical_aqi_data(location: Location, hours: int = 24) -> Optional[dict[str, list[Measurement]]]:
    """
    Generate realistic historical air quality data using AI.
    
    Creates a time series with realistic variations and trends.
    
    Args:
        location: Location object
        hours: Number of hours of historical data (24 or 168)
        
    Returns:
        Dictionary mapping pollutant names to lists of Measurement objects
    """
    # Generate current measurements first
    current_measurements = generate_aqi_data(location)
    
    if not current_measurements:
        return None
    
    # Create historical data with realistic variations
    historical_data = {}
    now = datetime.now(UTC)
    
    for measurement in current_measurements:
        pollutant = measurement.pollutant
        base_value = measurement.value
        
        # Generate time series with variations
        time_series = []
        
        for i in range(hours):
            # Time going backwards
            timestamp = now - timedelta(hours=hours - i)
            hour_of_day = timestamp.hour
            
            # Add realistic variations
            # Daily cycle: higher during rush hours (7-9am, 5-7pm), lower at night
            if 7 <= hour_of_day <= 9 or 17 <= hour_of_day <= 19:
                time_factor = 1.2  # 20% higher during rush hour
            elif 0 <= hour_of_day <= 5:
                time_factor = 0.8  # 20% lower at night
            else:
                time_factor = 1.0
            
            # Add some random variation (±15%)
            import random
            random_factor = random.uniform(0.85, 1.15)
            
            # Calculate value
            value = base_value * time_factor * random_factor
            
            # Ensure non-negative
            value = max(0, value)
            
            time_series.append(Measurement(
                pollutant=pollutant,
                value=value,
                unit=measurement.unit,
                timestamp=timestamp,
                location=location
            ))
        
        historical_data[pollutant] = time_series
    
    return historical_data
