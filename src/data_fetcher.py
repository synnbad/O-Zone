"""
Data Fetcher module for O-Zone MVP.

This module handles all interactions with the OpenAQ API including
location resolution, current measurements, historical data, and global stations.

Falls back to demo data when API is unavailable.
"""

import httpx
from datetime import datetime, timedelta, UTC
from typing import Optional
import time
import json

from src.config import Config
from src.models import Location, Measurement, GeoBounds, StationSummary
from src import demo_data


# In-memory cache with TTL
_cache = {}
_cache_timestamps = {}

# Track if API is available
_api_available = None


def _is_cache_valid(key: str, ttl_seconds: int) -> bool:
    """Check if cached data is still valid."""
    if key not in _cache or key not in _cache_timestamps:
        return False
    
    age = (datetime.now(UTC) - _cache_timestamps[key]).total_seconds()
    return age < ttl_seconds


def _get_from_cache(key: str, ttl_seconds: int) -> Optional[any]:
    """Get data from cache if valid."""
    if _is_cache_valid(key, ttl_seconds):
        return _cache[key]
    return None


def _set_cache(key: str, value: any) -> None:
    """Store data in cache with current timestamp."""
    _cache[key] = value
    _cache_timestamps[key] = datetime.now(UTC)


def _call_openaq_api(endpoint: str, params: dict, retry: bool = True) -> dict:
    """
    Call OpenAQ API with authentication and error handling.
    
    Args:
        endpoint: API endpoint path (e.g., '/locations')
        params: Query parameters
        retry: Whether to retry on failure
        
    Returns:
        JSON response as dict
        
    Raises:
        Exception: If API call fails after retry
    """
    url = f"{Config.OPENAQ_API_BASE_URL}{endpoint}"
    headers = {
        "Accept": "application/json"
    }
    
    # Add API key if configured (v2 works without key but has rate limits)
    if Config.OPENAQ_API_KEY:
        headers["X-API-Key"] = Config.OPENAQ_API_KEY
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
    
    except (httpx.HTTPError, httpx.TimeoutException) as e:
        if retry:
            # Retry once after 1 second delay
            print(f"OpenAQ API error, retrying: {e}")
            time.sleep(1)
            return _call_openaq_api(endpoint, params, retry=False)
        else:
            raise Exception(
                f"OpenAQ API request failed: {str(e)}. "
                f"Please check your internet connection and try again."
            )


def get_location(location_query: str) -> Optional[Location]:
    """
    Resolve location query to Location object using hybrid approach:
    1. Try geocoding API (Nominatim/OpenStreetMap) for accurate coordinates
    2. Fall back to AI (Claude) for fuzzy matching and suggestions
    3. Fall back to demo data as last resort
    
    Supports:
    - City name (e.g., "San Francisco")
    - Coordinates (e.g., "37.7749,-122.4194")
    - Fuzzy names (e.g., "SF", "New York City")
    
    Args:
        location_query: User's location input
        
    Returns:
        Location object if found, None otherwise
    """
    global _api_available
    
    # Check cache first
    cache_key = f"location:{location_query}"
    cached = _get_from_cache(cache_key, Config.CACHE_TTL_SECONDS)
    if cached is not None:
        return cached
    
    # Try OpenAQ API first (if not known to be unavailable)
    if _api_available is not False:
        try:
            location = _get_location_from_api(location_query)
            if location:
                _api_available = True
                _set_cache(cache_key, location)
                return location
        except Exception as e:
            print(f"OpenAQ API unavailable: {e}")
            _api_available = False
    
    # Try geocoding API (Nominatim/OpenStreetMap) - free and accurate
    try:
        location = _get_location_from_geocoding(location_query)
        if location:
            _set_cache(cache_key, location)
            return location
    except Exception as e:
        print(f"Geocoding API error: {e}")
    
    # Try AI-powered location resolution (Claude via Bedrock)
    try:
        location = _get_location_from_ai(location_query)
        if location:
            _set_cache(cache_key, location)
            return location
    except Exception as e:
        print(f"AI location resolution error: {e}")
    
    # Fall back to demo data
    print(f"ℹ️  Using demo data for location: {location_query}")
    location = demo_data.get_demo_location(location_query)
    if location:
        _set_cache(cache_key, location)
    return location


