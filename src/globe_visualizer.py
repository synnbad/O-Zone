"""
Globe visualization module for O-Zone MVP.

This module provides functions for rendering and interacting with
the interactive globe/map visualization of global air quality data.
"""

import math
from typing import Optional
from src.models import GeoBounds


def calculate_zoom_bounds(location: tuple[float, float], zoom_level: int) -> GeoBounds:
    """
    Calculate geographic bounds for a given center point and zoom level.
    
    Uses standard web mercator projection formulas to determine the visible
    geographic area at a specific zoom level. Accounts for latitude distortion
    where degrees of longitude represent less distance near the poles.
    
    Zoom level mapping:
    - 0: Entire world
    - 5: Continent
    - 10: City
    - 15: City block
    
    Args:
        location: Tuple of (latitude, longitude) for center point
        zoom_level: Integer from 0 (global view) to 15 (city level)
    
    Returns:
        GeoBounds object with north, south, east, west coordinates
    
    Raises:
        ValueError: If zoom_level is not in range [0, 15] or coordinates invalid
    
    Requirements: 13.7
    """
    lat, lon = location
    
    # Validate inputs
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
    if not (0 <= zoom_level <= 15):
        raise ValueError(f"Invalid zoom_level: {zoom_level}. Must be 0-15.")
    
    # Calculate the viewport size in degrees based on zoom level
    # At zoom 0, we see the entire world (360 degrees longitude)
    # Each zoom level doubles the magnification (halves the viewport)
    # Base viewport width at zoom 0 is 360 degrees
    base_viewport_degrees = 360.0
    viewport_width_degrees = base_viewport_degrees / (2 ** zoom_level)
    
    # Account for latitude distortion using the Mercator projection
    # At higher latitudes, degrees of longitude represent less actual distance
    # We need to adjust the viewport width based on the cosine of latitude
    # This ensures consistent visual coverage at different latitudes
    lat_radians = math.radians(lat)
    
    # Avoid division by zero at poles and clamp extreme latitudes
    # At latitudes > 85 degrees, Mercator projection becomes highly distorted
    clamped_lat = max(-85, min(85, lat))
    clamped_lat_radians = math.radians(clamped_lat)
    
    # Calculate longitude adjustment factor
    # cos(latitude) gives us the ratio of longitude distance to equatorial distance
    cos_lat = math.cos(clamped_lat_radians)
    
    # Adjust longitude viewport width based on latitude
    # At the equator (cos = 1), no adjustment needed
    # Near poles (cos → 0), viewport width increases to maintain visual size
    if cos_lat > 0.01:  # Avoid extreme distortion near poles
        adjusted_lon_width = viewport_width_degrees / cos_lat
    else:
        # Near poles, use a large but bounded viewport
        adjusted_lon_width = viewport_width_degrees / 0.01
    
    # For latitude, use the same viewport height as width at equator
    # This maintains roughly square aspect ratio
    viewport_height_degrees = viewport_width_degrees
    
    # Calculate bounds
    half_width = adjusted_lon_width / 2
    half_height = viewport_height_degrees / 2
    
    # Calculate raw bounds
    north = lat + half_height
    south = lat - half_height
    east = lon + half_width
    west = lon - half_width
    
    # Clamp latitude to valid range [-90, 90]
    north = min(90, north)
    south = max(-90, south)
    
    # Handle longitude wraparound at antimeridian (±180 degrees)
    # Normalize to [-180, 180] range
    if east > 180:
        east = east - 360
    if west < -180:
        west = west + 360
    
    # Special case: if viewport spans more than 360 degrees longitude
    # (only possible at very high latitudes with low zoom), clamp to world bounds
    if adjusted_lon_width >= 360:
        east = 180
        west = -180
    
    # Ensure north > south for valid GeoBounds
    # This should always be true, but check for edge cases
    if north <= south:
        # If we're at a pole, create a minimal valid bounds
        if abs(lat) > 89:
            north = 90 if lat > 0 else -89.9
            south = 89.9 if lat > 0 else -90
        else:
            raise ValueError(f"Invalid bounds calculated: north={north}, south={south}")
    
    return GeoBounds(
        north=north,
        south=south,
        east=east,
        west=west
    )


