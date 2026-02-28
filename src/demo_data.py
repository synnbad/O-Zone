"""
Demo data for O-Zone MVP when OpenAQ API is unavailable.

Provides sample air quality data for testing without API access.
"""

from datetime import datetime, timedelta, UTC
from typing import Optional
from src.models import Location, Measurement, StationSummary, GeoBounds

# Sample locations with realistic AQI data
DEMO_LOCATIONS = {
    "san francisco": {
        "name": "San Francisco",
        "coordinates": (37.7749, -122.4194),
        "country": "US",
        "aqi": 45,
        "measurements": [
            ("PM2.5", 10.5, "μg/m³"),
            ("PM10", 20.0, "μg/m³"),
            ("O3", 45.0, "ppb"),
            ("NO2", 25.0, "ppb"),
        ]
    },
    "los angeles": {
        "name": "Los Angeles",
        "coordinates": (34.0522, -118.2437),
        "country": "US",
        "aqi": 85,
        "measurements": [
            ("PM2.5", 28.0, "μg/m³"),
            ("PM10", 45.0, "μg/m³"),
            ("O3", 65.0, "ppb"),
            ("NO2", 45.0, "ppb"),
            ("CO", 2.5, "ppm"),
        ]
    },
    "new york": {
        "name": "New York",
        "coordinates": (40.7128, -74.0060),
        "country": "US",
        "aqi": 55,
        "measurements": [
            ("PM2.5", 15.0, "μg/m³"),
            ("PM10", 30.0, "μg/m³"),
            ("O3", 50.0, "ppb"),
            ("NO2", 35.0, "ppb"),
        ]
    },
    "beijing": {
        "name": "Beijing",
        "coordinates": (39.9042, 116.4074),
        "country": "CN",
        "aqi": 165,
        "measurements": [
            ("PM2.5", 75.0, "μg/m³"),
            ("PM10", 120.0, "μg/m³"),
            ("O3", 80.0, "ppb"),
            ("NO2", 85.0, "ppb"),
            ("SO2", 45.0, "ppb"),
        ]
    },
    "delhi": {
        "name": "Delhi",
        "coordinates": (28.6139, 77.2090),
        "country": "IN",
        "aqi": 210,
        "measurements": [
            ("PM2.5", 110.0, "μg/m³"),
            ("PM10", 180.0, "μg/m³"),
            ("O3", 75.0, "ppb"),
            ("NO2", 95.0, "ppb"),
            ("SO2", 55.0, "ppb"),
            ("CO", 4.0, "ppm"),
        ]
    },
    "london": {
        "name": "London",
        "coordinates": (51.5074, -0.1278),
        "country": "GB",
        "aqi": 65,
        "measurements": [
            ("PM2.5", 18.0, "μg/m³"),
            ("PM10", 35.0, "μg/m³"),
            ("O3", 55.0, "ppb"),
            ("NO2", 40.0, "ppb"),
        ]
    },
    "tokyo": {
        "name": "Tokyo",
        "coordinates": (35.6762, 139.6503),
        "country": "JP",
        "aqi": 50,
        "measurements": [
            ("PM2.5", 12.0, "μg/m³"),
            ("PM10", 25.0, "μg/m³"),
            ("O3", 48.0, "ppb"),
            ("NO2", 30.0, "ppb"),
        ]
    },
    "seattle": {
        "name": "Seattle",
        "coordinates": (47.6062, -122.3321),
        "country": "US",
        "aqi": 40,
        "measurements": [
            ("PM2.5", 9.0, "μg/m³"),
            ("PM10", 18.0, "μg/m³"),
            ("O3", 42.0, "ppb"),
            ("NO2", 22.0, "ppb"),
        ]
    },
}