def _get_location_from_api(location_query: str) -> Optional[Location]:
    """Try to get location from OpenAQ API v3."""
    try:
        # Try to parse as coordinates
        if ',' in location_query:
            try:
                lat_str, lon_str = location_query.split(',')
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
                
                # Search for nearest location (v3 API)
                params = {
                    'coordinates': f"{lat},{lon}",
                    'radius': 50000,  # 50km radius
                    'limit': 1
                }
                response = _call_openaq_api('/locations', params)
                
                if response.get('results'):
                    result = response['results'][0]
                    return _parse_location_from_api_v3(result)
                
            except ValueError:
                pass  # Not valid coordinates, try as city name
        
        # Search by locality/city name (v3 API doesn't have direct city search)
        # We'll use geocoding first, then search OpenAQ by coordinates
        return None
    
    except Exception as e:
        raise Exception(f"API error: {e}")


def _get_location_from_geocoding(location_query: str) -> Optional[Location]:
    """
    Get location using Nominatim geocoding API (OpenStreetMap).
    Free, accurate, and reliable for location coordinates.
    """
    import time
    
    # Try to parse as coordinates first
    if ',' in location_query:
        try:
            lat_str, lon_str = location_query.split(',')
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            
            # Validate coordinates
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                # Reverse geocode to get location name
                url = "https://nominatim.openstreetmap.org/reverse"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'format': 'json',
                    'addressdetails': 1
                }
                headers = {
                    'User-Agent': 'O-Zone-AQI-App/1.0'
                }
                
                response = httpx.get(url, params=params, headers=headers, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                if data:
                    address = data.get('address', {})
                    city = (address.get('city') or 
                           address.get('town') or 
                           address.get('village') or 
                           address.get('county') or
                           'Unknown')
                    country = address.get('country', 'Unknown')
                    
                    return Location(
                        name=city,
                        country=country,
                        coordinates=(lat, lon),
                        providers=['Nominatim Geocoding']
                    )
        except (ValueError, httpx.HTTPError):
            pass
    
    # Search by location name
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': location_query,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1
    }
    headers = {
        'User-Agent': 'O-Zone-AQI-App/1.0'
    }
    
    # Nominatim requires 1 second between requests
    time.sleep(1)
    
    response = httpx.get(url, params=params, headers=headers, timeout=10.0)
    response.raise_for_status()
    results = response.json()
    
    if results:
        result = results[0]
        lat = float(result['lat'])
        lon = float(result['lon'])
        
        address = result.get('address', {})
        city = (address.get('city') or 
               address.get('town') or 
               address.get('village') or 
               address.get('county') or
               result.get('display_name', 'Unknown').split(',')[0])
        country = address.get('country', 'Unknown')
        
        return Location(
            name=city,
            country=country,
            coordinates=(lat, lon),
            providers=['Nominatim Geocoding']
        )
    
    return None


def _get_location_from_ai(location_query: str) -> Optional[Location]:
    """
    Use AI (Claude via Bedrock) to resolve location query.
    Handles fuzzy matching, abbreviations, and provides intelligent suggestions.
    """
    from src.config import Config
    import boto3
    import json
    
    # Check if AWS is configured
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
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
        
        # Construct prompt for location resolution
        prompt = f"""You are a geographic location resolver. Given a location query, provide the exact coordinates and standardized name.

Location query: "{location_query}"

Respond with ONLY a JSON object in this exact format:
{{
    "name": "City Name",
    "country": "Country Name",
    "latitude": 00.0000,
    "longitude": 00.0000,
    "confidence": "high|medium|low"
}}

Rules:
- Use the most commonly known name for the city
- Provide precise coordinates (4 decimal places)
- Set confidence based on query clarity
- If the location is ambiguous or unknown, set confidence to "low"

Examples:
- "SF" → San Francisco, USA (37.7749, -122.4194)
- "NYC" → New York City, USA (40.7128, -74.0060)
- "Paris" → Paris, France (48.8566, 2.3522)"""

        # Call Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "temperature": 0.1,  # Low temperature for factual accuracy
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
        # Claude might wrap it in markdown code blocks
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        data = json.loads(content)
        
        # Validate confidence
        if data.get('confidence') == 'low':
            print(f"AI location resolution has low confidence for: {location_query}")
            return None
        
        # Create Location object
        location = Location(
            name=data['name'],
            country=data['country'],
            coordinates=(data['latitude'], data['longitude']),
            providers=['AI (Claude 3.5 Sonnet)']
        )
        
        print(f"✓ AI resolved '{location_query}' to {location.name}, {location.country}")
        return location
    
    except Exception as e:
        print(f"AI location resolution failed: {e}")
        return None