def get_optimal_zoom_level(bounds: GeoBounds) -> int:
    """
    Determine appropriate zoom level to fit given geographic bounds.
    
    This function works inversely to calculate_zoom_bounds: given desired bounds,
    it finds the zoom level that would produce a viewport that fits those bounds.
    The function prefers showing slightly more area rather than less (rounds down
    zoom if needed) to ensure the entire desired area is visible.
    
    The algorithm:
    1. Calculate the center point of the bounds
    2. Calculate the span (width and height) of the bounds
    3. Account for latitude distortion like calculate_zoom_bounds does
    4. Find the zoom level where the viewport would fit the desired span
    5. Round down to ensure the area fits (show more rather than less)
    
    Args:
        bounds: GeoBounds object with north, south, east, west coordinates
    
    Returns:
        Integer zoom level between 0 and 15 that fits the bounds
    
    Raises:
        ValueError: If bounds are invalid (north <= south, invalid coordinates)
    
    Requirements: 13.5
    """
    # Validate bounds
    if bounds.north <= bounds.south:
        raise ValueError(
            f"Invalid bounds: north ({bounds.north}) must be greater than south ({bounds.south})"
        )
    if not (-90 <= bounds.north <= 90):
        raise ValueError(f"Invalid north latitude: {bounds.north}. Must be between -90 and 90.")
    if not (-90 <= bounds.south <= 90):
        raise ValueError(f"Invalid south latitude: {bounds.south}. Must be between -90 and 90.")
    if not (-180 <= bounds.east <= 180):
        raise ValueError(f"Invalid east longitude: {bounds.east}. Must be between -180 and 180.")
    if not (-180 <= bounds.west <= 180):
        raise ValueError(f"Invalid west longitude: {bounds.west}. Must be between -180 and 180.")
    
    # Calculate center point of bounds
    center_lat = (bounds.north + bounds.south) / 2
    
    # Calculate longitude center, handling wraparound at antimeridian
    if bounds.east < bounds.west:
        # Bounds cross the antimeridian (e.g., east=170, west=-170)
        # Calculate center by going the "long way" around
        center_lon = ((bounds.east + 360 + bounds.west) / 2) % 360
        if center_lon > 180:
            center_lon -= 360
    else:
        center_lon = (bounds.east + bounds.west) / 2
    
    # Calculate the span of the bounds
    lat_span = bounds.north - bounds.south
    
    # Calculate longitude span, handling wraparound
    if bounds.east < bounds.west:
        # Crosses antimeridian
        lon_span = (bounds.east + 360) - bounds.west
    else:
        lon_span = bounds.east - bounds.west
    
    # Account for latitude distortion using Mercator projection
    # Same logic as calculate_zoom_bounds
    clamped_lat = max(-85, min(85, center_lat))
    clamped_lat_radians = math.radians(clamped_lat)
    cos_lat = math.cos(clamped_lat_radians)
    
    # Adjust longitude span based on latitude
    # At the equator, no adjustment needed
    # Near poles, longitude degrees represent less distance
    if cos_lat > 0.01:
        adjusted_lon_span = lon_span * cos_lat
    else:
        # Near poles, use minimum adjustment to avoid extreme values
        adjusted_lon_span = lon_span * 0.01
    
    # Determine which span (latitude or adjusted longitude) is larger
    # We need to fit both, so use the larger span to determine zoom level
    max_span = max(lat_span, adjusted_lon_span)
    
    # Calculate zoom level based on span
    # At zoom 0, viewport is 360 degrees
    # At zoom n, viewport is 360 / (2^n) degrees
    # So: max_span = 360 / (2^zoom)
    # Solving for zoom: 2^zoom = 360 / max_span
    # zoom = log2(360 / max_span)
    
    base_viewport_degrees = 360.0
    
    # Handle edge case where span is very large (larger than world)
    if max_span >= base_viewport_degrees:
        return 0  # Global view
    
    # Calculate ideal zoom level
    zoom_ratio = base_viewport_degrees / max_span
    ideal_zoom = math.log2(zoom_ratio)
    
    # Round down to show slightly more area rather than less
    # This ensures the entire desired area is visible
    zoom_level = int(math.floor(ideal_zoom))
    
    # Clamp to valid range [0, 15]
    zoom_level = max(0, min(15, zoom_level))
    
    return zoom_level


def get_stations_for_viewport(globe_state: 'GlobeState') -> list['StationSummary']:
    """
    Retrieve station data for the current viewport.

    This function is a thin wrapper around data_fetcher.get_global_stations
    that adds viewport-based caching. It calculates the geographic bounds
    for the current globe view and fetches stations within those bounds.

    The data_fetcher.get_global_stations function already returns StationSummary
    objects with AQI calculated, so this function primarily handles:
    1. Converting GlobeState to GeoBounds
    2. Calling the data fetcher
    3. Implementing viewport-specific caching

    Caching strategy:
    - Cache key includes center coordinates and zoom level
    - Separate from data_fetcher's cache for flexibility
    - Uses same TTL as globe cache (1 hour)

    Args:
        globe_state: Current state of the globe visualization including
                    center coordinates and zoom level

    Returns:
        List of StationSummary objects for stations within the viewport.
        Each station includes coordinates, name, country, and current AQI
        (if available).

    Requirements: 13.7
    """
    from src.models import GlobeState, StationSummary
    from src import data_fetcher
    from src.config import Config
    from datetime import datetime, UTC

    # Create cache key based on viewport parameters
    # Round coordinates to reduce cache fragmentation while maintaining accuracy
    cache_key = (
        f"viewport_stations:"
        f"{round(globe_state.center_lat, 2)}:"
        f"{round(globe_state.center_lon, 2)}:"
        f"{globe_state.zoom_level}"
    )

    # Check viewport cache
    cached = _get_viewport_cache(cache_key, Config.GLOBE_CACHE_TTL_SECONDS)
    if cached is not None:
        return cached

    # Calculate bounds for current viewport
    bounds = calculate_zoom_bounds(
        location=(globe_state.center_lat, globe_state.center_lon),
        zoom_level=globe_state.zoom_level
    )

    # Fetch stations from data fetcher
    # Note: data_fetcher.get_global_stations already returns StationSummary
    # objects with AQI calculated (or None if no recent data)
    stations = data_fetcher.get_global_stations(bounds)

    # Cache the results
    _set_viewport_cache(cache_key, stations)

    return stations


# Viewport-specific cache (separate from data_fetcher's cache)
_viewport_cache = {}
_viewport_cache_timestamps = {}


def _get_viewport_cache(key: str, ttl_seconds: int) -> Optional[list]:
    """Get data from viewport cache if valid."""
    if key not in _viewport_cache or key not in _viewport_cache_timestamps:
        return None

    age = (datetime.now(UTC) - _viewport_cache_timestamps[key]).total_seconds()
    if age < ttl_seconds:
        return _viewport_cache[key]

    # Cache expired, remove it
    del _viewport_cache[key]
    del _viewport_cache_timestamps[key]
    return None


