"""Test the hybrid location resolution system."""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data_fetcher import get_location

# Test cases
test_queries = [
    "Paris",           # Should use geocoding
    "Tokyo",           # Should use geocoding
    "NYC",             # Should use AI (abbreviation)
    "SF",              # Should use AI (abbreviation)
    "London",          # Should use geocoding
    "40.7128,-74.0060" # Coordinates (New York)
]

print("Testing Hybrid Location Resolution")
print("=" * 60)

for query in test_queries:
    print(f"\nQuery: '{query}'")
    location = get_location(query)
    
    if location:
        print(f"✓ Found: {location.name}, {location.country}")
        print(f"  Coordinates: {location.coordinates}")
        print(f"  Provider: {', '.join(location.providers)}")
    else:
        print(f"✗ Not found")

print("\n" + "=" * 60)
print("Test complete!")