def _parse_location_from_api_v3(api_result: dict) -> Location:
    """Parse OpenAQ v3 API location result into Location object."""
    # v3 API format
    name = api_result.get('name', api_result.get('locality', 'Unknown'))
    
    coords = api_result.get('coordinates', {})
    lat = coords.get('latitude', 0.0)
    lon = coords.get('longitude', 0.0)
    
    country_data = api_result.get('country', {})
    country = country_data.get('name', 'Unknown') if isinstance(country_data, dict) else 'Unknown'
    
    # v3 API has provider information
    provider_data = api_result.get('provider', {})
    if isinstance(provider_data, dict):
        providers = [provider_data.get('name', 'OpenAQ')]
    else:
        providers = ['OpenAQ']
    
    return Location(
        name=name,
        coordinates=(lat, lon),
        country=country,
        providers=providers
    )


def get_current_measurements(location: Location) -> list[Measurement]:
    """
    Retrieve current measurements for all pollutants at location.
    
    Tries multiple sources in order:
    1. OpenAQ API (if available)
    2. AI-generated data (using Claude via Bedrock)
    3. Demo data (fallback)
    
    Args:
        location: Location object
        
    Returns:
        List of Measurement objects (may be empty if no recent data)
    """
    global _api_available
    
    # Check cache first
    cache_key = f"measurements:{location.name}:{location.coordinates}"
    cached = _get_from_cache(cache_key, Config.CACHE_TTL_SECONDS)
    if cached is not None:
        return cached
    
    # Try API first (if not known to be unavailable)
    if _api_available is not False:
        try:
            measurements = _get_measurements_from_api(location)
            if measurements:
                _api_available = True
                _set_cache(cache_key, measurements)
                return measurements
        except Exception as e:
            print(f"OpenAQ API unavailable: {e}")
            _api_available = False
    
    # Try AI-generated data
    try:
        from src.ai_aqi_generator import generate_aqi_data
        measurements = generate_aqi_data(location)
        if measurements:
            print(f"✓ Using AI-generated AQI data for {location.name}")
            _set_cache(cache_key, measurements)
            return measurements
    except Exception as e:
        print(f"AI AQI generation failed: {e}")
    
    # Fall back to demo data
    print(f"ℹ️  Using demo data for measurements: {location.name}")
    measurements = demo_data.get_demo_measurements(location)
    _set_cache(cache_key, measurements)
    return measurements


def _get_measurements_from_api(location: Location) -> list[Measurement]:
    """Try to get measurements from OpenAQ API v3."""
    try:
        # First, find the location ID by coordinates
        lat, lon = location.coordinates
        params = {
            'coordinates': f"{lat},{lon}",
            'radius': 10000,  # 10km radius
            'limit': 1
        }
        
        response = _call_openaq_api('/locations', params)
        
        if not response.get('results'):
            return []
        
        location_id = response['results'][0].get('id')
        if not location_id:
            return []
        
        # Get latest measurements for this location
        latest_response = _call_openaq_api(f'/locations/{location_id}/latest', {})
        
        measurements = []
        if latest_response.get('results'):
            # Get sensor details to map sensor IDs to parameters
            location_details = response['results'][0]
            sensors_map = {}
            for sensor in location_details.get('sensors', []):
                sensor_id = sensor.get('id')
                param_data = sensor.get('parameter', {})
                param_name = param_data.get('name', '').lower()
                sensors_map[sensor_id] = param_name
            
            for result in latest_response['results']:
                try:
                    sensor_id = result.get('sensorsId')
                    param_name = sensors_map.get(sensor_id, '').lower()
                    
                    measurement = _parse_measurement_from_api_v3(result, location, param_name)
                    if measurement:
                        measurements.append(measurement)
                except Exception as e:
                    print(f"Error parsing measurement: {e}")
                    continue
        
        return measurements
    
    except Exception as e:
        raise Exception(f"API error: {e}")