def _set_viewport_cache(key: str, value: list) -> None:
    """Store data in viewport cache with current timestamp."""
    _viewport_cache[key] = value
    _viewport_cache_timestamps[key] = datetime.now(UTC)



# Viewport-specific cache (separate from data_fetcher's cache)
_viewport_cache = {}
_viewport_cache_timestamps = {}


def _get_viewport_cache(key: str, ttl_seconds: int):
    """Get data from viewport cache if valid."""
    from datetime import datetime, UTC
    
    if key not in _viewport_cache or key not in _viewport_cache_timestamps:
        return None
    
    age = (datetime.now(UTC) - _viewport_cache_timestamps[key]).total_seconds()
    if age < ttl_seconds:
        return _viewport_cache[key]
    
    # Cache expired, remove it
    del _viewport_cache[key]
    del _viewport_cache_timestamps[key]
    return None


def _set_viewport_cache(key: str, value: list) -> None:
    """Store data in viewport cache with current timestamp."""
    from datetime import datetime, UTC
    
    _viewport_cache[key] = value
    _viewport_cache_timestamps[key] = datetime.now(UTC)


def get_stations_for_viewport(globe_state) -> list:
    """
    Retrieve station data for the current viewport.
    
    This function is a thin wrapper around data_fetcher.get_global_stations
    that adds viewport-based caching. It calculates the geographic bounds
    for the current globe view and fetches stations within those bounds.
    
    The data_fetcher.get_global_stations function already returns StationSummary
    objects with AQI calculated, so this function primarily handles:
    1. Converting GlobeState to GeoBounds
    2. Calling the data fetcher
    3. Implementing viewport-specific caching
    
    Caching strategy:
    - Cache key includes center coordinates and zoom level
    - Separate from data_fetcher's cache for flexibility
    - Uses same TTL as globe cache (1 hour)
    
    Args:
        globe_state: Current state of the globe visualization including
                    center coordinates and zoom level (GlobeState object)
    
    Returns:
        List of StationSummary objects for stations within the viewport.
        Each station includes coordinates, name, country, and current AQI
        (if available).
    
    Requirements: 13.7
    """
    from src import data_fetcher
    from src.config import Config
    
    # Create cache key based on viewport parameters
    # Round coordinates to reduce cache fragmentation while maintaining accuracy
    cache_key = (
        f"viewport_stations:"
        f"{round(globe_state.center_lat, 2)}:"
        f"{round(globe_state.center_lon, 2)}:"
        f"{globe_state.zoom_level}"
    )
    
    # Check viewport cache
    cached = _get_viewport_cache(cache_key, Config.GLOBE_CACHE_TTL_SECONDS)
    if cached is not None:
        return cached
    
    # Calculate bounds for current viewport
    bounds = calculate_zoom_bounds(
        location=(globe_state.center_lat, globe_state.center_lon),
        zoom_level=globe_state.zoom_level
    )
    
    # Fetch stations from data fetcher
    # Note: data_fetcher.get_global_stations already returns StationSummary
    # objects with AQI calculated (or None if no recent data)
    stations = data_fetcher.get_global_stations(bounds)
    
    # Cache the results
    _set_viewport_cache(cache_key, stations)
    
    return stations


def cluster_markers(
    stations: list['StationSummary'],
    zoom_level: int
) -> list['MarkerCluster | StationSummary']:
    """
    Apply spatial clustering algorithm based on zoom level.

    This function uses grid-based clustering for performance when rendering
    thousands of stations. At lower zoom levels, nearby stations are grouped
    into clusters to reduce visual clutter and improve rendering performance.
    At higher zoom levels, individual stations are shown.

    Grid-based clustering algorithm:
    1. Divide the world into a grid based on zoom level
    2. Assign each station to a grid cell based on its coordinates
    3. For cells with multiple stations, create a MarkerCluster
    4. For cells with a single station, keep as StationSummary
    5. Calculate average AQI and center coordinates for clusters

    Clustering thresholds by zoom level:
    - Zoom 0-5: Aggressive clustering (grid size ~10 degrees, 100+ stations per cluster)
    - Zoom 6-10: Moderate clustering (grid size ~1 degree, 10-50 stations per cluster)
    - Zoom 11+: Minimal clustering (grid size ~0.1 degrees, individual markers visible)

    Args:
        stations: List of StationSummary objects to cluster
        zoom_level: Current zoom level (0-15)

    Returns:
        Mixed list of MarkerCluster and StationSummary objects.
        Clusters contain multiple stations, individual stations are returned as-is.

    Raises:
        ValueError: If zoom_level is not in range [0, 15]

    Requirements: 13.12
    """
    from src.models import MarkerCluster, StationSummary
    from src.config import Config
    from collections import defaultdict

    # Validate zoom level
    if not (0 <= zoom_level <= 15):
        raise ValueError(f"Invalid zoom_level: {zoom_level}. Must be 0-15.")

    # Handle empty input
    if not stations:
        return []

    # Determine grid cell size based on zoom level
    # Lower zoom = larger cells = more aggressive clustering
    # Higher zoom = smaller cells = less clustering
    if zoom_level <= 5:
        # Aggressive clustering: ~10 degree cells
        # At zoom 0, this creates ~36 cells globally (360/10 * 180/10)
        grid_size = 10.0
    elif zoom_level <= 10:
        # Moderate clustering: ~1 degree cells
        # At zoom 8, this creates ~64,800 cells globally
        grid_size = 1.0
    else:
        # Minimal clustering: ~0.1 degree cells
        # At zoom 12+, most cells will have 0-1 stations
        grid_size = 0.1

    # Group stations into grid cells
    # Key: (grid_lat, grid_lon) tuple representing cell coordinates
    # Value: list of stations in that cell
    grid_cells = defaultdict(list)

    for station in stations:
        lat, lon = station.coordinates

        # Calculate grid cell coordinates by rounding to nearest grid boundary
        # Floor division ensures consistent cell assignment
        grid_lat = int(lat / grid_size) * grid_size
        grid_lon = int(lon / grid_size) * grid_size

        grid_cells[(grid_lat, grid_lon)].append(station)

    # Process each grid cell to create clusters or individual markers
    result = []

    for (grid_lat, grid_lon), cell_stations in grid_cells.items():
        if len(cell_stations) == 1:
            # Single station in cell - return as individual marker
            result.append(cell_stations[0])
        else:
            # Multiple stations in cell - create cluster

            # Calculate center coordinates as average of all station coordinates
            total_lat = sum(s.coordinates[0] for s in cell_stations)
            total_lon = sum(s.coordinates[1] for s in cell_stations)
            center_lat = total_lat / len(cell_stations)
            center_lon = total_lon / len(cell_stations)

            # Calculate average AQI from stations with valid AQI data
            stations_with_aqi = [s for s in cell_stations if s.current_aqi is not None]

            if stations_with_aqi:
                # Calculate average AQI
                avg_aqi = sum(s.current_aqi for s in stations_with_aqi) / len(stations_with_aqi)
                avg_aqi_int = int(round(avg_aqi))

                # Get color for average AQI
                aqi_color = Config.get_aqi_color(avg_aqi_int)
            else:
                # No stations have AQI data - use neutral values
                avg_aqi_int = 0
                aqi_color = '#CCCCCC'  # Gray for no data

            # Create cluster object
            cluster = MarkerCluster(
                center_coordinates=(center_lat, center_lon),
                station_count=len(cell_stations),
                avg_aqi=avg_aqi_int,
                aqi_color=aqi_color,
                stations=cell_stations
            )

            result.append(cluster)

    return result


