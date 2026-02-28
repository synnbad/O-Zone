"""
Data models for O-Zone MVP.

This module defines all dataclasses used throughout the application
for type safety and structured data handling.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import json


@dataclass
class Location:
    """Represents a geographic location with air quality monitoring."""
    name: str
    coordinates: tuple[float, float]  # (latitude, longitude)
    country: str
    providers: list[str]  # Available data providers
    
    def __post_init__(self):
        """Validate location data."""
        lat, lon = self.coordinates
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'name': self.name,
            'coordinates': list(self.coordinates),
            'country': self.country,
            'providers': self.providers
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Location':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            name=data['name'],
            coordinates=tuple(data['coordinates']),
            country=data['country'],
            providers=data['providers']
        )


@dataclass
class Measurement:
    """Represents a single air quality measurement."""
    pollutant: str  # PM2.5, PM10, CO, NO2, O3, SO2
    value: float
    unit: str
    timestamp: datetime
    location: Location
    
    def __post_init__(self):
        """Validate measurement data."""
        valid_pollutants = ['PM2.5', 'PM10', 'CO', 'NO2', 'O3', 'SO2']
        if self.pollutant not in valid_pollutants:
            raise ValueError(f"Invalid pollutant: {self.pollutant}. Must be one of {valid_pollutants}")
        if self.value < 0:
            raise ValueError(f"Invalid value: {self.value}. Must be non-negative.")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'pollutant': self.pollutant,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'location': json.loads(self.location.to_json())
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Measurement':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            pollutant=data['pollutant'],
            value=data['value'],
            unit=data['unit'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            location=Location.from_json(json.dumps(data['location']))
        )


@dataclass
class AQIResult:
    """Represents calculated AQI for a single pollutant."""
    pollutant: str
    concentration: float
    aqi: int  # 0-500
    category: str  # Good, Moderate, Unhealthy for Sensitive Groups, etc.
    color: str  # Hex color code for UI display
    
    def __post_init__(self):
        """Validate AQI result."""
        if not (0 <= self.aqi <= 500):
            raise ValueError(f"Invalid AQI: {self.aqi}. Must be between 0 and 500.")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AQIResult':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class OverallAQI:
    """Represents overall air quality assessment."""
    aqi: int  # Maximum of all pollutant AQIs
    category: str
    color: str
    dominant_pollutant: str  # Pollutant with highest AQI
    individual_results: list[AQIResult]
    timestamp: datetime
    location: Location
    
    def __post_init__(self):
        """Validate overall AQI."""
        if not (0 <= self.aqi <= 500):
            raise ValueError(f"Invalid AQI: {self.aqi}. Must be between 0 and 500.")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'aqi': self.aqi,
            'category': self.category,
            'color': self.color,
            'dominant_pollutant': self.dominant_pollutant,
            'individual_results': [json.loads(r.to_json()) for r in self.individual_results],
            'timestamp': self.timestamp.isoformat(),
            'location': json.loads(self.location.to_json())
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'OverallAQI':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            aqi=data['aqi'],
            category=data['category'],
            color=data['color'],
            dominant_pollutant=data['dominant_pollutant'],
            individual_results=[AQIResult.from_json(json.dumps(r)) for r in data['individual_results']],
            timestamp=datetime.fromisoformat(data['timestamp']),
            location=Location.from_json(json.dumps(data['location']))
        )



@dataclass
class TimeWindow:
    """Represents predicted optimal time period."""
    start_time: datetime
    end_time: datetime
    expected_aqi_range: tuple[int, int]  # (min, max)
    confidence: str  # High, Medium, Low
    
    def __post_init__(self):
        """Validate time window."""
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be before end_time")
        if self.confidence not in ['High', 'Medium', 'Low']:
            raise ValueError(f"Invalid confidence: {self.confidence}")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'expected_aqi_range': list(self.expected_aqi_range),
            'confidence': self.confidence
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TimeWindow':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            start_time=datetime.fromisoformat(data['start_time']),
            end_time=datetime.fromisoformat(data['end_time']),
            expected_aqi_range=tuple(data['expected_aqi_range']),
            confidence=data['confidence']
        )


@dataclass
class RecommendationResponse:
    """Represents AI-generated recommendation."""
    safety_assessment: str  # Safe, Moderate Risk, Unsafe
    recommendation_text: str
    precautions: list[str]
    time_windows: list[TimeWindow]
    reasoning: str
    
    def __post_init__(self):
        """Validate recommendation response."""
        valid_assessments = ['Safe', 'Moderate Risk', 'Unsafe']
        if self.safety_assessment not in valid_assessments:
            raise ValueError(
                f"Invalid safety_assessment: {self.safety_assessment}. "
                f"Must be one of {valid_assessments}"
            )
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'safety_assessment': self.safety_assessment,
            'recommendation_text': self.recommendation_text,
            'precautions': self.precautions,
            'time_windows': [json.loads(tw.to_json()) for tw in self.time_windows],
            'reasoning': self.reasoning
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RecommendationResponse':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            safety_assessment=data['safety_assessment'],
            recommendation_text=data['recommendation_text'],
            precautions=data['precautions'],
            time_windows=[TimeWindow.from_json(json.dumps(tw)) for tw in data['time_windows']],
            reasoning=data['reasoning']
        )


@dataclass
class GeoBounds:
    """Represents geographic bounding box for viewport queries."""
    north: float  # Maximum latitude
    south: float  # Minimum latitude
    east: float   # Maximum longitude
    west: float   # Minimum longitude
    
    def __post_init__(self):
        """Validate geographic bounds."""
        if not (-90 <= self.north <= 90):
            raise ValueError(f"Invalid north latitude: {self.north}. Must be between -90 and 90.")
        if not (-90 <= self.south <= 90):
            raise ValueError(f"Invalid south latitude: {self.south}. Must be between -90 and 90.")
        if not (-180 <= self.east <= 180):
            raise ValueError(f"Invalid east longitude: {self.east}. Must be between -180 and 180.")
        if not (-180 <= self.west <= 180):
            raise ValueError(f"Invalid west longitude: {self.west}. Must be between -180 and 180.")
        if self.north <= self.south:
            raise ValueError("north must be greater than south")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'north': self.north,
            'south': self.south,
            'east': self.east,
            'west': self.west
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'GeoBounds':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            north=data['north'],
            south=data['south'],
            east=data['east'],
            west=data['west']
        )


@dataclass
class StationSummary:
    """Represents air quality monitoring station for globe visualization."""
    station_id: str
    name: str
    coordinates: tuple[float, float]  # (latitude, longitude)
    country: str
    current_aqi: Optional[int] = None  # None if no recent data
    aqi_category: Optional[str] = None
    aqi_color: Optional[str] = None
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate station summary data."""
        lat, lon = self.coordinates
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
        if self.current_aqi is not None and not (0 <= self.current_aqi <= 500):
            raise ValueError(f"Invalid current_aqi: {self.current_aqi}. Must be between 0 and 500.")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'station_id': self.station_id,
            'name': self.name,
            'coordinates': list(self.coordinates),
            'country': self.country,
            'current_aqi': self.current_aqi,
            'aqi_category': self.aqi_category,
            'aqi_color': self.aqi_color,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'StationSummary':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            station_id=data['station_id'],
            name=data['name'],
            coordinates=tuple(data['coordinates']),
            country=data['country'],
            current_aqi=data.get('current_aqi'),
            aqi_category=data.get('aqi_category'),
            aqi_color=data.get('aqi_color'),
            last_updated=datetime.fromisoformat(data['last_updated']) if data.get('last_updated') else None
        )