def _parse_measurement_from_api_v3(api_result: dict, location: Location, param_name: str) -> Optional[Measurement]:
    """Parse OpenAQ v3 API measurement result into Measurement object."""
    # Map OpenAQ parameter names to our standard names
    pollutant_map = {
        'pm25': 'PM2.5',
        'pm10': 'PM10',
        'co': 'CO',
        'no2': 'NO2',
        'o3': 'O3',
        'so2': 'SO2'
    }
    
    pollutant = pollutant_map.get(param_name)
    if not pollutant:
        return None  # Skip unsupported pollutants
    
    # Get value
    value = api_result.get('value')
    if value is None:
        return None
    
    # Determine unit based on pollutant (v3 API uses standard units)
    if pollutant in ['PM2.5', 'PM10']:
        unit = 'μg/m³'
    elif pollutant == 'CO':
        unit = 'ppm'
    else:  # NO2, O3, SO2
        unit = 'ppm'  # v3 uses ppm for gases
    
    # Convert units to our standard format
    value, unit = _normalize_units(pollutant, value, unit)
    
    # Get timestamp
    datetime_data = api_result.get('datetime', {})
    timestamp_str = datetime_data.get('utc') if isinstance(datetime_data, dict) else None
    
    if timestamp_str:
        timestamp_str = timestamp_str.replace('Z', '+00:00')
        timestamp = datetime.fromisoformat(timestamp_str)
    else:
        timestamp = datetime.now(UTC)
    
    return Measurement(
        pollutant=pollutant,
        value=value,
        unit=unit,
        timestamp=timestamp,
        location=location
    )


def _normalize_units(pollutant: str, value: float, unit: str) -> tuple[float, str]:
    """
    Normalize units to standard format.
    
    Standard units:
    - PM2.5, PM10: μg/m³
    - CO: ppm
    - NO2, O3, SO2: ppb
    
    Args:
        pollutant: Pollutant name
        value: Concentration value
        unit: Current unit
        
    Returns:
        Tuple of (normalized_value, normalized_unit)
    """
    unit_lower = unit.lower()
    
    # Particulate matter conversions
    if pollutant in ['PM2.5', 'PM10']:
        if 'mg/m' in unit_lower:
            # Convert mg/m³ to μg/m³
            return value * 1000, 'μg/m³'
        return value, 'μg/m³'
    
    # Gas conversions
    if pollutant == 'CO':
        if 'ppb' in unit_lower:
            # Convert ppb to ppm
            return value / 1000, 'ppm'
        return value, 'ppm'
    
    # NO2, O3, SO2 use ppb
    if pollutant in ['NO2', 'O3', 'SO2']:
        if 'ppm' in unit_lower:
            # Convert ppm to ppb
            return value * 1000, 'ppb'
        return value, 'ppb'
    
    return value, unit


def get_historical_measurements(
    location: Location,
    hours: int = 24
) -> dict[str, list[Measurement]]:
    """
    Retrieve historical measurements for time-series analysis.
    
    Tries multiple sources in order:
    1. OpenAQ API (if available)
    2. AI-generated data (using Claude via Bedrock)
    3. Demo data (fallback)
    
    Args:
        location: Location object
        hours: Number of hours to retrieve (24 or 168 for 7 days)
        
    Returns:
        Dict mapping pollutant names to lists of Measurement objects
    """
    global _api_available
    
    # Check cache first
    cache_key = f"historical:{location.name}:{location.coordinates}:{hours}"
    cached = _get_from_cache(cache_key, Config.CACHE_TTL_SECONDS)
    if cached is not None:
        return cached
    
    # Try API first (if not known to be unavailable)
    if _api_available is not False:
        try:
            historical = _get_historical_from_api(location, hours)
            if historical:
                _api_available = True
                _set_cache(cache_key, historical)
                return historical
        except Exception as e:
            print(f"OpenAQ API unavailable: {e}")
            _api_available = False
    
    # Try AI-generated data
    try:
        from src.ai_aqi_generator import generate_historical_aqi_data
        historical = generate_historical_aqi_data(location, hours)
        if historical:
            print(f"✓ Using AI-generated historical data for {location.name}")
            _set_cache(cache_key, historical)
            return historical
    except Exception as e:
        print(f"AI historical generation failed: {e}")
    
    # Fall back to demo data
    print(f"ℹ️  Using demo data for historical: {location.name}")
    historical = demo_data.get_demo_historical_measurements(location, hours)
    _set_cache(cache_key, historical)
    return historical