def generate_tooltip(marker: 'StationSummary | MarkerCluster') -> str:
    """
    Generate HTML tooltip content for station marker or cluster.

    Creates formatted HTML tooltip that displays relevant information
    when users hover over markers on the globe visualization. Handles
    both individual stations and clustered markers, with graceful
    handling of missing data.

    For StationSummary markers:
    - Station name
    - Current AQI value and category
    - Last update timestamp
    - "No recent data" message if AQI unavailable

    For MarkerCluster markers:
    - Number of stations in cluster
    - Average AQI value
    - AQI category based on average

    The HTML is styled inline for compatibility with pydeck tooltips.

    Args:
        marker: Either a StationSummary or MarkerCluster object

    Returns:
        Formatted HTML string ready for display in tooltip

    Requirements: 13.8
    """
    from src.models import StationSummary, MarkerCluster
    from src.config import Config

    # Check if this is a cluster or individual station
    if isinstance(marker, MarkerCluster):
        # Generate tooltip for cluster
        # Get category name from average AQI
        category = Config.get_aqi_category(marker.avg_aqi)

        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 8px; max-width: 250px;">
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #333;">
                Cluster of {marker.station_count} stations
            </div>
            <div style="font-size: 12px; color: #666; margin-bottom: 2px;">
                Average AQI: <span style="font-weight: bold; color: {marker.aqi_color};">{marker.avg_aqi}</span>
            </div>
            <div style="font-size: 11px; color: #888;">
                Category: {category}
            </div>
        </div>
        """

    elif isinstance(marker, StationSummary):
        # Generate tooltip for individual station
        if marker.current_aqi is not None:
            # Station has recent data
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 8px; max-width: 250px;">
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #333;">
                    {marker.name}
                </div>
                <div style="font-size: 12px; color: #666; margin-bottom: 2px;">
                    AQI: <span style="font-weight: bold; color: {marker.aqi_color};">{marker.current_aqi}</span>
                </div>
                <div style="font-size: 11px; color: #888; margin-bottom: 2px;">
                    Category: {marker.aqi_category}
                </div>
            """

            # Add last update time if available
            if marker.last_updated:
                # Format timestamp in a readable way
                time_str = marker.last_updated.strftime("%Y-%m-%d %H:%M UTC")
                html += f"""
                <div style="font-size: 10px; color: #999; margin-top: 4px;">
                    Updated: {time_str}
                </div>
                """

            html += "</div>"

        else:
            # Station has no recent data
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 8px; max-width: 250px;">
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #333;">
                    {marker.name}
                </div>
                <div style="font-size: 12px; color: #999; font-style: italic;">
                    No recent data
                </div>
            </div>
            """
    else:
        # Unknown marker type - return generic message
        html = """
        <div style="font-family: Arial, sans-serif; padding: 8px;">
            <div style="font-size: 12px; color: #666;">
                Air quality monitoring station
            </div>
        </div>
        """

    return html.strip()




def cluster_markers(
    stations: list['StationSummary'], 
    zoom_level: int
) -> list['MarkerCluster | StationSummary']:
    """
    Apply spatial clustering algorithm based on zoom level.
    
    This function uses grid-based clustering for performance when rendering
    thousands of stations. At lower zoom levels, nearby stations are grouped
    into clusters to reduce visual clutter and improve rendering performance.
    At higher zoom levels, individual stations are shown.
    
    Grid-based clustering algorithm:
    1. Divide the world into a grid based on zoom level
    2. Assign each station to a grid cell based on its coordinates
    3. For cells with multiple stations, create a MarkerCluster
    4. For cells with a single station, keep as StationSummary
    5. Calculate average AQI and center coordinates for clusters
    
    Clustering thresholds by zoom level:
    - Zoom 0-5: Aggressive clustering (grid size ~10 degrees, 100+ stations per cluster)
    - Zoom 6-10: Moderate clustering (grid size ~1 degree, 10-50 stations per cluster)
    - Zoom 11+: Minimal clustering (grid size ~0.1 degrees, individual markers visible)
    
    Args:
        stations: List of StationSummary objects to cluster
        zoom_level: Current zoom level (0-15)
    
    Returns:
        Mixed list of MarkerCluster and StationSummary objects.
        Clusters contain multiple stations, individual stations are returned as-is.
    
    Raises:
        ValueError: If zoom_level is not in range [0, 15]
    
    Requirements: 13.12
    """
    from src.models import MarkerCluster, StationSummary
    from src.config import Config
    from collections import defaultdict
    
    # Validate zoom level
    if not (0 <= zoom_level <= 15):
        raise ValueError(f"Invalid zoom_level: {zoom_level}. Must be 0-15.")
    
    # Handle empty input
    if not stations:
        return []
    
    # Determine grid cell size based on zoom level
    # Lower zoom = larger cells = more aggressive clustering
    # Higher zoom = smaller cells = less clustering
    if zoom_level <= 5:
        # Aggressive clustering: ~10 degree cells
        # At zoom 0, this creates ~36 cells globally (360/10 * 180/10)
        grid_size = 10.0
    elif zoom_level <= 10:
        # Moderate clustering: ~1 degree cells
        # At zoom 8, this creates ~64,800 cells globally
        grid_size = 1.0
    else:
        # Minimal clustering: ~0.1 degree cells
        # At zoom 12+, most cells will have 0-1 stations
        grid_size = 0.1
    
    # Group stations into grid cells
    # Key: (grid_lat, grid_lon) tuple representing cell coordinates
    # Value: list of stations in that cell
    grid_cells = defaultdict(list)
    
    for station in stations:
        lat, lon = station.coordinates
        
        # Calculate grid cell coordinates by rounding to nearest grid boundary
        # Floor division ensures consistent cell assignment
        grid_lat = int(lat / grid_size) * grid_size
        grid_lon = int(lon / grid_size) * grid_size
        
        grid_cells[(grid_lat, grid_lon)].append(station)
    
    # Process each grid cell to create clusters or individual markers
    result = []
    
    for (grid_lat, grid_lon), cell_stations in grid_cells.items():
        if len(cell_stations) == 1:
            # Single station in cell - return as individual marker
            result.append(cell_stations[0])
        else:
            # Multiple stations in cell - create cluster
            
            # Calculate center coordinates as average of all station coordinates
            total_lat = sum(s.coordinates[0] for s in cell_stations)
            total_lon = sum(s.coordinates[1] for s in cell_stations)
            center_lat = total_lat / len(cell_stations)
            center_lon = total_lon / len(cell_stations)
            
            # Calculate average AQI from stations with valid AQI data
            stations_with_aqi = [s for s in cell_stations if s.current_aqi is not None]
            
            if stations_with_aqi:
                # Calculate average AQI
                avg_aqi = sum(s.current_aqi for s in stations_with_aqi) / len(stations_with_aqi)
                avg_aqi_int = int(round(avg_aqi))
                
                # Get color for average AQI
                aqi_color = Config.get_aqi_color(avg_aqi_int)
            else:
                # No stations have AQI data - use neutral values
                avg_aqi_int = 0
                aqi_color = '#CCCCCC'  # Gray for no data
            
            # Create cluster object
            cluster = MarkerCluster(
                center_coordinates=(center_lat, center_lon),
                station_count=len(cell_stations),
                avg_aqi=avg_aqi_int,
                aqi_color=aqi_color,
                stations=cell_stations
            )
            
            result.append(cluster)
    
    return result


def generate_tooltip(marker: 'StationSummary | MarkerCluster') -> str:
    """
    Generate HTML tooltip content for station marker or cluster.
    
    Creates formatted HTML tooltip that displays relevant information
    when users hover over markers on the globe visualization. Handles
    both individual stations and clustered markers, with graceful
    handling of missing data.
    
    For StationSummary markers:
    - Station name
    - Current AQI value and category
    - Last update timestamp
    - "No recent data" message if AQI unavailable
    
    For MarkerCluster markers:
    - Number of stations in cluster
    - Average AQI value
    - AQI category based on average
    
    The HTML is styled inline for compatibility with pydeck tooltips.
    
    Args:
        marker: Either a StationSummary or MarkerCluster object
    
    Returns:
        Formatted HTML string ready for display in tooltip
    
    Requirements: 13.8
    """
    from src.models import StationSummary, MarkerCluster
    from src.config import Config
    
    # Check if this is a cluster or individual station
    if isinstance(marker, MarkerCluster):
        # Generate tooltip for cluster
        # Get category name from average AQI
        category = Config.get_aqi_category_name(marker.avg_aqi)
        
        html = f"""
        <div style="font-family: Arial, sans-serif; padding: 8px; max-width: 250px;">
            <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #333;">
                Cluster of {marker.station_count} stations
            </div>
            <div style="font-size: 12px; color: #666; margin-bottom: 2px;">
                Average AQI: <span style="font-weight: bold; color: {marker.aqi_color};">{marker.avg_aqi}</span>
            </div>
            <div style="font-size: 11px; color: #888;">
                Category: {category}
            </div>
        </div>
        """
        
    elif isinstance(marker, StationSummary):
        # Generate tooltip for individual station
        if marker.current_aqi is not None:
            # Station has recent data
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 8px; max-width: 250px;">
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #333;">
                    {marker.name}
                </div>
                <div style="font-size: 12px; color: #666; margin-bottom: 2px;">
                    AQI: <span style="font-weight: bold; color: {marker.aqi_color};">{marker.current_aqi}</span>
                </div>
                <div style="font-size: 11px; color: #888; margin-bottom: 2px;">
                    Category: {marker.aqi_category}
                </div>
            """
            
            # Add last update time if available
            if marker.last_updated:
                # Format timestamp in a readable way
                time_str = marker.last_updated.strftime("%Y-%m-%d %H:%M UTC")
                html += f"""
                <div style="font-size: 10px; color: #999; margin-top: 4px;">
                    Updated: {time_str}
                </div>
                """
            
            html += "</div>"
            
        else:
            # Station has no recent data
            html = f"""
            <div style="font-family: Arial, sans-serif; padding: 8px; max-width: 250px;">
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #333;">
                    {marker.name}
                </div>
                <div style="font-size: 12px; color: #999; font-style: italic;">
                    No recent data
                </div>
            </div>
            """
    else:
        # Unknown marker type - return generic message
        html = """
        <div style="font-family: Arial, sans-serif; padding: 8px;">
            <div style="font-size: 12px; color: #666;">
                Air quality monitoring station
            </div>
        </div>
        """
    
    return html.strip()


