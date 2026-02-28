"""
Unit tests for globe-specific data models.
"""

import pytest
from datetime import datetime
from src.models import GeoBounds, StationSummary, GlobeState, MarkerCluster


class TestGeoBounds:
    """Tests for GeoBounds model."""
    
    def test_valid_bounds(self):
        """Test creating valid geographic bounds."""
        bounds = GeoBounds(north=45.0, south=30.0, east=-100.0, west=-120.0)
        assert bounds.north == 45.0
        assert bounds.south == 30.0
        assert bounds.east == -100.0
        assert bounds.west == -120.0
    
    def test_invalid_north_latitude(self):
        """Test that north latitude must be in valid range."""
        with pytest.raises(ValueError, match="Invalid north latitude"):
            GeoBounds(north=95.0, south=30.0, east=-100.0, west=-120.0)
    
    def test_invalid_south_latitude(self):
        """Test that south latitude must be in valid range."""
        with pytest.raises(ValueError, match="Invalid south latitude"):
            GeoBounds(north=45.0, south=-95.0, east=-100.0, west=-120.0)
    
    def test_invalid_east_longitude(self):
        """Test that east longitude must be in valid range."""
        with pytest.raises(ValueError, match="Invalid east longitude"):
            GeoBounds(north=45.0, south=30.0, east=185.0, west=-120.0)
    
    def test_invalid_west_longitude(self):
        """Test that west longitude must be in valid range."""
        with pytest.raises(ValueError, match="Invalid west longitude"):
            GeoBounds(north=45.0, south=30.0, east=-100.0, west=-185.0)
    
    def test_north_must_be_greater_than_south(self):
        """Test that north must be greater than south."""
        with pytest.raises(ValueError, match="north must be greater than south"):
            GeoBounds(north=30.0, south=45.0, east=-100.0, west=-120.0)
    
    def test_serialization_roundtrip(self):
        """Test JSON serialization and deserialization."""
        bounds = GeoBounds(north=45.0, south=30.0, east=-100.0, west=-120.0)
        json_str = bounds.to_json()
        deserialized = GeoBounds.from_json(json_str)
        assert deserialized.north == bounds.north
        assert deserialized.south == bounds.south
        assert deserialized.east == bounds.east
        assert deserialized.west == bounds.west