def get_demo_location(location_query: str) -> Location:
    """
    Get demo location data.
    
    Args:
        location_query: City name or coordinates
        
    Returns:
        Location object with demo data
    """
    # Normalize query
    query_lower = location_query.lower().strip()
    
    # Check if it's coordinates
    if ',' in query_lower:
        try:
            lat, lon = map(float, query_lower.split(','))
            # Find closest demo location
            min_dist = float('inf')
            closest = None
            for loc_data in DEMO_LOCATIONS.values():
                loc_lat, loc_lon = loc_data['coordinates']
                dist = ((lat - loc_lat)**2 + (lon - loc_lon)**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    closest = loc_data
            if closest:
                return Location(
                    name=closest['name'],
                    coordinates=closest['coordinates'],
                    country=closest['country'],
                    providers=['Demo Data']
                )
        except:
            pass
    
    # Search by name
    for key, loc_data in DEMO_LOCATIONS.items():
        if query_lower in key or key in query_lower:
            return Location(
                name=loc_data['name'],
                coordinates=loc_data['coordinates'],
                country=loc_data['country'],
                providers=['Demo Data']
            )
    
    # Return None if not found
    return None


def get_demo_measurements(location: Location) -> list[Measurement]:
    """
    Get demo measurements for a location.
    
    Args:
        location: Location object
        
    Returns:
        List of Measurement objects with demo data
    """
    # Find matching demo location
    loc_data = None
    for key, data in DEMO_LOCATIONS.items():
        if location.name.lower() == data['name'].lower():
            loc_data = data
            break
    
    if not loc_data:
        return []
    
    # Create measurements
    now = datetime.now(UTC)
    measurements = []
    
    for pollutant, value, unit in loc_data['measurements']:
        measurement = Measurement(
            pollutant=pollutant,
            value=value,
            unit=unit,
            timestamp=now,
            location=location
        )
        measurements.append(measurement)
    
    return measurements


def get_demo_historical_measurements(location: Location, hours: int = 24) -> dict:
    """
    Get demo historical measurements.
    
    Args:
        location: Location object
        hours: Number of hours of history
        
    Returns:
        Dict mapping pollutant names to lists of measurements
    """
    # Get current measurements
    current = get_demo_measurements(location)
    
    if not current:
        return {}
    
    # Generate historical data with some variation
    historical = {}
    now = datetime.now(UTC)
    
    for measurement in current:
        pollutant = measurement.pollutant
        base_value = measurement.value
        
        # Generate hourly data points
        measurements_list = []
        for i in range(hours):
            timestamp = now - timedelta(hours=hours - i)
            # Add some variation (±20%)
            import random
            variation = random.uniform(0.8, 1.2)
            value = base_value * variation
            
            hist_measurement = Measurement(
                pollutant=pollutant,
                value=value,
                unit=measurement.unit,
                timestamp=timestamp,
                location=location
            )
            measurements_list.append(hist_measurement)
        
        historical[pollutant] = measurements_list
    
    return historical


# Extended global stations for globe visualization
DEMO_GLOBAL_STATIONS = [
    # North America
    {
        "station_id": "sf-001",
        "name": "San Francisco Downtown",
        "coordinates": (37.7749, -122.4194),
        "country": "US",
        "aqi": 45
    },
    {
        "station_id": "la-001",
        "name": "Los Angeles Central",
        "coordinates": (34.0522, -118.2437),
        "country": "US",
        "aqi": 85
    },
    {
        "station_id": "ny-001",
        "name": "New York City",
        "coordinates": (40.7128, -74.0060),
        "country": "US",
        "aqi": 55
    },
    {
        "station_id": "sea-001",
        "name": "Seattle Downtown",
        "coordinates": (47.6062, -122.3321),
        "country": "US",
        "aqi": 40
    },
    {
        "station_id": "chi-001",
        "name": "Chicago Loop",
        "coordinates": (41.8781, -87.6298),
        "country": "US",
        "aqi": 60
    },
    {
        "station_id": "mex-001",
        "name": "Mexico City",
        "coordinates": (19.4326, -99.1332),
        "country": "MX",
        "aqi": 120
    },
    {
        "station_id": "tor-001",
        "name": "Toronto Downtown",
        "coordinates": (43.6532, -79.3832),
        "country": "CA",
        "aqi": 50
    },
    
    # Europe
    {
        "station_id": "lon-001",
        "name": "London Central",
        "coordinates": (51.5074, -0.1278),
        "country": "GB",
        "aqi": 65
    },
    {
        "station_id": "par-001",
        "name": "Paris Centre",
        "coordinates": (48.8566, 2.3522),
        "country": "FR",
        "aqi": 70
    },
    {
        "station_id": "ber-001",
        "name": "Berlin Mitte",
        "coordinates": (52.5200, 13.4050),
        "country": "DE",
        "aqi": 55
    },
    {
        "station_id": "mad-001",
        "name": "Madrid Centro",
        "coordinates": (40.4168, -3.7038),
        "country": "ES",
        "aqi": 75
    },
    {
        "station_id": "rom-001",
        "name": "Rome Centro",
        "coordinates": (41.9028, 12.4964),
        "country": "IT",
        "aqi": 80
    },
    {
        "station_id": "ams-001",
        "name": "Amsterdam Centrum",
        "coordinates": (52.3676, 4.9041),
        "country": "NL",
        "aqi": 45
    },
    {
        "station_id": "sto-001",
        "name": "Stockholm City",
        "coordinates": (59.3293, 18.0686),
        "country": "SE",
        "aqi": 35
    },
    
    # Asia
    {
        "station_id": "bei-001",
        "name": "Beijing Central",
        "coordinates": (39.9042, 116.4074),
        "country": "CN",
        "aqi": 165
    },
    {
        "station_id": "sha-001",
        "name": "Shanghai Pudong",
        "coordinates": (31.2304, 121.4737),
        "country": "CN",
        "aqi": 140
    },
    {
        "station_id": "del-001",
        "name": "Delhi Centre",
        "coordinates": (28.6139, 77.2090),
        "country": "IN",
        "aqi": 210
    },
    {
        "station_id": "mum-001",
        "name": "Mumbai Downtown",
        "coordinates": (19.0760, 72.8777),
        "country": "IN",
        "aqi": 180
    },
    {
        "station_id": "tok-001",
        "name": "Tokyo Shibuya",
        "coordinates": (35.6762, 139.6503),
        "country": "JP",
        "aqi": 50
    },
    {
        "station_id": "seo-001",
        "name": "Seoul Gangnam",
        "coordinates": (37.5665, 126.9780),
        "country": "KR",
        "aqi": 90
    },
    {
        "station_id": "sin-001",
        "name": "Singapore Central",
        "coordinates": (1.3521, 103.8198),
        "country": "SG",
        "aqi": 55
    },
    {
        "station_id": "ban-001",
        "name": "Bangkok Downtown",
        "coordinates": (13.7563, 100.5018),
        "country": "TH",
        "aqi": 110
    },
    {
        "station_id": "hk-001",
        "name": "Hong Kong Central",
        "coordinates": (22.3193, 114.1694),
        "country": "HK",
        "aqi": 75
    },
    
    # Middle East
    {
        "station_id": "dub-001",
        "name": "Dubai Marina",
        "coordinates": (25.2048, 55.2708),
        "country": "AE",
        "aqi": 95
    },
    {
        "station_id": "tel-001",
        "name": "Tel Aviv Center",
        "coordinates": (32.0853, 34.7818),
        "country": "IL",
        "aqi": 60
    },
    
    # South America
    {
        "station_id": "sao-001",
        "name": "São Paulo Centro",
        "coordinates": (-23.5505, -46.6333),
        "country": "BR",
        "aqi": 100
    },
    {
        "station_id": "rio-001",
        "name": "Rio de Janeiro",
        "coordinates": (-22.9068, -43.1729),
        "country": "BR",
        "aqi": 70
    },
    {
        "station_id": "bue-001",
        "name": "Buenos Aires Centro",
        "coordinates": (-34.6037, -58.3816),
        "country": "AR",
        "aqi": 65
    },
    {
        "station_id": "lim-001",
        "name": "Lima Centro",
        "coordinates": (-12.0464, -77.0428),
        "country": "PE",
        "aqi": 85
    },
    
    # Africa
    {
        "station_id": "cai-001",
        "name": "Cairo Downtown",
        "coordinates": (30.0444, 31.2357),
        "country": "EG",
        "aqi": 150
    },
    {
        "station_id": "joh-001",
        "name": "Johannesburg CBD",
        "coordinates": (-26.2041, 28.0473),
        "country": "ZA",
        "aqi": 80
    },
    {
        "station_id": "lag-001",
        "name": "Lagos Island",
        "coordinates": (6.5244, 3.3792),
        "country": "NG",
        "aqi": 130
    },
    {
        "station_id": "nai-001",
        "name": "Nairobi CBD",
        "coordinates": (-1.2921, 36.8219),
        "country": "KE",
        "aqi": 90
    },
    
    # Oceania
    {
        "station_id": "syd-001",
        "name": "Sydney CBD",
        "coordinates": (-33.8688, 151.2093),
        "country": "AU",
        "aqi": 40
    },
    {
        "station_id": "mel-001",
        "name": "Melbourne CBD",
        "coordinates": (-37.8136, 144.9631),
        "country": "AU",
        "aqi": 45
    },
    {
        "station_id": "auk-001",
        "name": "Auckland Central",
        "coordinates": (-36.8485, 174.7633),
        "country": "NZ",
        "aqi": 30
    },
]


def get_demo_global_stations(bounds: Optional[GeoBounds] = None) -> list[StationSummary]:
    """
    Get demo global stations data.
    
    Args:
        bounds: Optional geographic bounding box to filter stations
        
    Returns:
        List of StationSummary objects with demo data
    """
    from src.config import Config
    
    now = datetime.now(UTC)
    stations = []
    
    for station_data in DEMO_GLOBAL_STATIONS:
        lat, lon = station_data['coordinates']
        
        # Filter by bounds if provided
        if bounds:
            if not (bounds.south <= lat <= bounds.north):
                continue
            # Handle longitude wraparound
            if bounds.west <= bounds.east:
                # Normal case (doesn't cross antimeridian)
                if not (bounds.west <= lon <= bounds.east):
                    continue
            else:
                # Crosses antimeridian (e.g., 170 to -170)
                if not (lon >= bounds.west or lon <= bounds.east):
                    continue
        
        # Get AQI and calculate category/color
        aqi = station_data['aqi']
        category = Config.get_aqi_category_name(aqi)
        color = Config.get_aqi_color(aqi)
        
        station = StationSummary(
            station_id=station_data['station_id'],
            name=station_data['name'],
            coordinates=station_data['coordinates'],
            country=station_data['country'],
            current_aqi=aqi,
            aqi_category=category,
            aqi_color=color,
            last_updated=now
        )
        stations.append(station)
    
    return stations