def handle_marker_click(marker: 'StationSummary | MarkerCluster') -> 'Location':
    """
    Process click event on a station marker or cluster.

    When a user clicks on a marker in the globe visualization, this function
    converts the marker data into a Location object that can be used to fetch
    detailed air quality data. This enables the click-to-select workflow where
    users can explore the globe and click on any location to see details.

    For StationSummary markers:
    - Creates Location directly from station data
    - Uses station name, coordinates, and country
    - Providers list is set to empty (will be populated by data fetcher)

    For MarkerCluster markers:
    - Selects a representative station from the cluster
    - Strategy: Choose station with highest AQI (most critical data)
    - Falls back to first station if no stations have AQI data
    - Creates Location from selected station

    The returned Location object can be passed to data_fetcher functions
    to retrieve current measurements, historical data, and generate
    recommendations.

    Args:
        marker: Either a StationSummary or MarkerCluster object representing
               the clicked marker on the globe

    Returns:
        Location object with name, coordinates, country, and providers.
        This can be used with data_fetcher.get_current_measurements() and
        other data fetching functions.

    Raises:
        ValueError: If marker is neither StationSummary nor MarkerCluster,
                   or if a cluster has no stations

    Requirements: 13.2, 13.5
    """
    from src.models import StationSummary, MarkerCluster, Location

    if isinstance(marker, StationSummary):
        # Direct conversion from station to location
        # The station already has all the information we need
        location = Location(
            name=marker.name,
            coordinates=marker.coordinates,
            country=marker.country,
            providers=[]  # Will be populated by data fetcher when needed
        )
        return location

    elif isinstance(marker, MarkerCluster):
        # Need to select a representative station from the cluster
        # Handle edge case: empty cluster
        if not marker.stations:
            raise ValueError("Cannot handle click on empty cluster")

        # Strategy: Select station with highest AQI (most critical/interesting)
        # This gives users the most important information from the cluster
        stations_with_aqi = [
            s for s in marker.stations
            if s.current_aqi is not None
        ]

        if stations_with_aqi:
            # Select station with highest AQI
            selected_station = max(
                stations_with_aqi,
                key=lambda s: s.current_aqi
            )
        else:
            # No stations have AQI data - just use the first station
            # This ensures we can still select a location even without data
            selected_station = marker.stations[0]

        # Create Location from selected station
        location = Location(
            name=selected_station.name,
            coordinates=selected_station.coordinates,
            country=selected_station.country,
            providers=[]  # Will be populated by data fetcher when needed
        )
        return location

    else:
        # Unknown marker type
        raise ValueError(
            f"Invalid marker type: {type(marker).__name__}. "
            f"Expected StationSummary or MarkerCluster."
        )



