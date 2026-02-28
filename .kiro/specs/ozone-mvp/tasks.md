# Implementation Plan: O-Zone MVP

## Overview

This implementation plan breaks down the O-Zone MVP into discrete coding tasks following a phased approach. The system integrates real-time air quality data from OpenAQ with AI-powered recommendations via Amazon Bedrock, featuring an interactive globe visualization for exploring global air quality data.

The implementation follows 6 phases: Project Setup, AQI Calculator, Data Fetcher, Bedrock Client, Globe Visualizer, and Streamlit UI. Each phase builds incrementally with testing integrated throughout to catch errors early.

## Tasks

- [x] 1. Project setup and configuration
  - Create project directory structure (src/, tests/unit/, tests/property/, tests/integration/)
  - Create requirements.txt with dependencies: streamlit, boto3, httpx, pandas, pydeck, python-dotenv, pytest, hypothesis
  - Create .env.example template with required environment variables (OPENAQ_API_KEY, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
  - Create src/config.py with all configuration constants (API endpoints, cache TTL, AQI breakpoints, globe settings, activity/health options)
  - Implement Config.validate() method to check required environment variables and configuration structure
  - Create tests/conftest.py with shared fixtures and mocks for OpenAQ and Bedrock APIs
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 2. Implement AQI Calculator module
  - [x] 2.1 Create core data models for AQI calculation
    - Create src/models.py with dataclasses: AQIResult, OverallAQI, Measurement, Location
    - Add JSON serialization methods (to_json, from_json) to all dataclasses
    - Add validation logic to ensure AQI values are 0-500, coordinates are valid ranges
    - _Requirements: 2.4, 11.3_

  - [ ]* 2.2 Write property test for measurement serialization
    - **Property 23: Measurement Serialization Round-Trip**
    - **Validates: Requirements 11.4**

  - [x] 2.3 Implement AQI breakpoint tables and calculation logic
    - Add AQI_BREAKPOINTS dictionary to config.py for all 6 pollutants (PM2.5, PM10, CO, NO2, O3, SO2)
    - Add AQI_CATEGORIES dictionary mapping AQI ranges to category names and colors
    - Create src/aqi_calculator.py with calculate_aqi function implementing EPA formula
    - Implement get_aqi_category function to map AQI values to categories and colors
    - Add error handling for out-of-range concentrations with descriptive ValueError messages
    - _Requirements: 2.1, 2.2, 2.4, 2.5, 3.1_

  - [ ]* 2.4 Write property tests for AQI calculation
    - **Property 2: AQI Calculation Validity**
    - **Validates: Requirements 2.1, 2.2, 2.4**

  - [ ]* 2.5 Write property test for out-of-range handling
    - **Property 4: Out-of-Range Concentration Error Handling**
    - **Validates: Requirements 2.5**

  - [ ]* 2.6 Write property test for color coding consistency
    - **Property 5: AQI Color Coding Consistency**
    - **Validates: Requirements 3.1, 7.3, Usability.3**

  - [x] 2.7 Implement overall AQI calculation
    - Implement calculate_overall_aqi function that takes list of Measurement objects
    - Calculate individual AQI for each pollutant using calculate_aqi
    - Determine overall AQI as maximum of individual AQIs
    - Identify dominant pollutant (one with highest AQI)
    - Return OverallAQI object with all details
    - Handle partial pollutant data (calculate with available pollutants only)
    - _Requirements: 2.3, 8.1_

  - [ ]* 2.8 Write property test for overall AQI maximum rule
    - **Property 3: Overall AQI Maximum Rule**
    - **Validates: Requirements 2.3**

  - [ ]* 2.9 Write property test for partial pollutant data handling
    - **Property 11: Partial Pollutant Data Handling**
    - **Validates: Requirements 8.1**

  - [ ]* 2.10 Write unit tests for AQI calculator
    - Test AQI calculation for boundary values (e.g., PM2.5 = 35.4 μg/m³)
    - Test overall AQI with multiple pollutants
    - Test error for negative concentration
    - Test single pollutant AQI calculation
    - Test all six pollutant types

- [x] 3. Checkpoint - Ensure AQI calculator tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement Data Fetcher module
  - [x] 4.1 Create data fetcher with OpenAQ API client
    - Create src/data_fetcher.py with _call_openaq_api helper function
    - Implement authentication and request formatting for OpenAQ API v3
    - Implement retry logic (1 retry with 1 second delay on failure)
    - Add error handling with descriptive exceptions for API errors
    - _Requirements: 1.1, 1.3, Reliability.2_

  - [ ]* 4.2 Write property test for API response validation
    - **Property 29: API Response Validation**
    - **Validates: Requirements Reliability.5**

  - [x] 4.3 Implement location resolution
    - Implement get_location function to resolve location queries to Location objects
    - Support city name, coordinates, and region identifier formats
    - Return None if location not found
    - Implement in-memory caching for successful resolutions
    - _Requirements: 9.1, 9.2_

  - [ ]* 4.4 Write property tests for location input
    - **Property 15: Location Input Format Support**
    - **Validates: Requirements 9.1**

  - [ ]* 4.5 Write property test for location validation
    - **Property 16: Location Validation Response**
    - **Validates: Requirements 9.2**

  - [ ]* 4.6 Write property test for location not found errors
    - **Property 17: Location Not Found Error with Suggestions**
    - **Validates: Requirements 9.3**

  - [x] 4.7 Implement current measurements retrieval
    - Implement get_current_measurements function to fetch latest measurements for all pollutants
    - Filter measurements within last 3 hours (DATA_FRESHNESS_HOURS)
    - Return empty list if no recent data available
    - Implement 15-minute cache per location using in-memory dict with TTL
    - _Requirements: 1.1, 1.2, 8.5, Performance.4_

  - [ ]* 4.8 Write property test for measurement structure
    - **Property 1: Measurement Structure Completeness**
    - **Validates: Requirements 1.2, 1.5, 11.3**

  - [ ]* 4.9 Write property test for stale data marking
    - **Property 14: Stale Data Marking**
    - **Validates: Requirements 8.5**

  - [ ]* 4.10 Write property test for cache behavior
    - **Property 26: Cache Behavior**
    - **Validates: Requirements Performance.4**

  - [x] 4.11 Implement historical measurements retrieval
    - Implement get_historical_measurements function to fetch time-series data
    - Accept location and hours parameter (24 or 168 for 7 days)
    - Return dict mapping pollutant names to list of Measurement objects
    - Implement caching with time-range-specific keys
    - _Requirements: 7.1, 7.2, 8.3_

  - [x] 4.12 Implement unit conversion and data parsing
    - Implement unit conversion to standard units (μg/m³ for particulates, ppm for gases)
    - Parse OpenAQ JSON responses into Measurement objects
    - Validate that parsed measurements include required fields
    - Handle invalid API responses with parsing errors
    - _Requirements: 11.1, 11.2, 11.5_

  - [ ]* 4.13 Write property test for OpenAQ response parsing
    - **Property 21: OpenAQ Response Parsing**
    - **Validates: Requirements 11.1**

  - [ ]* 4.14 Write property test for unit normalization
    - **Property 22: Unit Normalization**
    - **Validates: Requirements 11.2**

  - [ ]* 4.15 Write property test for invalid API response handling
    - **Property 24: Invalid API Response Error Handling**
    - **Validates: Requirements 11.5**

  - [ ]* 4.16 Write property test for data fetcher error messages
    - **Property 30: Data Fetcher Error Messages**
    - **Validates: Requirements 1.3**

  - [x] 4.17 Implement global stations retrieval for globe view
    - Implement get_global_stations function to fetch all monitoring stations
    - Support optional GeoBounds parameter for viewport-based filtering
    - Return list of StationSummary objects with station metadata and latest AQI
    - Implement aggressive caching (1 hour TTL) due to data volume
    - _Requirements: 13.1, 13.7_

  - [ ]* 4.18 Write unit tests for data fetcher
    - Test successful location resolution for "San Francisco"
    - Test empty result when no measurements available
    - Test API error handling with 500 status code
    - Test caching behavior with repeated queries
    - Test unit conversion from mg/m³ to μg/m³

- [x] 5. Checkpoint - Ensure data fetcher tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Bedrock Client module
  - [x] 6.1 Create prompt templates
    - Create src/prompts.py with RECOMMENDATION_PROMPT_TEMPLATE constant
    - Include placeholders for AQI data, activity, health sensitivity, historical context
    - Add template formatting helper functions
    - _Requirements: 10.2, 10.3_

  - [x] 6.2 Create recommendation data models
    - Add RecommendationResponse and TimeWindow dataclasses to src/models.py
    - Add JSON serialization support for these models
    - Add validation for safety_assessment enum values
    - _Requirements: 5.2, 6.3_

  - [ ]* 6.3 Write property test for safety assessment enumeration
    - **Property 6: Safety Assessment Enumeration**
    - **Validates: Requirements 5.2**

  - [ ]* 6.4 Write property test for TimeWindow structure
    - **Property 9: TimeWindow Structure and Ordering**
    - **Validates: Requirements 6.3, 6.5**

  - [x] 6.5 Implement Bedrock client with AWS authentication
    - Create src/bedrock_client.py with _call_bedrock helper function
    - Implement AWS authentication using boto3 with credentials from environment
    - Use bedrock-runtime:InvokeModel API with Claude 3.5 Sonnet model ID
    - Set temperature=0.7 for balanced creativity/consistency
    - Return raw response text
    - _Requirements: 10.1_

  - [x] 6.6 Implement prompt construction
    - Implement _construct_prompt function to build structured prompts
    - Load template from prompts.py and inject current AQI data
    - Include activity profile, health sensitivity, and historical trends
    - Format as structured prompt for Claude
    - _Requirements: 10.2, 10.3_

  - [ ]* 6.7 Write property test for prompt completeness
    - **Property 18: Bedrock Prompt Completeness**
    - **Validates: Requirements 10.2, 10.3**

  - [x] 6.8 Implement response parsing
    - Implement _parse_response function to extract JSON from Claude response
    - Validate required fields present (safety_assessment, recommendation_text, precautions, time_windows, reasoning)
    - Convert strings to appropriate types (datetime, enums)
    - Handle malformed responses gracefully with error messages
    - _Requirements: 10.5_

  - [ ]* 6.9 Write property test for Bedrock response parsing
    - **Property 20: Bedrock Response Parsing**
    - **Validates: Requirements 10.5**

  - [x] 6.10 Implement recommendation generation with retry logic
    - Implement get_recommendation function as main entry point
    - Call _construct_prompt, _call_bedrock, and _parse_response in sequence
    - Implement retry logic (1 retry on failure with exponential backoff)
    - Return error-state response if Bedrock unavailable after retry
    - Handle recommendations without historical data (pass None)
    - _Requirements: 5.1, 5.4, 5.5, 8.4, 10.4_

  - [ ]* 6.11 Write property test for Bedrock retry logic
    - **Property 19: Bedrock Retry Logic**
    - **Validates: Requirements 10.4**

  - [ ]* 6.12 Write property test for precautions for unsafe conditions
    - **Property 7: Precautions for Unsafe Conditions**
    - **Validates: Requirements 5.3**

  - [ ]* 6.13 Write property test for health sensitivity conservatism
    - **Property 8: Health Sensitivity Conservatism**
    - **Validates: Requirements 5.5**

  - [ ]* 6.14 Write property test for TimeWindow explanation when empty
    - **Property 10: TimeWindow Explanation When Empty**
    - **Validates: Requirements 6.4**

  - [ ]* 6.15 Write property test for recommendations without historical data
    - **Property 13: Recommendations Without Historical Data**
    - **Validates: Requirements 8.4**

  - [ ]* 6.16 Write property test for historical data prediction
    - **Property 32: Historical Data Prediction**
    - **Validates: Requirements 6.1**

  - [ ]* 6.17 Write unit tests for Bedrock client
    - Test prompt construction with all required fields
    - Test response parsing for valid JSON
    - Test retry logic with mocked API failure
    - Test graceful handling of malformed response
    - Test recommendation without historical data

- [x] 7. Checkpoint - Ensure Bedrock client tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Implement Globe Visualizer module
  - [x] 8.1 Create globe-specific data models
    - Add GeoBounds, StationSummary, GlobeState, MarkerCluster dataclasses to src/models.py
    - Add validation for coordinate ranges (lat: -90 to 90, lon: -180 to 180)
    - Add validation for zoom_level range (0 to 15)
    - _Requirements: 13.1, 13.7_

  - [x] 8.2 Implement viewport bounds calculation
    - Create src/globe_visualizer.py with calculate_zoom_bounds function
    - Calculate geographic bounds for given center point and zoom level
    - Account for map projection distortion at high latitudes
    - Return GeoBounds object
    - _Requirements: 13.7_

  - [x] 8.3 Implement optimal zoom level calculation
    - Implement get_optimal_zoom_level function to determine zoom for given bounds
    - Ensure selected location is prominently displayed
    - Return zoom level (0-15)
    - _Requirements: 13.5_

  - [x] 8.4 Implement station fetching for viewport
    - Implement get_stations_for_viewport function to retrieve stations for current view
    - Call data_fetcher.get_global_stations with bounds parameter
    - Calculate current AQI for each station using aqi_calculator
    - Return list of StationSummary objects
    - Implement viewport-based caching
    - _Requirements: 13.7_

  - [ ]* 8.5 Write property test for globe marker viewport rendering
    - **Property 33: Globe Marker Viewport Rendering**
    - **Validates: Requirements 13.7**

  - [x] 8.6 Implement marker clustering algorithm
    - Implement cluster_markers function with spatial clustering based on zoom level
    - Zoom 0-5: aggressive clustering (100+ stations per cluster)
    - Zoom 6-10: moderate clustering (10-50 stations per cluster)
    - Zoom 11+: minimal or no clustering (individual markers)
    - Use grid-based clustering for performance
    - Return mixed list of MarkerCluster and StationSummary objects
    - _Requirements: 13.12_

  - [x] 8.7 Implement tooltip generation
    - Implement generate_tooltip function to create HTML tooltip content
    - Include station name, current AQI, category, and last update time
    - Handle missing data gracefully (show "No recent data")
    - Return formatted HTML string
    - _Requirements: 13.8_

  - [ ]* 8.8 Write property test for globe marker tooltip completeness
    - **Property 35: Globe Marker Tooltip Completeness**
    - **Validates: Requirements 13.8**

  - [x] 8.9 Implement marker click handler
    - Implement handle_marker_click function to process click events
    - Retrieve full location details for the station
    - Return Location object for data fetching
    - _Requirements: 13.2, 13.5_

  - [ ]* 8.10 Write property test for globe click-to-location selection
    - **Property 34: Globe Click-to-Location Selection**
    - **Validates: Requirements 13.2, 13.5**

  - [x] 8.11 Implement globe rendering with pydeck
    - Implement render_globe function using pydeck for WebGL rendering
    - Apply marker clustering based on zoom level
    - Color-code markers by AQI category using standard colors
    - Configure zoom, pan, and rotation controls
    - Set up marker instancing for performance
    - Target 30+ FPS for smooth animations
    - _Requirements: 13.1, 13.3, 13.6, 13.9, 13.11, 13.12_

  - [ ]* 8.12 Write unit tests for globe visualizer
    - Test marker clustering at zoom level 3 (should cluster)
    - Test marker clustering at zoom level 12 (minimal clustering)
    - Test tooltip generation with complete station data
    - Test tooltip generation with missing AQI data
    - Test viewport bounds calculation for zoom level 5
    - Test click handler updates location correctly

- [x] 9. Checkpoint - Ensure globe visualizer tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement Streamlit UI
  - [x] 10.1 Create main app structure and session state
    - Create src/app.py with Streamlit page configuration
    - Initialize session state variables (location, current_aqi, activity, health_sensitivity, recommendation, historical_data, view_mode, globe_state, visible_stations)
    - Set default values for all session state variables
    - _Requirements: 9.5, Performance.1_

  - [x] 10.2 Implement location input section
    - Implement render_location_input function with text input field
    - Add search button to trigger location resolution
    - Display resolved location name and country
    - Display error messages for invalid locations
    - Add "Explore Globe" button to switch to globe view
    - Update session state with resolved location
    - _Requirements: 9.1, 9.3, 9.4, Usability.1, Usability.4_

  - [x] 10.3 Implement globe view section
    - Implement render_globe_view function to display interactive globe/map
    - Fetch stations for current viewport using get_stations_for_viewport
    - Call render_globe to display pydeck visualization
    - Handle zoom, pan, and rotation interactions
    - Process marker click events using handle_marker_click
    - Update session state on location selection
    - Add "Return to Search" button to switch back to text input
    - Display loading indicator during station data fetch
    - _Requirements: 13.1, 13.2, 13.5, 13.6, 13.9, 13.10, 13.13_

  - [x] 10.4 Implement current conditions section
    - Implement render_current_conditions function to display overall AQI
    - Display AQI value with color-coded background using get_aqi_category
    - Display AQI category label
    - Display timestamp of measurements
    - Display location name
    - Create grid of individual pollutant AQI values with mini color indicators
    - Display loading spinner during data fetch
    - Indicate missing pollutants clearly
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 8.2, Usability.2_

  - [ ]* 10.5 Write property test for missing pollutant indication
    - **Property 12: Missing Pollutant Indication**
    - **Validates: Requirements 8.2**

  - [x] 10.6 Implement activity input section
    - Implement render_activity_input function with dropdown selectors
    - Add Activity_Profile dropdown with options from config.ACTIVITY_OPTIONS
    - Add Health_Sensitivity dropdown with options from config.HEALTH_SENSITIVITY_OPTIONS
    - Trigger recommendation refresh on change
    - Update session state with selections
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 10.7 Write property test for activity profile display accuracy
    - **Property 31: Activity Profile Display Accuracy**
    - **Validates: Requirements 4.5**

  - [x] 10.8 Implement recommendation section
    - Implement render_recommendation function to display AI recommendations
    - Display safety assessment badge with color coding
    - Display main recommendation text
    - Create expandable precautions list
    - Display predicted time windows with time ranges and expected AQI
    - Display loading spinner during AI analysis
    - Display fallback message if Bedrock unavailable
    - _Requirements: 5.2, 5.3, 6.2, 6.5, Reliability.3_

  - [ ]* 10.9 Write property test for graceful Bedrock degradation
    - **Property 28: Graceful Bedrock Degradation**
    - **Validates: Requirements Reliability.3**

  - [x] 10.10 Implement historical context section
    - Implement render_historical_context function with tabbed interface
    - Create 24-hour trend line chart using Plotly/Altair showing AQI over time
    - Create 7-day pattern chart showing daily min/max/avg AQI
    - Add color-coded background zones for AQI categories
    - Add hover tooltips with exact values
    - Display message if insufficient historical data
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 8.3_

  - [x] 10.11 Implement data orchestration function
    - Implement fetch_and_update_data function to coordinate all data operations
    - Call data_fetcher.get_location to resolve location
    - Call data_fetcher.get_current_measurements to fetch measurements
    - Call aqi_calculator.calculate_overall_aqi to compute AQI
    - Call data_fetcher.get_historical_measurements for trend data
    - Call bedrock_client.get_recommendation to generate AI analysis
    - Update all session state variables
    - Handle errors at each step with appropriate error messages
    - _Requirements: Performance.2, Performance.3, Reliability.4_

  - [ ]* 10.12 Write property test for error logging
    - **Property 27: Error Logging**
    - **Validates: Requirements Reliability.1**

  - [x] 10.13 Wire all UI sections together in main app
    - Call render_location_input or render_globe_view based on view_mode
    - Call render_current_conditions if location selected
    - Call render_activity_input if location selected
    - Call render_recommendation if AQI data available
    - Call render_historical_context if historical data available
    - Ensure logical flow from location selection to recommendations
    - _Requirements: Usability.5_

  - [ ]* 10.14 Write unit tests for UI components
    - Test AQI color assignment for each category
    - Test loading state display during data fetch
    - Test error message display for invalid location
    - Test activity selector contains all options
    - Test time window display ordering

- [x] 11. Checkpoint - Ensure UI tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Integration testing and final wiring
  - [ ]* 12.1 Write integration test for end-to-end flow
    - Test: User enters location → Data fetched → AQI calculated → Recommendation generated → UI updated
    - Test: User changes activity → Recommendation regenerated with new context
    - Test: API failure → Error displayed → User retries → Success
    - Test: Cached data used → No API call made → Fresh data after cache expiry

  - [ ]* 12.2 Write integration test for globe interaction flow
    - Test: User opens globe view → Stations load → User zooms in → Markers decluster → User clicks marker → Location selected → Data displayed
    - Test: User pans globe → New viewport stations load → Cached stations reused when panning back
    - Test: User clicks marker with no recent data → Tooltip shows "No recent data" → Click still selects location

  - [ ]* 12.3 Write integration test for error scenarios
    - Test: OpenAQ API returns 500 error → Retry → Success
    - Test: Bedrock unavailable → AQI shown without recommendations
    - Test: Invalid location → Error with suggestions → User corrects → Success
    - Test: Partial pollutant data → AQI calculated with available data → Missing pollutants indicated

  - [ ]* 12.4 Write property test for configuration validation
    - **Property 25: Configuration Validation Error**
    - **Validates: Requirements 12.5**

  - [x] 12.5 Create README.md with setup instructions
    - Document installation steps (pip install -r requirements.txt)
    - Document environment variable setup (.env file)
    - Document how to run the application (streamlit run src/app.py)
    - Document AWS credentials configuration for Bedrock
    - Document OpenAQ API key setup

  - [x] 12.6 Verify all components are properly integrated
    - Verify config.py is imported by all modules
    - Verify all error handling paths work correctly
    - Verify caching works across all data fetcher functions
    - Verify session state persists across UI interactions
    - Verify globe view and text input view switch correctly

- [x] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at phase boundaries
- Property tests validate universal correctness properties (35 total)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- All code should follow Python best practices (type hints, docstrings, PEP 8)
- Use pytest for all testing with Hypothesis for property-based tests
- Mock external APIs (OpenAQ, Bedrock) in tests using responses and moto libraries
- Target test coverage: >90% line coverage, >85% branch coverage
