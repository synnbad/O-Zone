"""
AQI Calculator module for O-Zone MVP.

This module implements the EPA AQI calculation algorithm for converting
pollutant concentrations to standardized AQI values.
"""

from datetime import datetime
from typing import Optional

from src.config import Config
from src.models import Measurement, AQIResult, OverallAQI


def calculate_aqi(pollutant: str, concentration: float, unit: str) -> AQIResult:
    """
    Calculate AQI for a single pollutant using EPA formula.
    
    The EPA AQI formula is:
    AQI = ((I_high - I_low) / (C_high - C_low)) * (C - C_low) + I_low
    
    Where:
    - I_high, I_low: AQI breakpoint values
    - C_high, C_low: Concentration breakpoint values
    - C: Measured concentration
    
    Args:
        pollutant: Pollutant name (PM2.5, PM10, CO, NO2, O3, SO2)
        concentration: Measured concentration value
        unit: Unit of measurement
        
    Returns:
        AQIResult with calculated AQI, category, and color
        
    Raises:
        ValueError: If concentration is out of valid range or pollutant unknown
    """
    # Validate pollutant
    if pollutant not in Config.AQI_BREAKPOINTS:
        raise ValueError(
            f"Unknown pollutant: {pollutant}. "
            f"Must be one of {list(Config.AQI_BREAKPOINTS.keys())}"
        )
    
    # Validate concentration
    if concentration < 0:
        raise ValueError(
            f"Invalid concentration for {pollutant}: {concentration}. "
            f"Concentration must be non-negative."
        )
    
    # Get breakpoints for this pollutant
    breakpoints = Config.AQI_BREAKPOINTS[pollutant]
    
    # Find the appropriate breakpoint range
    breakpoint_found = None
    for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
        if bp_low <= concentration <= bp_high:
            breakpoint_found = (bp_low, bp_high, aqi_low, aqi_high)
            break
    
    if breakpoint_found is None:
        # Concentration is out of range
        max_concentration = breakpoints[-1][1]
        raise ValueError(
            f"Concentration {concentration} {unit} for {pollutant} is out of valid range. "
            f"Maximum supported concentration is {max_concentration} {unit}."
        )
    
    # Apply EPA AQI formula
    c_low, c_high, i_low, i_high = breakpoint_found
    
    if c_high == c_low:
        # Edge case: avoid division by zero
        aqi = i_low
    else:
        aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
    
    # Round to nearest integer
    aqi = round(aqi)
    
    # Ensure AQI is within valid range
    aqi = max(0, min(500, aqi))
    
    # Get category and color
    category, color = get_aqi_category(aqi)
    
    return AQIResult(
        pollutant=pollutant,
        concentration=concentration,
        aqi=aqi,
        category=category,
        color=color
    )


def get_aqi_category(aqi: int) -> tuple[str, str]:
    """
    Map AQI value to category name and color.
    
    Args:
        aqi: AQI value (0-500)
        
    Returns:
        Tuple of (category_name, hex_color_code)
    """
    for category, (low, high, color, _) in Config.AQI_CATEGORIES.items():
        if low <= aqi <= high:
            return category, color
    
    # Default to Hazardous for values > 500
    return 'Hazardous', Config.AQI_CATEGORIES['Hazardous'][2]


def calculate_overall_aqi(measurements: list[Measurement]) -> OverallAQI:
    """
    Calculate overall AQI from multiple pollutant measurements.
    
    The overall AQI is the maximum of all individual pollutant AQIs.
    The dominant pollutant is the one with the highest AQI.
    
    Args:
        measurements: List of Measurement objects
        
    Returns:
        OverallAQI object with overall assessment
        
    Raises:
        ValueError: If measurements list is empty
    """
    if not measurements:
        raise ValueError("Cannot calculate overall AQI: measurements list is empty")
    
    # Calculate individual AQI for each pollutant
    individual_results = []
    for measurement in measurements:
        try:
            aqi_result = calculate_aqi(
                measurement.pollutant,
                measurement.value,
                measurement.unit
            )
            individual_results.append(aqi_result)
        except ValueError as e:
            # Log error but continue with other pollutants
            print(f"Warning: Could not calculate AQI for {measurement.pollutant}: {e}")
            continue
    
    if not individual_results:
        raise ValueError(
            "Cannot calculate overall AQI: no valid AQI results from measurements"
        )
    
    # Find maximum AQI and dominant pollutant
    max_aqi_result = max(individual_results, key=lambda r: r.aqi)
    overall_aqi_value = max_aqi_result.aqi
    dominant_pollutant = max_aqi_result.pollutant
    
    # Get category and color for overall AQI
    category, color = get_aqi_category(overall_aqi_value)
    
    # Get most recent timestamp
    most_recent_timestamp = max(m.timestamp for m in measurements)
    
    # Get location from first measurement (all should be same location)
    location = measurements[0].location
    
    return OverallAQI(
        aqi=overall_aqi_value,
        category=category,
        color=color,
        dominant_pollutant=dominant_pollutant,
        individual_results=individual_results,
        timestamp=most_recent_timestamp,
        location=location
    )