def handle_marker_click(marker: 'StationSummary | MarkerCluster') -> 'Location':
    """
    Process click event on a station marker or cluster.
    
    When a user clicks on a marker in the globe visualization, this function
    converts the marker data into a Location object that can be used to fetch
    detailed air quality data. This enables the click-to-select workflow where
    users can explore the globe and click on any location to see details.
    
    For StationSummary markers:
    - Creates Location directly from station data
    - Uses station name, coordinates, and country
    - Providers list is set to empty (will be populated by data fetcher)
    
    For MarkerCluster markers:
    - Selects a representative station from the cluster
    - Strategy: Choose station with highest AQI (most critical data)
    - Falls back to first station if no stations have AQI data
    - Creates Location from selected station
    
    The returned Location object can be passed to data_fetcher functions
    to retrieve current measurements, historical data, and generate
    recommendations.
    
    Args:
        marker: Either a StationSummary or MarkerCluster object representing
               the clicked marker on the globe
    
    Returns:
        Location object with name, coordinates, country, and providers.
        This can be used with data_fetcher.get_current_measurements() and
        other data fetching functions.
    
    Raises:
        ValueError: If marker is neither StationSummary nor MarkerCluster,
                   or if a cluster has no stations
    
    Requirements: 13.2, 13.5
    """
    from src.models import StationSummary, MarkerCluster, Location
    
    if isinstance(marker, StationSummary):
        # Direct conversion from station to location
        # The station already has all the information we need
        location = Location(
            name=marker.name,
            coordinates=marker.coordinates,
            country=marker.country,
            providers=[]  # Will be populated by data fetcher when needed
        )
        return location
    
    elif isinstance(marker, MarkerCluster):
        # Need to select a representative station from the cluster
        # Handle edge case: empty cluster
        if not marker.stations:
            raise ValueError("Cannot handle click on empty cluster")
        
        # Strategy: Select station with highest AQI (most critical/interesting)
        # This gives users the most important information from the cluster
        stations_with_aqi = [
            s for s in marker.stations 
            if s.current_aqi is not None
        ]
        
        if stations_with_aqi:
            # Select station with highest AQI
            selected_station = max(
                stations_with_aqi,
                key=lambda s: s.current_aqi
            )
        else:
            # No stations have AQI data - just use the first station
            # This ensures we can still select a location even without data
            selected_station = marker.stations[0]
        
        # Create Location from selected station
        location = Location(
            name=selected_station.name,
            coordinates=selected_station.coordinates,
            country=selected_station.country,
            providers=[]  # Will be populated by data fetcher when needed
        )
        return location
    
    else:
        # Unknown marker type
        raise ValueError(
            f"Invalid marker type: {type(marker).__name__}. "
            f"Expected StationSummary or MarkerCluster."
        )