def _get_historical_from_api(location: Location, hours: int) -> dict[str, list[Measurement]]:
    """Try to get historical data from OpenAQ API v3."""
    try:
        # v3 API doesn't have a direct historical measurements endpoint like v2
        # We'll use the measurements endpoint with date filters
        # For now, return empty dict and rely on AI/demo data for historical
        # This would require implementing the /measurements endpoint with proper date filtering
        return {}
    
    except Exception as e:
        raise Exception(f"API error: {e}")


def get_global_stations(bounds: Optional[GeoBounds] = None) -> list[StationSummary]:
    """
    Retrieve list of all monitoring stations globally or within specified bounds.
    
    Returns station metadata including location, coordinates, and latest AQI.
    Uses aggressive caching (1 hour TTL) due to data volume.
    Falls back to demo data if API is unavailable.
    
    Args:
        bounds: Optional geographic bounding box to filter stations
        
    Returns:
        List of StationSummary objects
    """
    global _api_available
    
    # Create cache key based on bounds
    if bounds:
        cache_key = f"global_stations:{bounds.north}:{bounds.south}:{bounds.east}:{bounds.west}"
    else:
        cache_key = "global_stations:all"
    
    # Check cache first (1 hour TTL)
    cached = _get_from_cache(cache_key, Config.GLOBE_CACHE_TTL_SECONDS)
    if cached is not None:
        return cached
    
    # Try API first (if not known to be unavailable)
    if _api_available is not False:
        try:
            stations = _get_global_stations_from_api(bounds)
            if stations:
                _api_available = True
                _set_cache(cache_key, stations)
                return stations
        except Exception as e:
            print(f"OpenAQ API unavailable: {e}")
            _api_available = False
    
    # Fall back to demo data
    print(f"ℹ️  Using demo data for global stations")
    stations = demo_data.get_demo_global_stations(bounds)
    _set_cache(cache_key, stations)
    return stations


def _get_global_stations_from_api(bounds: Optional[GeoBounds] = None) -> list[StationSummary]:
    """Try to get global stations from OpenAQ API v3."""
    try:
        # Build query parameters
        params = {
            'limit': 1000
        }
        
        # Add bounding box if provided
        if bounds:
            # OpenAQ v3 uses bbox parameter: minX,minY,maxX,maxY (lon,lat,lon,lat)
            params['bbox'] = f"{bounds.west},{bounds.south},{bounds.east},{bounds.north}"
        
        response = _call_openaq_api('/locations', params)
        
        stations = []
        if response.get('results'):
            for result in response['results']:
                try:
                    station = _parse_station_from_api_v3(result)
                    if station:
                        stations.append(station)
                except Exception as e:
                    print(f"Error parsing station: {e}")
                    continue
        
        return stations
    
    except Exception as e:
        raise Exception(f"API error: {e}")


def _parse_station_from_api_v3(api_result: dict) -> Optional[StationSummary]:
    """Parse OpenAQ v3 API location result into StationSummary object."""
    try:
        # Get station ID
        station_id = str(api_result.get('id', 'unknown'))
        
        # Get name
        name = api_result.get('name', api_result.get('locality', 'Unknown Station'))
        
        # Get coordinates
        coords = api_result.get('coordinates', {})
        lat = coords.get('latitude')
        lon = coords.get('longitude')
        
        if lat is None or lon is None:
            return None  # Skip stations without coordinates
        
        # Get country
        country_data = api_result.get('country', {})
        country = country_data.get('name', 'Unknown') if isinstance(country_data, dict) else 'Unknown'
        
        # Get latest measurement data if available
        current_aqi = None
        aqi_category = None
        aqi_color = None
        last_updated = None
        
        # Check for datetimeLast timestamp
        datetime_last = api_result.get('datetimeLast', {})
        if isinstance(datetime_last, dict):
            last_updated_str = datetime_last.get('utc')
            if last_updated_str:
                try:
                    last_updated_str = last_updated_str.replace('Z', '+00:00')
                    last_updated = datetime.fromisoformat(last_updated_str)
                except:
                    pass
        
        # Note: We don't calculate AQI here as it would require fetching measurements
        # The globe visualizer will calculate AQI when needed
        
        return StationSummary(
            station_id=station_id,
            name=name,
            coordinates=(lat, lon),
            country=country,
            current_aqi=current_aqi,
            aqi_category=aqi_category,
            aqi_color=aqi_color,
            last_updated=last_updated
        )
    
    except Exception as e:
        print(f"Error parsing station: {e}")
        return None