class TestStationSummary:
    """Tests for StationSummary model."""
    
    def test_valid_station(self):
        """Test creating valid station summary."""
        station = StationSummary(
            station_id="test-123",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=datetime(2024, 1, 1, 12, 0, 0)
        )
        assert station.station_id == "test-123"
        assert station.current_aqi == 50
    
    def test_station_without_aqi_data(self):
        """Test creating station with no recent AQI data."""
        station = StationSummary(
            station_id="test-123",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US"
        )
        assert station.current_aqi is None
        assert station.aqi_category is None
    
    def test_invalid_latitude(self):
        """Test that latitude must be in valid range."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            StationSummary(
                station_id="test-123",
                name="Test Station",
                coordinates=(95.0, -122.4194),
                country="US"
            )
    
    def test_invalid_longitude(self):
        """Test that longitude must be in valid range."""
        with pytest.raises(ValueError, match="Invalid longitude"):
            StationSummary(
                station_id="test-123",
                name="Test Station",
                coordinates=(37.7749, -185.0),
                country="US"
            )
    
    def test_invalid_aqi(self):
        """Test that AQI must be in valid range."""
        with pytest.raises(ValueError, match="Invalid current_aqi"):
            StationSummary(
                station_id="test-123",
                name="Test Station",
                coordinates=(37.7749, -122.4194),
                country="US",
                current_aqi=600
            )
    
    def test_serialization_roundtrip(self):
        """Test JSON serialization and deserialization."""
        station = StationSummary(
            station_id="test-123",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=datetime(2024, 1, 1, 12, 0, 0)
        )
        json_str = station.to_json()
        deserialized = StationSummary.from_json(json_str)
        assert deserialized.station_id == station.station_id
        assert deserialized.name == station.name
        assert deserialized.coordinates == station.coordinates
        assert deserialized.current_aqi == station.current_aqi


class TestGlobeState:
    """Tests for GlobeState model."""
    
    def test_valid_globe_state(self):
        """Test creating valid globe state."""
        state = GlobeState(
            center_lat=37.7749,
            center_lon=-122.4194,
            zoom_level=10,
            rotation=45.0,
            selected_station="test-123"
        )
        assert state.center_lat == 37.7749
        assert state.zoom_level == 10
    
    def test_default_rotation(self):
        """Test that rotation defaults to 0.0."""
        state = GlobeState(center_lat=0.0, center_lon=0.0, zoom_level=5)
        assert state.rotation == 0.0
    
    def test_invalid_center_lat(self):
        """Test that center_lat must be in valid range."""
        with pytest.raises(ValueError, match="Invalid center_lat"):
            GlobeState(center_lat=95.0, center_lon=0.0, zoom_level=5)
    
    def test_invalid_center_lon(self):
        """Test that center_lon must be in valid range."""
        with pytest.raises(ValueError, match="Invalid center_lon"):
            GlobeState(center_lat=0.0, center_lon=185.0, zoom_level=5)
    
    def test_invalid_zoom_level_too_low(self):
        """Test that zoom_level must be at least 0."""
        with pytest.raises(ValueError, match="Invalid zoom_level"):
            GlobeState(center_lat=0.0, center_lon=0.0, zoom_level=-1)
    
    def test_invalid_zoom_level_too_high(self):
        """Test that zoom_level must be at most 15."""
        with pytest.raises(ValueError, match="Invalid zoom_level"):
            GlobeState(center_lat=0.0, center_lon=0.0, zoom_level=16)
    
    def test_boundary_zoom_levels(self):
        """Test that zoom levels 0 and 15 are valid."""
        state_min = GlobeState(center_lat=0.0, center_lon=0.0, zoom_level=0)
        state_max = GlobeState(center_lat=0.0, center_lon=0.0, zoom_level=15)
        assert state_min.zoom_level == 0
        assert state_max.zoom_level == 15
    
    def test_serialization_roundtrip(self):
        """Test JSON serialization and deserialization."""
        state = GlobeState(
            center_lat=37.7749,
            center_lon=-122.4194,
            zoom_level=10,
            rotation=45.0,
            selected_station="test-123"
        )
        json_str = state.to_json()
        deserialized = GlobeState.from_json(json_str)
        assert deserialized.center_lat == state.center_lat
        assert deserialized.center_lon == state.center_lon
        assert deserialized.zoom_level == state.zoom_level
        assert deserialized.rotation == state.rotation
        assert deserialized.selected_station == state.selected_station


class TestMarkerCluster:
    """Tests for MarkerCluster model."""
    
    def test_valid_marker_cluster(self):
        """Test creating valid marker cluster."""
        stations = [
            StationSummary(
                station_id="test-1",
                name="Station 1",
                coordinates=(37.7, -122.4),
                country="US",
                current_aqi=50
            ),
            StationSummary(
                station_id="test-2",
                name="Station 2",
                coordinates=(37.8, -122.5),
                country="US",
                current_aqi=60
            )
        ]
        cluster = MarkerCluster(
            center_coordinates=(37.75, -122.45),
            station_count=2,
            avg_aqi=55,
            aqi_color="#00E400",
            stations=stations
        )
        assert cluster.station_count == 2
        assert cluster.avg_aqi == 55
        assert len(cluster.stations) == 2
    
    def test_invalid_station_count_mismatch(self):
        """Test that station_count must match stations list length."""
        stations = [
            StationSummary(
                station_id="test-1",
                name="Station 1",
                coordinates=(37.7, -122.4),
                country="US"
            )
        ]
        with pytest.raises(ValueError, match="station_count.*must match"):
            MarkerCluster(
                center_coordinates=(37.75, -122.45),
                station_count=2,  # Mismatch!
                avg_aqi=55,
                aqi_color="#00E400",
                stations=stations
            )
    
    def test_invalid_center_latitude(self):
        """Test that center latitude must be in valid range."""
        stations = [
            StationSummary(
                station_id="test-1",
                name="Station 1",
                coordinates=(37.7, -122.4),
                country="US"
            )
        ]
        with pytest.raises(ValueError, match="Invalid latitude"):
            MarkerCluster(
                center_coordinates=(95.0, -122.45),
                station_count=1,
                avg_aqi=55,
                aqi_color="#00E400",
                stations=stations
            )
    
    def test_invalid_center_longitude(self):
        """Test that center longitude must be in valid range."""
        stations = [
            StationSummary(
                station_id="test-1",
                name="Station 1",
                coordinates=(37.7, -122.4),
                country="US"
            )
        ]
        with pytest.raises(ValueError, match="Invalid longitude"):
            MarkerCluster(
                center_coordinates=(37.75, -185.0),
                station_count=1,
                avg_aqi=55,
                aqi_color="#00E400",
                stations=stations
            )
    
    def test_invalid_avg_aqi(self):
        """Test that avg_aqi must be in valid range."""
        stations = [
            StationSummary(
                station_id="test-1",
                name="Station 1",
                coordinates=(37.7, -122.4),
                country="US"
            )
        ]
        with pytest.raises(ValueError, match="Invalid avg_aqi"):
            MarkerCluster(
                center_coordinates=(37.75, -122.45),
                station_count=1,
                avg_aqi=600,
                aqi_color="#00E400",
                stations=stations
            )
    
    def test_serialization_roundtrip(self):
        """Test JSON serialization and deserialization."""
        stations = [
            StationSummary(
                station_id="test-1",
                name="Station 1",
                coordinates=(37.7, -122.4),
                country="US",
                current_aqi=50
            )
        ]
        cluster = MarkerCluster(
            center_coordinates=(37.75, -122.45),
            station_count=1,
            avg_aqi=50,
            aqi_color="#00E400",
            stations=stations
        )
        json_str = cluster.to_json()
        deserialized = MarkerCluster.from_json(json_str)
        assert deserialized.center_coordinates == cluster.center_coordinates
        assert deserialized.station_count == cluster.station_count
        assert deserialized.avg_aqi == cluster.avg_aqi
        assert deserialized.aqi_color == cluster.aqi_color
        assert len(deserialized.stations) == len(cluster.stations)