def render_globe(state: 'GlobeState', stations: list['StationSummary']) -> 'pdk.Deck':
    """
    Render the interactive globe/map visualization using pydeck.

    This is the main rendering function that ties everything together. It takes
    the current globe state and list of stations, applies clustering based on
    zoom level, creates a pydeck Deck with ScatterplotLayer for markers, and
    configures all visualization settings.

    The function creates a WebGL-based visualization with:
    - Color-coded markers based on AQI categories
    - Marker clustering at lower zoom levels for performance
    - Interactive tooltips showing station information
    - Smooth zoom, pan, and rotation controls
    - Marker instancing for efficient rendering

    Performance optimizations:
    - Uses marker instancing to reduce draw calls
    - Applies clustering to reduce marker count at low zoom
    - Configures pydeck for 30+ FPS animations
    - Uses ScatterplotLayer for hardware-accelerated rendering

    Args:
        state: GlobeState object with center coordinates, zoom level, and rotation
        stations: List of StationSummary objects to render as markers

    Returns:
        pydeck.Deck object that can be rendered in Streamlit using st.pydeck_chart()

    Requirements: 13.1, 13.3, 13.6, 13.9, 13.11, 13.12
    """
    import pydeck as pdk
    from src.models import StationSummary, MarkerCluster
    from src.config import Config

    # Apply marker clustering based on zoom level
    # This reduces the number of markers at lower zoom levels for better performance
    markers = cluster_markers(stations, state.zoom_level)

    # Prepare data for pydeck ScatterplotLayer
    # We need to convert our markers to a list of dicts with required fields
    marker_data = []

    for marker in markers:
        if isinstance(marker, StationSummary):
            # Individual station marker
            lat, lon = marker.coordinates

            # Use station's AQI color, or gray if no data
            if marker.current_aqi is not None:
                color = _hex_to_rgb(marker.aqi_color)
                radius = 50000  # Base radius for individual stations
            else:
                color = [200, 200, 200]  # Gray for no data
                radius = 30000  # Smaller radius for stations without data

            marker_data.append({
                'position': [lon, lat],  # pydeck uses [lon, lat] order
                'color': color,
                'radius': radius,
                'tooltip': generate_tooltip(marker),
                'marker_type': 'station',
                'marker_object': marker  # Store for click handling
            })

        elif isinstance(marker, MarkerCluster):
            # Cluster marker
            lat, lon = marker.center_coordinates
            color = _hex_to_rgb(marker.aqi_color)

            # Scale cluster radius based on station count
            # Larger clusters get bigger markers
            base_radius = 80000
            radius = base_radius + (marker.station_count * 1000)
            radius = min(radius, 200000)  # Cap maximum radius

            marker_data.append({
                'position': [lon, lat],
                'color': color,
                'radius': radius,
                'tooltip': generate_tooltip(marker),
                'marker_type': 'cluster',
                'marker_object': marker  # Store for click handling
            })

    # Create ScatterplotLayer for markers
    # ScatterplotLayer uses WebGL for hardware-accelerated rendering
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=marker_data,
        get_position='position',
        get_color='color',
        get_radius='radius',
        pickable=True,  # Enable click and hover interactions
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=1,
        radius_min_pixels=3,  # Minimum pixel size for markers
        radius_max_pixels=50,  # Maximum pixel size for markers
        line_width_min_pixels=1,
        get_line_color=[255, 255, 255],  # White outline for visibility
    )

    # Configure view state
    # This determines the camera position and orientation
    view_state = pdk.ViewState(
        latitude=state.center_lat,
        longitude=state.center_lon,
        zoom=state.zoom_level,
        pitch=0,  # 0 = top-down view, 60 = angled view
        bearing=state.rotation,  # Rotation in degrees
        min_zoom=0,
        max_zoom=Config.GLOBE_MAX_ZOOM,
    )

    # Create the Deck
    # This is the main pydeck object that Streamlit will render
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            'html': '{tooltip}',
            'style': {
                'backgroundColor': 'white',
                'color': 'black',
                'border': '1px solid #ccc',
                'borderRadius': '4px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            }
        },
        map_style='mapbox://styles/mapbox/light-v10',  # Light base map
        # Performance settings for smooth animations (30+ FPS target)
        parameters={
            'clearColor': [0.95, 0.95, 0.95, 1],  # Light gray background
        }
    )

    return deck


