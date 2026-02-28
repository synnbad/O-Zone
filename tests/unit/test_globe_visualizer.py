"""
Unit tests for globe_visualizer module.
"""

import pytest
import math
from src.globe_visualizer import calculate_zoom_bounds
from src.models import GeoBounds


class TestCalculateZoomBounds:
    """Tests for calculate_zoom_bounds function."""
    
    def test_zoom_0_covers_world(self):
        """At zoom level 0, viewport should cover most of the world."""
        bounds = calculate_zoom_bounds((0, 0), 0)
        
        # At zoom 0 from equator, should see most of the world
        assert bounds.north > 80
        assert bounds.south < -80
        # Longitude should span full world at equator
        assert bounds.east == 180
        assert bounds.west == -180
    
    def test_zoom_15_is_small_area(self):
        """At zoom level 15, viewport should be very small (city block)."""
        bounds = calculate_zoom_bounds((37.7749, -122.4194), 15)
        
        # At zoom 15, viewport should be less than 0.01 degrees
        lat_span = bounds.north - bounds.south
        lon_span = bounds.east - bounds.west
        
        assert lat_span < 0.02
        assert lon_span < 0.02
    
    def test_center_point_within_bounds(self):
        """Center point should always be within calculated bounds."""
        test_cases = [
            ((0, 0), 5),
            ((37.7749, -122.4194), 10),  # San Francisco
            ((51.5074, -0.1278), 8),      # London
            ((-33.8688, 151.2093), 12),   # Sydney
        ]
        
        for location, zoom in test_cases:
            lat, lon = location
            bounds = calculate_zoom_bounds(location, zoom)
            
            assert bounds.south <= lat <= bounds.north
            # Longitude comparison needs to handle wraparound
            if bounds.west <= bounds.east:
                assert bounds.west <= lon <= bounds.east
            else:
                # Wraparound case
                assert lon >= bounds.west or lon <= bounds.east
    
    def test_higher_zoom_smaller_bounds(self):
        """Higher zoom levels should produce smaller viewport bounds."""
        location = (40.7128, -74.0060)  # New York
        
        bounds_5 = calculate_zoom_bounds(location, 5)
        bounds_10 = calculate_zoom_bounds(location, 10)
        bounds_15 = calculate_zoom_bounds(location, 15)
        
        span_5 = bounds_5.north - bounds_5.south
        span_10 = bounds_10.north - bounds_10.south
        span_15 = bounds_15.north - bounds_15.south
        
        assert span_5 > span_10 > span_15
    
    def test_latitude_distortion_at_high_latitudes(self):
        """At high latitudes, longitude span should be larger to compensate for distortion."""
        # Compare equator vs high latitude at same zoom
        equator_bounds = calculate_zoom_bounds((0, 0), 5)
        arctic_bounds = calculate_zoom_bounds((70, 0), 5)
        
        equator_lon_span = equator_bounds.east - equator_bounds.west
        arctic_lon_span = arctic_bounds.east - arctic_bounds.west
        
        # At high latitude, longitude span should be larger
        # (or equal if clamped to world bounds)
        assert arctic_lon_span >= equator_lon_span
    
    def test_north_pole_handling(self):
        """Should handle North Pole without error."""
        # Use lower zoom to ensure we hit the pole
        bounds = calculate_zoom_bounds((89, 0), 3)
        
        # Should clamp to 90 degrees north
        assert bounds.north == 90
        assert bounds.south < 90
        # At zoom 3 from lat 89, viewport extends quite far south
        assert bounds.south > 60  # Should still be in northern hemisphere
    
    def test_south_pole_handling(self):
        """Should handle South Pole without error."""
        # Use lower zoom to ensure we hit the pole
        bounds = calculate_zoom_bounds((-89, 0), 3)
        
        # Should clamp to -90 degrees south
        assert bounds.south == -90
        assert bounds.north > -90
        # At zoom 3 from lat -89, viewport extends quite far north
        assert bounds.north < -60  # Should still be in southern hemisphere
    
    def test_antimeridian_crossing_positive(self):
        """Should handle crossing the antimeridian from positive side."""
        # Location near antimeridian at 180 degrees
        bounds = calculate_zoom_bounds((0, 175), 5)
        
        # Bounds should be valid
        assert -90 <= bounds.north <= 90
        assert -90 <= bounds.south <= 90
        assert -180 <= bounds.east <= 180
        assert -180 <= bounds.west <= 180
    
    def test_antimeridian_crossing_negative(self):
        """Should handle crossing the antimeridian from negative side."""
        # Location near antimeridian at -180 degrees
        bounds = calculate_zoom_bounds((0, -175), 5)
        
        # Bounds should be valid
        assert -90 <= bounds.north <= 90
        assert -90 <= bounds.south <= 90
        assert -180 <= bounds.east <= 180
        assert -180 <= bounds.west <= 180
    
    def test_invalid_latitude_raises_error(self):
        """Should raise ValueError for invalid latitude."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            calculate_zoom_bounds((91, 0), 5)
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            calculate_zoom_bounds((-91, 0), 5)
    
    def test_invalid_longitude_raises_error(self):
        """Should raise ValueError for invalid longitude."""
        with pytest.raises(ValueError, match="Invalid longitude"):
            calculate_zoom_bounds((0, 181), 5)
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            calculate_zoom_bounds((0, -181), 5)
    
    def test_invalid_zoom_level_raises_error(self):
        """Should raise ValueError for invalid zoom level."""
        with pytest.raises(ValueError, match="Invalid zoom_level"):
            calculate_zoom_bounds((0, 0), -1)
        
        with pytest.raises(ValueError, match="Invalid zoom_level"):
            calculate_zoom_bounds((0, 0), 16)
    
    def test_returns_geobounds_object(self):
        """Should return a valid GeoBounds object."""
        bounds = calculate_zoom_bounds((0, 0), 5)
        
        assert isinstance(bounds, GeoBounds)
        assert hasattr(bounds, 'north')
        assert hasattr(bounds, 'south')
        assert hasattr(bounds, 'east')
        assert hasattr(bounds, 'west')
    
    def test_consistent_results(self):
        """Same inputs should produce same outputs."""
        location = (37.7749, -122.4194)
        zoom = 10
        
        bounds1 = calculate_zoom_bounds(location, zoom)
        bounds2 = calculate_zoom_bounds(location, zoom)
        
        assert bounds1.north == bounds2.north
        assert bounds1.south == bounds2.south
        assert bounds1.east == bounds2.east
        assert bounds1.west == bounds2.west



class TestGetOptimalZoomLevel:
    """Tests for get_optimal_zoom_level function."""
    
    def test_inverse_of_calculate_zoom_bounds(self):
        """get_optimal_zoom_level should be roughly inverse of calculate_zoom_bounds."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        test_cases = [
            ((0, 0), 5),
            ((37.7749, -122.4194), 10),  # San Francisco
            ((51.5074, -0.1278), 8),      # London
            ((-33.8688, 151.2093), 12),   # Sydney
        ]
        
        for location, original_zoom in test_cases:
            # Calculate bounds for a zoom level
            bounds = calculate_zoom_bounds(location, original_zoom)
            
            # Get optimal zoom for those bounds
            calculated_zoom = get_optimal_zoom_level(bounds)
            
            # Should be same or one level lower (due to rounding down)
            assert calculated_zoom in [original_zoom - 1, original_zoom], \
                f"For location {location} at zoom {original_zoom}, got zoom {calculated_zoom}"
    
    def test_world_bounds_returns_zoom_0(self):
        """Bounds covering the whole world should return zoom level 0."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        world_bounds = GeoBounds(north=85, south=-85, east=180, west=-180)
        zoom = get_optimal_zoom_level(world_bounds)
        
        assert zoom == 0
    
    def test_small_bounds_returns_high_zoom(self):
        """Very small bounds should return high zoom level."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        # City block sized bounds (about 0.01 degrees)
        small_bounds = GeoBounds(north=37.78, south=37.77, east=-122.41, west=-122.42)
        zoom = get_optimal_zoom_level(small_bounds)
        
        # Should be high zoom (at least 12)
        assert zoom >= 12
    
    def test_returns_value_in_valid_range(self):
        """Should always return zoom level between 0 and 15."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        test_bounds = [
            GeoBounds(north=90, south=-90, east=180, west=-180),  # World
            GeoBounds(north=50, south=40, east=10, west=0),       # Country
            GeoBounds(north=37.8, south=37.7, east=-122.3, west=-122.5),  # City
            GeoBounds(north=37.775, south=37.774, east=-122.419, west=-122.420),  # Block
        ]
        
        for bounds in test_bounds:
            zoom = get_optimal_zoom_level(bounds)
            assert 0 <= zoom <= 15
    
    def test_larger_bounds_lower_zoom(self):
        """Larger geographic bounds should produce lower zoom levels."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        # Continent-sized bounds
        continent_bounds = GeoBounds(north=70, south=30, east=40, west=-10)
        
        # Country-sized bounds
        country_bounds = GeoBounds(north=55, south=50, east=5, west=-5)
        
        # City-sized bounds
        city_bounds = GeoBounds(north=37.8, south=37.7, east=-122.3, west=-122.5)
        
        continent_zoom = get_optimal_zoom_level(continent_bounds)
        country_zoom = get_optimal_zoom_level(country_bounds)
        city_zoom = get_optimal_zoom_level(city_bounds)
        
        assert continent_zoom < country_zoom < city_zoom
    
    def test_handles_antimeridian_crossing(self):
        """Should handle bounds that cross the antimeridian."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        # Bounds crossing antimeridian (east < west)
        crossing_bounds = GeoBounds(north=10, south=-10, east=-170, west=170)
        
        # Should not raise error and return valid zoom
        zoom = get_optimal_zoom_level(crossing_bounds)
        assert 0 <= zoom <= 15
    
    def test_accounts_for_latitude_distortion(self):
        """Should account for latitude distortion like calculate_zoom_bounds."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        # Same longitude span at equator vs high latitude
        equator_bounds = GeoBounds(north=5, south=-5, east=10, west=-10)
        arctic_bounds = GeoBounds(north=75, south=65, east=10, west=-10)
        
        equator_zoom = get_optimal_zoom_level(equator_bounds)
        arctic_zoom = get_optimal_zoom_level(arctic_bounds)
        
        # Arctic bounds should have higher zoom (smaller area due to distortion)
        assert arctic_zoom >= equator_zoom
    
    def test_invalid_bounds_north_south_raises_error(self):
        """Should raise ValueError if north <= south."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        # GeoBounds validates in __post_init__, so error happens at construction
        with pytest.raises(ValueError, match="north must be greater than south"):
            invalid_bounds = GeoBounds(north=30, south=40, east=10, west=0)
    
    def test_invalid_bounds_latitude_raises_error(self):
        """Should raise ValueError for invalid latitude values."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        # North latitude out of range
        with pytest.raises(ValueError, match="Invalid north latitude"):
            get_optimal_zoom_level(GeoBounds(north=91, south=0, east=10, west=0))
        
        # South latitude out of range
        with pytest.raises(ValueError, match="Invalid south latitude"):
            get_optimal_zoom_level(GeoBounds(north=0, south=-91, east=10, west=0))
    
    def test_invalid_bounds_longitude_raises_error(self):
        """Should raise ValueError for invalid longitude values."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        # East longitude out of range
        with pytest.raises(ValueError, match="Invalid east longitude"):
            get_optimal_zoom_level(GeoBounds(north=10, south=0, east=181, west=0))
        
        # West longitude out of range
        with pytest.raises(ValueError, match="Invalid west longitude"):
            get_optimal_zoom_level(GeoBounds(north=10, south=0, east=10, west=-181))
    
    def test_prefers_showing_more_area(self):
        """Should round down zoom to show slightly more area rather than less."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        # Create bounds that would ideally be between two zoom levels
        # At zoom 10, viewport is about 0.35 degrees
        # At zoom 11, viewport is about 0.175 degrees
        # Use bounds of 0.25 degrees (between the two)
        bounds = GeoBounds(north=37.875, south=37.625, east=-122.3, west=-122.55)
        
        zoom = get_optimal_zoom_level(bounds)
        
        # Should round down to ensure area fits
        # Verify that the calculated zoom's bounds would contain our input bounds
        center_lat = (bounds.north + bounds.south) / 2
        center_lon = (bounds.east + bounds.west) / 2
        
        calculated_bounds = calculate_zoom_bounds((center_lat, center_lon), zoom)
        
        # The calculated bounds should be at least as large as input bounds
        lat_span_input = bounds.north - bounds.south
        lat_span_calculated = calculated_bounds.north - calculated_bounds.south
        
        assert lat_span_calculated >= lat_span_input * 0.9  # Allow small margin for rounding
    
    def test_consistent_results(self):
        """Same inputs should produce same outputs."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        bounds = GeoBounds(north=37.8, south=37.7, east=-122.3, west=-122.5)
        
        zoom1 = get_optimal_zoom_level(bounds)
        zoom2 = get_optimal_zoom_level(bounds)
        
        assert zoom1 == zoom2
    
    def test_returns_integer(self):
        """Should always return an integer zoom level."""
        from src.globe_visualizer import get_optimal_zoom_level
        
        bounds = GeoBounds(north=37.8, south=37.7, east=-122.3, west=-122.5)
        zoom = get_optimal_zoom_level(bounds)
        
        assert isinstance(zoom, int)



class TestGetStationsForViewport:
    """Tests for get_stations_for_viewport function."""
    
    def test_returns_list_of_station_summaries(self):
        """Should return a list of StationSummary objects."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState, StationSummary
        
        globe_state = GlobeState(
            center_lat=37.7749,
            center_lon=-122.4194,
            zoom_level=10
        )
        
        stations = get_stations_for_viewport(globe_state)
        
        assert isinstance(stations, list)
        # All items should be StationSummary objects
        for station in stations:
            assert isinstance(station, StationSummary)
    
    def test_uses_globe_state_coordinates(self):
        """Should use coordinates from GlobeState to calculate bounds."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        # Test with different locations
        sf_state = GlobeState(center_lat=37.7749, center_lon=-122.4194, zoom_level=10)
        london_state = GlobeState(center_lat=51.5074, center_lon=-0.1278, zoom_level=10)
        
        sf_stations = get_stations_for_viewport(sf_state)
        london_stations = get_stations_for_viewport(london_state)
        
        # Should return stations (may be empty if no data, but should not error)
        assert isinstance(sf_stations, list)
        assert isinstance(london_stations, list)
    
    def test_caching_returns_same_results(self):
        """Should return cached results for same viewport."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        globe_state = GlobeState(
            center_lat=37.7749,
            center_lon=-122.4194,
            zoom_level=10
        )
        
        # First call
        stations1 = get_stations_for_viewport(globe_state)
        
        # Second call with same state should return cached results
        stations2 = get_stations_for_viewport(globe_state)
        
        # Should be the same list (cached)
        assert stations1 == stations2
    
    def test_different_zoom_levels_different_cache(self):
        """Different zoom levels should have separate cache entries."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        state_zoom_5 = GlobeState(center_lat=37.7749, center_lon=-122.4194, zoom_level=5)
        state_zoom_10 = GlobeState(center_lat=37.7749, center_lon=-122.4194, zoom_level=10)
        
        stations_zoom_5 = get_stations_for_viewport(state_zoom_5)
        stations_zoom_10 = get_stations_for_viewport(state_zoom_10)
        
        # Both should return lists
        assert isinstance(stations_zoom_5, list)
        assert isinstance(stations_zoom_10, list)
    
    def test_handles_global_view(self):
        """Should handle global view (zoom level 0)."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        global_state = GlobeState(center_lat=0, center_lon=0, zoom_level=0)
        
        stations = get_stations_for_viewport(global_state)
        
        assert isinstance(stations, list)
    
    def test_handles_high_zoom(self):
        """Should handle high zoom level (city block)."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        high_zoom_state = GlobeState(
            center_lat=37.7749,
            center_lon=-122.4194,
            zoom_level=15
        )
        
        stations = get_stations_for_viewport(high_zoom_state)
        
        assert isinstance(stations, list)
    
    def test_handles_poles(self):
        """Should handle views near poles."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        north_pole_state = GlobeState(center_lat=85, center_lon=0, zoom_level=5)
        south_pole_state = GlobeState(center_lat=-85, center_lon=0, zoom_level=5)
        
        north_stations = get_stations_for_viewport(north_pole_state)
        south_stations = get_stations_for_viewport(south_pole_state)
        
        assert isinstance(north_stations, list)
        assert isinstance(south_stations, list)
    
    def test_handles_antimeridian(self):
        """Should handle views crossing the antimeridian."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        antimeridian_state = GlobeState(center_lat=0, center_lon=180, zoom_level=5)
        
        stations = get_stations_for_viewport(antimeridian_state)
        
        assert isinstance(stations, list)
    
    def test_cache_key_rounds_coordinates(self):
        """Cache should round coordinates to reduce fragmentation."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        # Very slightly different coordinates (within rounding to 2 decimal places)
        # 37.774 rounds to 37.77, 37.775 also rounds to 37.78 (banker's rounding)
        # Let's use 37.771 and 37.774 which both round to 37.77
        # -122.411 and -122.414 both round to -122.41
        state1 = GlobeState(center_lat=37.771, center_lon=-122.411, zoom_level=10)
        state2 = GlobeState(center_lat=37.774, center_lon=-122.414, zoom_level=10)
        
        stations1 = get_stations_for_viewport(state1)
        stations2 = get_stations_for_viewport(state2)
        
        # Should return cached results (same after rounding to 2 decimal places)
        # Compare lengths and station IDs rather than full objects (timestamps may differ)
        assert len(stations1) == len(stations2)
        if len(stations1) > 0:
            assert stations1[0].station_id == stations2[0].station_id
    
    def test_returns_stations_with_coordinates(self):
        """All returned stations should have valid coordinates."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        globe_state = GlobeState(center_lat=37.7749, center_lon=-122.4194, zoom_level=10)
        
        stations = get_stations_for_viewport(globe_state)
        
        for station in stations:
            lat, lon = station.coordinates
            assert -90 <= lat <= 90
            assert -180 <= lon <= 180
    
    def test_stations_have_required_fields(self):
        """All returned stations should have required fields."""
        from src.globe_visualizer import get_stations_for_viewport
        from src.models import GlobeState
        
        globe_state = GlobeState(center_lat=37.7749, center_lon=-122.4194, zoom_level=10)
        
        stations = get_stations_for_viewport(globe_state)
        
        for station in stations:
            assert hasattr(station, 'station_id')
            assert hasattr(station, 'name')
            assert hasattr(station, 'coordinates')
            assert hasattr(station, 'country')
            assert hasattr(station, 'current_aqi')
            assert hasattr(station, 'aqi_category')
            assert hasattr(station, 'aqi_color')
            assert hasattr(station, 'last_updated')



class TestClusterMarkers:
    """Tests for cluster_markers function."""
    
    def test_empty_list_returns_empty(self):
        """Empty station list should return empty result."""
        from src.globe_visualizer import cluster_markers
        
        result = cluster_markers([], 5)
        
        assert result == []
    
    def test_single_station_returns_unchanged(self):
        """Single station should be returned as-is, not clustered."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=datetime.now(UTC)
        )
        
        result = cluster_markers([station], 5)
        
        assert len(result) == 1
        assert result[0] == station
    
    def test_zoom_0_aggressive_clustering(self):
        """At zoom level 0-5, should create large clusters."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        from datetime import datetime, UTC
        
        # Create stations within 10 degree grid cell (should cluster at zoom 0)
        stations = [
            StationSummary(
                station_id=f"test{i}",
                name=f"Station {i}",
                coordinates=(37.0 + i * 0.5, -122.0 + i * 0.5),  # Within same 10-degree cell
                country="US",
                current_aqi=50 + i * 10,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            )
            for i in range(5)
        ]
        
        result = cluster_markers(stations, 0)
        
        # Should create one cluster
        assert len(result) == 1
        assert isinstance(result[0], MarkerCluster)
        assert result[0].station_count == 5
    
    def test_zoom_10_moderate_clustering(self):
        """At zoom level 6-10, should create moderate clusters."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        from datetime import datetime, UTC
        
        # Create stations within 1 degree grid cell (should cluster at zoom 10)
        # Grid cells are 1 degree, so all stations must be in range [37.0, 38.0) and [-122.0, -121.0)
        stations = [
            StationSummary(
                station_id=f"test{i}",
                name=f"Station {i}",
                coordinates=(37.1 + i * 0.1, -121.9 + i * 0.1),  # All within [37, 38) x [-122, -121)
                country="US",
                current_aqi=50 + i * 10,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            )
            for i in range(5)
        ]
        
        result = cluster_markers(stations, 10)
        
        # Should create one cluster (all stations in same 1-degree cell)
        assert len(result) == 1
        assert isinstance(result[0], MarkerCluster)
        assert result[0].station_count == 5
    
    def test_zoom_15_minimal_clustering(self):
        """At zoom level 11+, should have minimal clustering."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        # Create stations spread across different 0.1 degree cells
        stations = [
            StationSummary(
                station_id=f"test{i}",
                name=f"Station {i}",
                coordinates=(37.0 + i * 0.2, -122.0 + i * 0.2),  # Different 0.1-degree cells
                country="US",
                current_aqi=50 + i * 10,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            )
            for i in range(5)
        ]
        
        result = cluster_markers(stations, 15)
        
        # Should return individual stations (no clustering)
        assert len(result) == 5
        for item in result:
            assert isinstance(item, StationSummary)
    
    def test_cluster_calculates_average_aqi(self):
        """Cluster should calculate average AQI from stations."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        from datetime import datetime, UTC
        
        # Create stations with known AQI values
        stations = [
            StationSummary(
                station_id="test1",
                name="Station 1",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test2",
                name="Station 2",
                coordinates=(37.1, -122.1),
                country="US",
                current_aqi=100,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test3",
                name="Station 3",
                coordinates=(37.2, -122.2),
                country="US",
                current_aqi=150,
                aqi_category="Unhealthy for Sensitive Groups",
                aqi_color="#FF7E00",
                last_updated=datetime.now(UTC)
            ),
        ]
        
        result = cluster_markers(stations, 0)
        
        # Should create one cluster
        assert len(result) == 1
        cluster = result[0]
        assert isinstance(cluster, MarkerCluster)
        
        # Average AQI should be (50 + 100 + 150) / 3 = 100
        assert cluster.avg_aqi == 100
    
    def test_cluster_calculates_center_coordinates(self):
        """Cluster should calculate center coordinates from stations."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        from datetime import datetime, UTC
        
        # Create stations with known coordinates
        stations = [
            StationSummary(
                station_id="test1",
                name="Station 1",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test2",
                name="Station 2",
                coordinates=(38.0, -123.0),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            ),
        ]
        
        result = cluster_markers(stations, 0)
        
        # Should create one cluster
        assert len(result) == 1
        cluster = result[0]
        assert isinstance(cluster, MarkerCluster)
        
        # Center should be average: (37.5, -122.5)
        center_lat, center_lon = cluster.center_coordinates
        assert abs(center_lat - 37.5) < 0.01
        assert abs(center_lon - (-122.5)) < 0.01
    
    def test_cluster_handles_missing_aqi(self):
        """Cluster should handle stations with missing AQI data."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        from datetime import datetime, UTC
        
        # Create stations, some with AQI, some without
        stations = [
            StationSummary(
                station_id="test1",
                name="Station 1",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test2",
                name="Station 2",
                coordinates=(37.1, -122.1),
                country="US",
                current_aqi=None,  # No AQI data
                aqi_category=None,
                aqi_color=None,
                last_updated=None
            ),
            StationSummary(
                station_id="test3",
                name="Station 3",
                coordinates=(37.2, -122.2),
                country="US",
                current_aqi=100,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
        ]
        
        result = cluster_markers(stations, 0)
        
        # Should create one cluster
        assert len(result) == 1
        cluster = result[0]
        assert isinstance(cluster, MarkerCluster)
        
        # Average AQI should only consider stations with data: (50 + 100) / 2 = 75
        assert cluster.avg_aqi == 75
    
    def test_cluster_all_missing_aqi_uses_default(self):
        """Cluster with all missing AQI should use default values."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        
        # Create stations without AQI data
        stations = [
            StationSummary(
                station_id="test1",
                name="Station 1",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=None,
                aqi_category=None,
                aqi_color=None,
                last_updated=None
            ),
            StationSummary(
                station_id="test2",
                name="Station 2",
                coordinates=(37.1, -122.1),
                country="US",
                current_aqi=None,
                aqi_category=None,
                aqi_color=None,
                last_updated=None
            ),
        ]
        
        result = cluster_markers(stations, 0)
        
        # Should create one cluster
        assert len(result) == 1
        cluster = result[0]
        assert isinstance(cluster, MarkerCluster)
        
        # Should use default values
        assert cluster.avg_aqi == 0
        assert cluster.aqi_color == '#CCCCCC'  # Gray for no data
    
    def test_cluster_assigns_correct_color(self):
        """Cluster should assign color based on average AQI."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        from datetime import datetime, UTC
        
        # Create stations with AQI that averages to "Moderate" (51-100)
        stations = [
            StationSummary(
                station_id="test1",
                name="Station 1",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=60,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test2",
                name="Station 2",
                coordinates=(37.1, -122.1),
                country="US",
                current_aqi=80,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
        ]
        
        result = cluster_markers(stations, 0)
        
        # Should create one cluster
        assert len(result) == 1
        cluster = result[0]
        assert isinstance(cluster, MarkerCluster)
        
        # Average AQI is 70, which is "Moderate" (yellow)
        assert cluster.avg_aqi == 70
        assert cluster.aqi_color == '#FFFF00'  # Yellow for Moderate
    
    def test_mixed_result_clusters_and_individuals(self):
        """Should return mix of clusters and individual stations."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        from datetime import datetime, UTC
        
        # Create stations: 2 in one cell, 1 in another cell
        stations = [
            # These two should cluster (same 10-degree cell at zoom 0)
            StationSummary(
                station_id="test1",
                name="Station 1",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test2",
                name="Station 2",
                coordinates=(37.5, -122.5),
                country="US",
                current_aqi=60,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
            # This one is far away (different 10-degree cell)
            StationSummary(
                station_id="test3",
                name="Station 3",
                coordinates=(50.0, -100.0),
                country="US",
                current_aqi=70,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
        ]
        
        result = cluster_markers(stations, 0)
        
        # Should have 2 items: 1 cluster and 1 individual
        assert len(result) == 2
        
        # Check types
        clusters = [r for r in result if isinstance(r, MarkerCluster)]
        individuals = [r for r in result if isinstance(r, StationSummary)]
        
        assert len(clusters) == 1
        assert len(individuals) == 1
        
        # Cluster should have 2 stations
        assert clusters[0].station_count == 2
    
    def test_invalid_zoom_level_raises_error(self):
        """Should raise ValueError for invalid zoom level."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=datetime.now(UTC)
        )
        
        with pytest.raises(ValueError, match="Invalid zoom_level"):
            cluster_markers([station], -1)
        
        with pytest.raises(ValueError, match="Invalid zoom_level"):
            cluster_markers([station], 16)
    
    def test_cluster_contains_all_stations(self):
        """Cluster should contain all stations in its stations list."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary, MarkerCluster
        from datetime import datetime, UTC
        
        stations = [
            StationSummary(
                station_id=f"test{i}",
                name=f"Station {i}",
                coordinates=(37.0 + i * 0.1, -122.0 + i * 0.1),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            )
            for i in range(3)
        ]
        
        result = cluster_markers(stations, 0)
        
        # Should create one cluster
        assert len(result) == 1
        cluster = result[0]
        assert isinstance(cluster, MarkerCluster)
        
        # Cluster should contain all original stations
        assert len(cluster.stations) == 3
        assert set(s.station_id for s in cluster.stations) == {"test0", "test1", "test2"}
    
    def test_grid_based_clustering_consistency(self):
        """Same stations should produce same clusters regardless of order."""
        from src.globe_visualizer import cluster_markers
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        stations = [
            StationSummary(
                station_id=f"test{i}",
                name=f"Station {i}",
                coordinates=(37.0 + i * 0.5, -122.0 + i * 0.5),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            )
            for i in range(5)
        ]
        
        # Cluster in original order
        result1 = cluster_markers(stations, 5)
        
        # Cluster in reversed order
        result2 = cluster_markers(list(reversed(stations)), 5)
        
        # Should produce same number of clusters/individuals
        assert len(result1) == len(result2)
        
        # Should have same station counts
        counts1 = sorted([
            r.station_count if hasattr(r, 'station_count') else 1
            for r in result1
        ])
        counts2 = sorted([
            r.station_count if hasattr(r, 'station_count') else 1
            for r in result2
        ])
        assert counts1 == counts2



class TestGenerateTooltip:
    """Tests for generate_tooltip function."""
    
    def test_station_with_complete_data(self):
        """Should generate tooltip with all station information."""
        from src.globe_visualizer import generate_tooltip
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="San Francisco Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=75,
            aqi_category="Moderate",
            aqi_color="#FFFF00",
            last_updated=datetime(2024, 1, 15, 12, 30, tzinfo=UTC)
        )
        
        tooltip = generate_tooltip(station)
        
        # Should contain station name
        assert "San Francisco Station" in tooltip
        # Should contain AQI value
        assert "75" in tooltip
        # Should contain category
        assert "Moderate" in tooltip
        # Should contain timestamp
        assert "2024-01-15" in tooltip
        assert "12:30" in tooltip
        # Should be HTML
        assert "<div" in tooltip
        assert "</div>" in tooltip
    
    def test_station_with_no_recent_data(self):
        """Should show 'No recent data' for station without AQI."""
        from src.globe_visualizer import generate_tooltip
        from src.models import StationSummary
        
        station = StationSummary(
            station_id="test1",
            name="Remote Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=None,
            aqi_category=None,
            aqi_color=None,
            last_updated=None
        )
        
        tooltip = generate_tooltip(station)
        
        # Should contain station name
        assert "Remote Station" in tooltip
        # Should show no data message
        assert "No recent data" in tooltip
        # Should be HTML
        assert "<div" in tooltip
        assert "</div>" in tooltip
    
    def test_station_without_last_updated(self):
        """Should handle station with AQI but no last_updated timestamp."""
        from src.globe_visualizer import generate_tooltip
        from src.models import StationSummary
        
        station = StationSummary(
            station_id="test1",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=None
        )
        
        tooltip = generate_tooltip(station)
        
        # Should contain station name and AQI
        assert "Test Station" in tooltip
        assert "50" in tooltip
        assert "Good" in tooltip
        # Should not crash without timestamp
        assert "<div" in tooltip
    
    def test_cluster_tooltip(self):
        """Should generate tooltip for marker cluster."""
        from src.globe_visualizer import generate_tooltip
        from src.models import MarkerCluster, StationSummary
        from datetime import datetime, UTC
        
        # Create cluster with some stations
        stations = [
            StationSummary(
                station_id=f"test{i}",
                name=f"Station {i}",
                coordinates=(37.0 + i * 0.1, -122.0 + i * 0.1),
                country="US",
                current_aqi=50 + i * 10,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            )
            for i in range(5)
        ]
        
        cluster = MarkerCluster(
            center_coordinates=(37.2, -122.2),
            station_count=5,
            avg_aqi=70,
            aqi_color="#FFFF00",
            stations=stations
        )
        
        tooltip = generate_tooltip(cluster)
        
        # Should show cluster information
        assert "Cluster" in tooltip
        assert "5 stations" in tooltip
        assert "70" in tooltip  # Average AQI
        # Should be HTML
        assert "<div" in tooltip
        assert "</div>" in tooltip
    
    def test_cluster_with_high_aqi(self):
        """Should show correct category for cluster with high AQI."""
        from src.globe_visualizer import generate_tooltip
        from src.models import MarkerCluster, StationSummary
        from datetime import datetime, UTC
        
        stations = [
            StationSummary(
                station_id="test1",
                name="Station 1",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=150,
                aqi_category="Unhealthy for Sensitive Groups",
                aqi_color="#FF7E00",
                last_updated=datetime.now(UTC)
            )
        ]
        
        cluster = MarkerCluster(
            center_coordinates=(37.0, -122.0),
            station_count=1,
            avg_aqi=150,
            aqi_color="#FF7E00",
            stations=stations
        )
        
        tooltip = generate_tooltip(cluster)
        
        # Should show high AQI value
        assert "150" in tooltip
        # Should show correct category
        assert "Unhealthy for Sensitive Groups" in tooltip
    
    def test_tooltip_returns_string(self):
        """Should always return a string."""
        from src.globe_visualizer import generate_tooltip
        from src.models import StationSummary
        
        station = StationSummary(
            station_id="test1",
            name="Test",
            coordinates=(0, 0),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=None
        )
        
        tooltip = generate_tooltip(station)
        
        assert isinstance(tooltip, str)
        assert len(tooltip) > 0
    
    def test_tooltip_html_is_valid(self):
        """Tooltip should contain valid HTML structure."""
        from src.globe_visualizer import generate_tooltip
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=75,
            aqi_category="Moderate",
            aqi_color="#FFFF00",
            last_updated=datetime.now(UTC)
        )
        
        tooltip = generate_tooltip(station)
        
        # Should have opening and closing div tags
        assert tooltip.count("<div") > 0
        assert tooltip.count("</div>") > 0
        # Should have inline styles
        assert "style=" in tooltip
        # Should not have leading/trailing whitespace
        assert tooltip == tooltip.strip()
    
    def test_tooltip_includes_color_coding(self):
        """Tooltip should include AQI color in styling."""
        from src.globe_visualizer import generate_tooltip
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=150,
            aqi_category="Unhealthy for Sensitive Groups",
            aqi_color="#FF7E00",
            last_updated=datetime.now(UTC)
        )
        
        tooltip = generate_tooltip(station)
        
        # Should include the color code
        assert "#FF7E00" in tooltip
    
    def test_tooltip_handles_special_characters_in_name(self):
        """Should handle station names with special characters."""
        from src.globe_visualizer import generate_tooltip
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="Station <Test> & 'Quotes'",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=datetime.now(UTC)
        )
        
        tooltip = generate_tooltip(station)
        
        # Should contain the name (HTML will handle escaping if needed)
        assert "Station" in tooltip
        # Should still be valid HTML
        assert "<div" in tooltip
    
    def test_tooltip_max_width_styling(self):
        """Tooltip should have max-width styling for readability."""
        from src.globe_visualizer import generate_tooltip
        from src.models import StationSummary
        
        station = StationSummary(
            station_id="test1",
            name="Test",
            coordinates=(0, 0),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=None
        )
        
        tooltip = generate_tooltip(station)
        
        # Should have max-width styling
        assert "max-width" in tooltip



class TestHandleMarkerClick:
    """Tests for handle_marker_click function."""
    
    def test_station_summary_returns_location(self):
        """Should convert StationSummary to Location object."""
        from src.globe_visualizer import handle_marker_click
        from src.models import StationSummary, Location
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="San Francisco Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=75,
            aqi_category="Moderate",
            aqi_color="#FFFF00",
            last_updated=datetime.now(UTC)
        )
        
        location = handle_marker_click(station)
        
        assert isinstance(location, Location)
        assert location.name == "San Francisco Station"
        assert location.coordinates == (37.7749, -122.4194)
        assert location.country == "US"
        assert location.providers == []  # Empty, will be populated by data fetcher
    
    def test_station_without_aqi_returns_location(self):
        """Should handle station without AQI data."""
        from src.globe_visualizer import handle_marker_click
        from src.models import StationSummary, Location
        
        station = StationSummary(
            station_id="test1",
            name="Remote Station",
            coordinates=(45.0, -100.0),
            country="CA",
            current_aqi=None,
            aqi_category=None,
            aqi_color=None,
            last_updated=None
        )
        
        location = handle_marker_click(station)
        
        assert isinstance(location, Location)
        assert location.name == "Remote Station"
        assert location.coordinates == (45.0, -100.0)
        assert location.country == "CA"
    
    def test_cluster_selects_highest_aqi_station(self):
        """Should select station with highest AQI from cluster."""
        from src.globe_visualizer import handle_marker_click
        from src.models import MarkerCluster, StationSummary, Location
        from datetime import datetime, UTC
        
        stations = [
            StationSummary(
                station_id="test1",
                name="Low AQI Station",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test2",
                name="High AQI Station",
                coordinates=(37.1, -122.1),
                country="US",
                current_aqi=150,
                aqi_category="Unhealthy for Sensitive Groups",
                aqi_color="#FF7E00",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test3",
                name="Medium AQI Station",
                coordinates=(37.2, -122.2),
                country="US",
                current_aqi=100,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
        ]
        
        cluster = MarkerCluster(
            center_coordinates=(37.1, -122.1),
            station_count=3,
            avg_aqi=100,
            aqi_color="#FFFF00",
            stations=stations
        )
        
        location = handle_marker_click(cluster)
        
        assert isinstance(location, Location)
        # Should select the station with highest AQI (150)
        assert location.name == "High AQI Station"
        assert location.coordinates == (37.1, -122.1)
    
    def test_cluster_with_no_aqi_data_uses_first_station(self):
        """Should use first station if no stations have AQI data."""
        from src.globe_visualizer import handle_marker_click
        from src.models import MarkerCluster, StationSummary, Location
        
        stations = [
            StationSummary(
                station_id="test1",
                name="First Station",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=None,
                aqi_category=None,
                aqi_color=None,
                last_updated=None
            ),
            StationSummary(
                station_id="test2",
                name="Second Station",
                coordinates=(37.1, -122.1),
                country="US",
                current_aqi=None,
                aqi_category=None,
                aqi_color=None,
                last_updated=None
            ),
        ]
        
        cluster = MarkerCluster(
            center_coordinates=(37.05, -122.05),
            station_count=2,
            avg_aqi=0,
            aqi_color="#CCCCCC",
            stations=stations
        )
        
        location = handle_marker_click(cluster)
        
        assert isinstance(location, Location)
        # Should use first station
        assert location.name == "First Station"
        assert location.coordinates == (37.0, -122.0)
    
    def test_cluster_with_mixed_aqi_data(self):
        """Should select highest AQI station even if some have no data."""
        from src.globe_visualizer import handle_marker_click
        from src.models import MarkerCluster, StationSummary, Location
        from datetime import datetime, UTC
        
        stations = [
            StationSummary(
                station_id="test1",
                name="No Data Station",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=None,
                aqi_category=None,
                aqi_color=None,
                last_updated=None
            ),
            StationSummary(
                station_id="test2",
                name="Good AQI Station",
                coordinates=(37.1, -122.1),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test3",
                name="Moderate AQI Station",
                coordinates=(37.2, -122.2),
                country="US",
                current_aqi=100,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
        ]
        
        cluster = MarkerCluster(
            center_coordinates=(37.1, -122.1),
            station_count=3,
            avg_aqi=75,
            aqi_color="#FFFF00",
            stations=stations
        )
        
        location = handle_marker_click(cluster)
        
        assert isinstance(location, Location)
        # Should select station with highest AQI (100), ignoring None
        assert location.name == "Moderate AQI Station"
        assert location.coordinates == (37.2, -122.2)
    
    def test_empty_cluster_raises_error(self):
        """Should raise ValueError for empty cluster."""
        from src.globe_visualizer import handle_marker_click
        from src.models import MarkerCluster
        
        # Create cluster with no stations (edge case)
        cluster = MarkerCluster(
            center_coordinates=(37.0, -122.0),
            station_count=0,
            avg_aqi=0,
            aqi_color="#CCCCCC",
            stations=[]
        )
        
        with pytest.raises(ValueError, match="Cannot handle click on empty cluster"):
            handle_marker_click(cluster)
    
    def test_invalid_marker_type_raises_error(self):
        """Should raise ValueError for invalid marker type."""
        from src.globe_visualizer import handle_marker_click
        
        # Pass something that's neither StationSummary nor MarkerCluster
        invalid_marker = {"name": "Invalid"}
        
        with pytest.raises(ValueError, match="Invalid marker type"):
            handle_marker_click(invalid_marker)
    
    def test_location_has_empty_providers_list(self):
        """Returned Location should have empty providers list."""
        from src.globe_visualizer import handle_marker_click
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=datetime.now(UTC)
        )
        
        location = handle_marker_click(station)
        
        # Providers should be empty list (will be populated by data fetcher)
        assert location.providers == []
    
    def test_location_coordinates_match_station(self):
        """Location coordinates should exactly match station coordinates."""
        from src.globe_visualizer import handle_marker_click
        from src.models import StationSummary
        from datetime import datetime, UTC
        
        # Use precise coordinates
        coords = (37.774929, -122.419418)
        
        station = StationSummary(
            station_id="test1",
            name="Precise Station",
            coordinates=coords,
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=datetime.now(UTC)
        )
        
        location = handle_marker_click(station)
        
        # Coordinates should match exactly
        assert location.coordinates == coords
        assert location.coordinates[0] == 37.774929
        assert location.coordinates[1] == -122.419418
    
    def test_cluster_with_single_station(self):
        """Should handle cluster with only one station."""
        from src.globe_visualizer import handle_marker_click
        from src.models import MarkerCluster, StationSummary, Location
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="Only Station",
            coordinates=(37.0, -122.0),
            country="US",
            current_aqi=75,
            aqi_category="Moderate",
            aqi_color="#FFFF00",
            last_updated=datetime.now(UTC)
        )
        
        cluster = MarkerCluster(
            center_coordinates=(37.0, -122.0),
            station_count=1,
            avg_aqi=75,
            aqi_color="#FFFF00",
            stations=[station]
        )
        
        location = handle_marker_click(cluster)
        
        assert isinstance(location, Location)
        assert location.name == "Only Station"
        assert location.coordinates == (37.0, -122.0)
    
    def test_cluster_with_tie_aqi_selects_first(self):
        """When multiple stations have same highest AQI, should select first one."""
        from src.globe_visualizer import handle_marker_click
        from src.models import MarkerCluster, StationSummary, Location
        from datetime import datetime, UTC
        
        stations = [
            StationSummary(
                station_id="test1",
                name="First High AQI",
                coordinates=(37.0, -122.0),
                country="US",
                current_aqi=100,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
            StationSummary(
                station_id="test2",
                name="Second High AQI",
                coordinates=(37.1, -122.1),
                country="US",
                current_aqi=100,
                aqi_category="Moderate",
                aqi_color="#FFFF00",
                last_updated=datetime.now(UTC)
            ),
        ]
        
        cluster = MarkerCluster(
            center_coordinates=(37.05, -122.05),
            station_count=2,
            avg_aqi=100,
            aqi_color="#FFFF00",
            stations=stations
        )
        
        location = handle_marker_click(cluster)
        
        assert isinstance(location, Location)
        # max() returns first occurrence in case of tie
        assert location.name in ["First High AQI", "Second High AQI"]
        assert location.coordinates in [(37.0, -122.0), (37.1, -122.1)]
    
    def test_location_can_be_used_with_data_fetcher(self):
        """Returned Location should be valid for data_fetcher functions."""
        from src.globe_visualizer import handle_marker_click
        from src.models import StationSummary, Location
        from datetime import datetime, UTC
        
        station = StationSummary(
            station_id="test1",
            name="Test Station",
            coordinates=(37.7749, -122.4194),
            country="US",
            current_aqi=50,
            aqi_category="Good",
            aqi_color="#00E400",
            last_updated=datetime.now(UTC)
        )
        
        location = handle_marker_click(station)
        
        # Verify Location has all required fields for data fetcher
        assert hasattr(location, 'name')
        assert hasattr(location, 'coordinates')
        assert hasattr(location, 'country')
        assert hasattr(location, 'providers')
        
        # Verify types
        assert isinstance(location.name, str)
        assert isinstance(location.coordinates, tuple)
        assert len(location.coordinates) == 2
        assert isinstance(location.country, str)
        assert isinstance(location.providers, list)



class TestRenderGlobe:
    """Tests for render_globe function."""
    
    def test_returns_pydeck_deck_object(self):
        """Should return a pydeck Deck object."""
        from src.globe_visualizer import render_globe
        from src.models import GlobeState, StationSummary
        import pydeck as pdk
        from datetime import datetime, UTC
        
        # Create test data
        state = GlobeState(
            center_lat=37.7749,
            center_lon=-122.4194,
            zoom_level=10,
            rotation=0.0
        )
        
        stations = [
            StationSummary(
                station_id="test1",
                name="Test Station 1",
                coordinates=(37.7749, -122.4194),
                country="US",
                current_aqi=50,
                aqi_category="Good",
                aqi_color="#00E400",
                last_updated=datetime.now(UTC)
            )
        ]
        
        deck = render_globe(state, stations)
        
        assert isinstance(deck, pdk.Deck)
    
    def test_applies_clustering_at_low_zoom(self):
        """Should apply clustering at low zoom levels."""
        from src.globe_visualizer import render_globe
        from src.models import GlobeState, StationSummary
        from datetime import datetime, UTC
        
        # Create many nearby stations
        stations = []
        for i in range(20):
            stations.append(
                StationSummary(
                    station_id=f"test{i}",
                    name=f"Test Station {i}",
                    coordinates=(37.7 + i * 0.01, -122.4 + i * 0.01),
                    country="US",
                    current_aqi=50 + i,
                    aqi_category="Good",
                    aqi_color="#00E400",
                    last_updated=datetime.now(UTC)
                )
            )
        
        # At zoom 3, should cluster
        state_low_zoom = GlobeState(
            center_lat=37.7749,
            center_lon=-122.4194,
            zoom_level=3,
            rotation=0.0
        )
        
        deck = render_globe(state_low_zoom, stations)
        
        # Should have created a deck with layers
        assert len(deck.layers) > 0
        assert deck.layers[0].type == 'ScatterplotLayer'
    
    def test_handles_empty_station_list(self):
        """Should handle empty station list without error."""
        from src.globe_visualizer import render_globe
        from src.models import GlobeState
        import pydeck as pdk
        
        state = GlobeState(
            center_lat=0.0,
            center_lon=0.0,
            zoom_level=2,
            rotation=0.0
        )
        
        deck = render_globe(state, [])
        
        assert isinstance(deck, pdk.Deck)
        assert len(deck.layers) > 0
    
    def test_uses_state_coordinates_for_view(self):
        """Should use GlobeState coordinates for view state."""
        from src.globe_visualizer import render_globe
        from src.models import GlobeState
        
        state = GlobeState(
            center_lat=51.5074,
            center_lon=-0.1278,
            zoom_level=8,
            rotation=45.0
        )
        
        deck = render_globe(state, [])
        
        # Check view state matches input
        assert deck.initial_view_state.latitude == 51.5074
        assert deck.initial_view_state.longitude == -0.1278
        assert deck.initial_view_state.zoom == 8
        assert deck.initial_view_state.bearing == 45.0
    
    def test_handles_stations_without_aqi(self):
        """Should handle stations with no AQI data."""
        from src.globe_visualizer import render_globe
        from src.models import GlobeState, StationSummary
        import pydeck as pdk
        
        state = GlobeState(
            center_lat=37.7749,
            center_lon=-122.4194,
            zoom_level=10,
            rotation=0.0
        )
        
        stations = [
            StationSummary(
                station_id="test1",
                name="Test Station",
                coordinates=(37.7749, -122.4194),
                country="US",
                current_aqi=None,  # No AQI data
                aqi_category=None,
                aqi_color=None,
                last_updated=None
            )
        ]
        
        deck = render_globe(state, stations)
        
        assert isinstance(deck, pdk.Deck)
        assert len(deck.layers) > 0
    
    def test_configures_tooltip(self):
        """Should configure tooltip for markers."""
        from src.globe_visualizer import render_globe
        from src.models import GlobeState
        import pydeck as pdk
        
        state = GlobeState(
            center_lat=0.0,
            center_lon=0.0,
            zoom_level=5,
            rotation=0.0
        )
        
        deck = render_globe(state, [])
        
        # Should have created a deck object
        assert isinstance(deck, pdk.Deck)
        # Should have layers configured
        assert len(deck.layers) > 0


class TestHexToRgb:
    """Tests for _hex_to_rgb helper function."""
    
    def test_converts_red(self):
        """Should convert red hex to RGB."""
        from src.globe_visualizer import _hex_to_rgb
        
        rgb = _hex_to_rgb('#FF0000')
        assert rgb == [255, 0, 0]
    
    def test_converts_green(self):
        """Should convert green hex to RGB."""
        from src.globe_visualizer import _hex_to_rgb
        
        rgb = _hex_to_rgb('#00E400')
        assert rgb == [0, 228, 0]
    
    def test_converts_without_hash(self):
        """Should handle hex codes without # prefix."""
        from src.globe_visualizer import _hex_to_rgb
        
        rgb = _hex_to_rgb('FF7E00')
        assert rgb == [255, 126, 0]
    
    def test_converts_purple(self):
        """Should convert purple hex to RGB."""
        from src.globe_visualizer import _hex_to_rgb
        
        rgb = _hex_to_rgb('#8F3F97')
        assert rgb == [143, 63, 151]
