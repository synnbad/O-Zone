"""Test AI-generated AQI data."""
import sys
import os

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_fetcher import get_location, get_current_measurements
from src.aqi_calculator import calculate_overall_aqi

# Test with Tallahassee (not in demo data)
print("Testing AI-Generated AQI Data")
print("=" * 60)

location = get_location("Tallahassee")
if location:
    print(f"\nLocation: {location.name}, {location.country}")
    print(f"Coordinates: {location.coordinates}")
    print(f"Provider: {', '.join(location.providers)}")
    
    print("\nFetching air quality data...")
    measurements = get_current_measurements(location)
    
    if measurements:
        print(f"\n✓ Got {len(measurements)} measurements:")
        for m in measurements:
            print(f"  {m.pollutant}: {m.value:.2f} {m.unit}")
        
        # Calculate overall AQI
        overall_aqi = calculate_overall_aqi(measurements)
        print(f"\nOverall AQI: {overall_aqi.aqi} ({overall_aqi.category})")
        print(f"Dominant Pollutant: {overall_aqi.dominant_pollutant}")
    else:
        print("✗ No measurements available")
else:
    print("✗ Location not found")

print("\n" + "=" * 60)