def _hex_to_rgb(hex_color: str) -> list[int]:
    """
    Convert hex color code to RGB list for pydeck.

    pydeck expects colors as [R, G, B] or [R, G, B, A] lists with values 0-255.
    This helper converts our hex color codes (e.g., '#FF0000') to that format.

    Args:
        hex_color: Hex color code string (e.g., '#FF0000' or 'FF0000')

    Returns:
        List of [R, G, B] integers in range 0-255

    Examples:
        >>> _hex_to_rgb('#FF0000')
        [255, 0, 0]
        >>> _hex_to_rgb('#00E400')
        [0, 228, 0]
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return [r, g, b]



def render_globe(state: 'GlobeState', stations: list['StationSummary']) -> 'pdk.Deck':
    """
    Render the interactive globe/map visualization using pydeck.

    This is the main rendering function that ties everything together. It takes
    the current globe state and list of stations, applies clustering based on
    zoom level, creates a pydeck Deck with ScatterplotLayer for markers, and
    configures all visualization settings.

    The function creates a WebGL-based visualization with:
    - Color-coded markers based on AQI categories
    - Marker clustering at lower zoom levels for performance
    - Interactive tooltips showing station information
    - Smooth zoom, pan, and rotation controls
    - Marker instancing for efficient rendering

    Performance optimizations:
    - Uses marker instancing to reduce draw calls
    - Applies clustering to reduce marker count at low zoom
    - Configures pydeck for 30+ FPS animations
    - Uses ScatterplotLayer for hardware-accelerated rendering

    Args:
        state: GlobeState object with center coordinates, zoom level, and rotation
        stations: List of StationSummary objects to render as markers

    Returns:
        pydeck.Deck object that can be rendered in Streamlit using st.pydeck_chart()

    Requirements: 13.1, 13.3, 13.6, 13.9, 13.11, 13.12
    """
    import pydeck as pdk
    from src.models import StationSummary, MarkerCluster
    from src.config import Config

    # Apply marker clustering based on zoom level
    # This reduces the number of markers at lower zoom levels for better performance
    markers = cluster_markers(stations, state.zoom_level)

    # Prepare data for pydeck ScatterplotLayer
    # We need to convert our markers to a list of dicts with required fields
    marker_data = []

    for marker in markers:
        if isinstance(marker, StationSummary):
            # Individual station marker
            lat, lon = marker.coordinates

            # Use station's AQI color, or gray if no data
            if marker.current_aqi is not None:
                color = _hex_to_rgb(marker.aqi_color)
                radius = 50000  # Base radius for individual stations
            else:
                color = [200, 200, 200]  # Gray for no data
                radius = 30000  # Smaller radius for stations without data

            marker_data.append({
                'position': [lon, lat],  # pydeck uses [lon, lat] order
                'color': color,
                'radius': radius,
                'tooltip': generate_tooltip(marker),
                'marker_type': 'station',
                'marker_object': marker  # Store for click handling
            })

        elif isinstance(marker, MarkerCluster):
            # Cluster marker
            lat, lon = marker.center_coordinates
            color = _hex_to_rgb(marker.aqi_color)

            # Scale cluster radius based on station count
            # Larger clusters get bigger markers
            base_radius = 80000
            radius = base_radius + (marker.station_count * 1000)
            radius = min(radius, 200000)  # Cap maximum radius

            marker_data.append({
                'position': [lon, lat],
                'color': color,
                'radius': radius,
                'tooltip': generate_tooltip(marker),
                'marker_type': 'cluster',
                'marker_object': marker  # Store for click handling
            })

    # Create ScatterplotLayer for markers
    # ScatterplotLayer uses WebGL for hardware-accelerated rendering
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=marker_data,
        get_position='position',
        get_color='color',
        get_radius='radius',
        pickable=True,  # Enable click and hover interactions
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=1,
        radius_min_pixels=3,  # Minimum pixel size for markers
        radius_max_pixels=50,  # Maximum pixel size for markers
        line_width_min_pixels=1,
        get_line_color=[255, 255, 255],  # White outline for visibility
    )

    # Configure view state
    # This determines the camera position and orientation
    view_state = pdk.ViewState(
        latitude=state.center_lat,
        longitude=state.center_lon,
        zoom=state.zoom_level,
        pitch=0,  # 0 = top-down view, 60 = angled view
        bearing=state.rotation,  # Rotation in degrees
        min_zoom=0,
        max_zoom=Config.GLOBE_MAX_ZOOM,
    )

    # Create the Deck
    # This is the main pydeck object that Streamlit will render
    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            'html': '{tooltip}',
            'style': {
                'backgroundColor': 'white',
                'color': 'black',
                'border': '1px solid #ccc',
                'borderRadius': '4px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            }
        },
        map_style='mapbox://styles/mapbox/light-v10',  # Light base map
        # Performance settings for smooth animations (30+ FPS target)
        parameters={
            'clearColor': [0.95, 0.95, 0.95, 1],  # Light gray background
        }
    )

    return deck


def _hex_to_rgb(hex_color: str) -> list[int]:
    """
    Convert hex color code to RGB list for pydeck.

    pydeck expects colors as [R, G, B] or [R, G, B, A] lists with values 0-255.
    This helper converts our hex color codes (e.g., '#FF0000') to that format.

    Args:
        hex_color: Hex color code string (e.g., '#FF0000' or 'FF0000')

    Returns:
        List of [R, G, B] integers in range 0-255

    Examples:
        >>> _hex_to_rgb('#FF0000')
        [255, 0, 0]
        >>> _hex_to_rgb('#00E400')
        [0, 228, 0]
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return [r, g, b]