@dataclass
class GlobeState:
    """Represents current state of globe visualization."""
    center_lat: float
    center_lon: float
    zoom_level: int  # 0 (global) to 15 (city level)
    rotation: float = 0.0  # Degrees for 3D globe
    selected_station: Optional[str] = None  # Station ID if selected
    
    def __post_init__(self):
        """Validate globe state."""
        if not (-90 <= self.center_lat <= 90):
            raise ValueError(f"Invalid center_lat: {self.center_lat}. Must be between -90 and 90.")
        if not (-180 <= self.center_lon <= 180):
            raise ValueError(f"Invalid center_lon: {self.center_lon}. Must be between -180 and 180.")
        if not (0 <= self.zoom_level <= 15):
            raise ValueError(f"Invalid zoom_level: {self.zoom_level}. Must be 0-15.")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'center_lat': self.center_lat,
            'center_lon': self.center_lon,
            'zoom_level': self.zoom_level,
            'rotation': self.rotation,
            'selected_station': self.selected_station
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'GlobeState':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            center_lat=data['center_lat'],
            center_lon=data['center_lon'],
            zoom_level=data['zoom_level'],
            rotation=data.get('rotation', 0.0),
            selected_station=data.get('selected_station')
        )


@dataclass
class MarkerCluster:
    """Represents clustered group of stations at lower zoom levels."""
    center_coordinates: tuple[float, float]
    station_count: int
    avg_aqi: int
    aqi_color: str
    stations: list[StationSummary]
    
    def __post_init__(self):
        """Validate marker cluster."""
        lat, lon = self.center_coordinates
        if not (-90 <= lat <= 90):
            raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
        if not (-180 <= lon <= 180):
            raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
        if self.station_count != len(self.stations):
            raise ValueError(
                f"station_count ({self.station_count}) must match "
                f"length of stations list ({len(self.stations)})"
            )
        if not (0 <= self.avg_aqi <= 500):
            raise ValueError(f"Invalid avg_aqi: {self.avg_aqi}. Must be between 0 and 500.")
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        data = {
            'center_coordinates': list(self.center_coordinates),
            'station_count': self.station_count,
            'avg_aqi': self.avg_aqi,
            'aqi_color': self.aqi_color,
            'stations': [json.loads(s.to_json()) for s in self.stations]
        }
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MarkerCluster':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            center_coordinates=tuple(data['center_coordinates']),
            station_count=data['station_count'],
            avg_aqi=data['avg_aqi'],
            aqi_color=data['aqi_color'],
            stations=[StationSummary.from_json(json.dumps(s)) for s in data['stations']]
        )
