# Integration Test Fixtures Guide

This guide explains how to use the comprehensive integration test fixtures defined in `tests/conftest.py` for testing the O-Zone Chatbot.

## Overview

The fixtures provide:
- **Mock backend services** (data_fetcher, aqi_calculator, bedrock_client)
- **Common response patterns** (valid location, no data, stale data, hazardous AQI)
- **User profile fixtures** (basic, child, technical, sensitive health, concise)
- **Session fixtures** (sample session, complete session context)
- **Time mocking** (for session expiration tests)
- **Automatic cleanup** (session store cleanup between tests)

## Backend Service Mocks

### `mock_data_fetcher`
Mocks the data_fetcher module with default behaviors:
- `get_location`: Returns San Francisco location
- `get_current_measurements`: Returns PM2.5 and PM10 measurements
- `get_historical_measurements`: Returns empty dict

**Usage:**
```python
def test_location_resolution(mock_data_fetcher):
    # Configure mock
    mock_data_fetcher['get_location'].return_value = Location(...)
    
    # Test code
    location = resolve_location("San Francisco")
    assert location.name == "San Francisco"
```

### `mock_aqi_calculator`
Mocks the aqi_calculator module:
- `calculate_overall_aqi`: Returns moderate AQI (100)

**Usage:**
```python
def test_aqi_calculation(mock_aqi_calculator):
    # Configure mock
    mock_aqi_calculator.return_value = OverallAQI(aqi=150, ...)
    
    # Test code
    aqi = fetch_current_aqi(location)
    assert aqi.aqi == 150
```

### `mock_bedrock_client`
Mocks the bedrock_client module:
- `get_recommendation`: Returns moderate risk recommendation with time windows

**Usage:**
```python
def test_recommendation(mock_bedrock_client):
    # Mock is already configured with default recommendation
    recommendation = generate_recommendation(aqi, "Walking", "None")
    assert recommendation.safety_assessment == "Moderate Risk"
```

## Common Response Pattern Fixtures

### `valid_location_response`
Complete valid scenario with location, measurements, and AQI.

**Usage:**
```python
def test_valid_scenario(mock_data_fetcher, mock_aqi_calculator, valid_location_response):
    mock_data_fetcher['get_location'].return_value = valid_location_response['location']
    mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
    mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
    
    # Test code
    location = resolve_location("San Francisco")
    aqi = fetch_current_aqi(location)
```

### `no_data_response`
Scenario where location is found but no measurements available.

**Usage:**
```python
def test_no_data(mock_data_fetcher, no_data_response):
    mock_data_fetcher['get_location'].return_value = no_data_response['location']
    mock_data_fetcher['get_current_measurements'].return_value = []
    
    with pytest.raises(NoDataAvailableError):
        fetch_current_aqi(location)
```

### `stale_data_response`
Scenario with measurements older than 3 hours.

**Usage:**
```python
def test_stale_data(mock_data_fetcher, mock_aqi_calculator, stale_data_response):
    mock_data_fetcher['get_location'].return_value = stale_data_response['location']
    mock_data_fetcher['get_current_measurements'].return_value = stale_data_response['measurements']
    mock_aqi_calculator.return_value = stale_data_response['overall_aqi']
    
    aqi = fetch_current_aqi(location)
    assert (datetime.utcnow() - aqi.timestamp) > timedelta(hours=3)
```

### `hazardous_aqi_response`
Scenario with hazardous air quality (AQI > 300).

**Usage:**
```python
def test_hazardous(mock_data_fetcher, mock_aqi_calculator, hazardous_aqi_response):
    mock_data_fetcher['get_location'].return_value = hazardous_aqi_response['location']
    mock_data_fetcher['get_current_measurements'].return_value = hazardous_aqi_response['measurements']
    mock_aqi_calculator.return_value = hazardous_aqi_response['overall_aqi']
    
    aqi = fetch_current_aqi(location)
    assert aqi.category == "Hazardous"
```

## User Profile Fixtures

### `basic_user_profile`
User with basic education level and no technical expertise.

**Usage:**
```python
def test_basic_user(basic_user_profile):
    assert basic_user_profile.education_level == "basic"
    assert basic_user_profile.technical_expertise == "none"
```

### `child_user_profile`
Child age group with basic education.

**Usage:**
```python
def test_child_user(child_user_profile):
    assert child_user_profile.age_group == "child"
    assert child_user_profile.communication_preference == "detailed"
```

### `technical_user_profile`
Expert user with advanced education (environmental scientist).

**Usage:**
```python
def test_technical_user(technical_user_profile):
    assert technical_user_profile.technical_expertise == "expert"
    assert technical_user_profile.occupation_category == "environmental_scientist"
```

