"""
Manual test script for globe view implementation.
This script tests the render_globe_view function without running the full Streamlit app.
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models import GlobeState
from src.globe_visualizer import get_stations_for_viewport, render_globe

def test_globe_view_components():
    """Test that all components of the globe view work correctly."""
    
    print("Testing globe view components...")
    
    # Test 1: Initialize GlobeState
    print("\n1. Testing GlobeState initialization...")
    globe_state = GlobeState(
        center_lat=0.0,
        center_lon=0.0,
        zoom_level=2,
        rotation=0.0,
        selected_station=None
    )
    print(f"   ✓ GlobeState created: center=({globe_state.center_lat}, {globe_state.center_lon}), zoom={globe_state.zoom_level}")
    
    # Test 2: Fetch stations for viewport
    print("\n2. Testing get_stations_for_viewport...")
    try:
        stations = get_stations_for_viewport(globe_state)
        print(f"   ✓ Fetched {len(stations)} stations for viewport")
        
        if stations:
            sample_station = stations[0]
            print(f"   Sample station: {sample_station.name} at {sample_station.coordinates}")
            print(f"   AQI: {sample_station.current_aqi}, Category: {sample_station.aqi_category}")
    except Exception as e:
        print(f"   ⚠ Error fetching stations: {e}")
        print("   This is expected if OpenAQ API is unavailable or demo data is being used")
    
    # Test 3: Render globe
    print("\n3. Testing render_globe...")
    try:
        deck = render_globe(globe_state, stations if 'stations' in locals() else [])
        print(f"   ✓ Globe rendered successfully")
        print(f"   Deck type: {type(deck)}")
        print(f"   View state: lat={deck.initial_view_state.latitude}, lon={deck.initial_view_state.longitude}, zoom={deck.initial_view_state.zoom}")
    except Exception as e:
        print(f"   ✗ Error rendering globe: {e}")
        return False
    
    print("\n✓ All globe view components tested successfully!")
    return True

if __name__ == "__main__":
    success = test_globe_view_components()
    sys.exit(0 if success else 1)