### `sensitive_health_profile`
User with health sensitivity considerations.

**Usage:**
```python
def test_sensitive_health(sensitive_health_profile):
    # Use for testing health-sensitive scenarios
    recommendation = generate_recommendation(aqi, "Walking", "Asthma/Respiratory")
```

### `concise_user_profile`
User preferring concise communication.

**Usage:**
```python
def test_concise_user(concise_user_profile):
    assert concise_user_profile.communication_preference == "concise"
```

## Session Fixtures

### `sample_session`
Session with basic context (location, activity, health profile, user profile).

**Usage:**
```python
def test_session(sample_session):
    assert sample_session.location.name == "San Francisco"
    assert sample_session.activity_profile == "Walking"
    assert sample_session.health_profile == "None"
```

### `complete_session_context`
Session with complete context including AQI and recommendation.

**Usage:**
```python
def test_complete_session(complete_session_context):
    assert complete_session_context.current_aqi is not None
    assert complete_session_context.recommendation is not None
    assert complete_session_context.current_state == "recommendation_presentation"
```

## Time Mocking Fixtures

### `frozen_time`
Freeze time at a specific point (requires freezegun package).

**Usage:**
```python
def test_with_frozen_time(frozen_time):
    # Time is frozen at 2024-01-15 12:00:00
    session = create_session()
    assert session.created_at == frozen_time
```

### `time_travel`
Advance time for testing session expiration (requires freezegun package).

**Usage:**
```python
def test_session_expiration(time_travel):
    session = create_session()
    session_id = session.session_id
    
    # Advance time by 31 minutes
    time_travel.advance(minutes=31)
    
    # Session should be expired
    expired_session = get_session(session_id)
    assert expired_session is None
```

**Note:** Time mocking tests will be skipped if freezegun is not installed. To enable:
```bash
pip install freezegun
```

## Automatic Cleanup

### `cleanup_sessions`
Automatically clears the session store after each test (autouse=True).

This fixture runs automatically - no need to include it in test parameters. It ensures:
- Session store is clean at the start of each test
- No session leakage between tests
- Consistent test isolation

## Complete Example

Here's a complete example showing how to use multiple fixtures together:

```python
def test_complete_conversation_flow(
    mock_data_fetcher,
    mock_aqi_calculator,
    mock_bedrock_client,
    valid_location_response,
    basic_user_profile
):
    """Test complete conversation flow with all fixtures"""
    # Configure mocks
    mock_data_fetcher['get_location'].return_value = valid_location_response['location']
    mock_data_fetcher['get_current_measurements'].return_value = valid_location_response['measurements']
    mock_aqi_calculator.return_value = valid_location_response['overall_aqi']
    
    # Create session
    session = create_session()
    session.user_profile = basic_user_profile
    session_id = session.session_id
    
    # Test conversation flow
    response1 = process_user_input(session_id, "Hello")
    assert "location" in response1.lower()
    
    response2 = process_user_input(session_id, "San Francisco")
    assert "activity" in response2.lower()
    
    response3 = process_user_input(session_id, "Walking")
    assert "health" in response3.lower()
    
    response4 = process_user_input(session_id, "None")
    # Should get recommendation
    assert len(response4) > 0
    
    # Verify session state
    final_session = get_session(session_id)
    assert final_session.location is not None
    assert final_session.activity_profile == "Walking"
    assert final_session.health_profile == "None"
```

## Best Practices

1. **Use specific fixtures**: Choose the most specific fixture for your test case (e.g., `hazardous_aqi_response` for testing hazardous conditions).

2. **Configure mocks explicitly**: Even though fixtures provide defaults, explicitly configure mocks in your test for clarity.

3. **Test isolation**: Each test should be independent. The `cleanup_sessions` fixture ensures session isolation.

4. **Mock at the right level**: Mock at the backend integration level (data_fetcher, aqi_calculator, bedrock_client) rather than lower-level HTTP calls.

5. **Use response patterns**: Leverage the response pattern fixtures (`valid_location_response`, etc.) for consistent test data.

6. **Test error scenarios**: Use fixtures like `no_data_response` to test error handling.

7. **Test different user profiles**: Use user profile fixtures to test adaptive communication.

## Running Integration Tests

Run all integration tests:
```bash
python -m pytest tests/integration/ -v
```

Run specific test file:
```bash
python -m pytest tests/integration/test_fixtures_demo.py -v
```

Run with coverage:
```bash
python -m pytest tests/integration/ --cov=src.chatbot --cov-report=html
```

## See Also

- `tests/integration/test_fixtures_demo.py` - Comprehensive examples of fixture usage
- `tests/integration/test_chatbot_interface_integration.py` - Real integration tests
- `tests/conftest.py` - Fixture definitions
