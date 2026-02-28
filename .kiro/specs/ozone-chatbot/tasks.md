# Implementation Plan: O-Zone Chatbot

## Overview

This implementation plan breaks down the O-Zone Chatbot into discrete coding tasks, prioritized for rapid MVP delivery. The chatbot provides a conversational interface for air quality recommendations, integrating with existing O-Zone MVP backend services.

**Implementation Strategy:**
1. **Priority Tasks (3-9)**: Core functionality needed for a working chatbot - backend integration, basic response generation, conversation flow, and chat interface
2. **Advanced Features (10-13)**: User profiling, adaptive communication with Claude Opus 4.6, and enhanced response formatting
3. **Testing and Polish (14-15)**: Comprehensive integration testing and documentation

This approach delivers a functional chatbot quickly, then adds sophistication incrementally.

## Completed Tasks

- [x] 1. Set up project structure and configuration
  - Created chatbot module directory structure
  - Defined ChatbotConfig class with session TTL, activity options, health sensitivity options, response templates
  - Implemented configuration validation at startup
  - Set up logging configuration for chatbot components
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

- [x] 1.1 Write property test for configuration validation
  - **Property 22: Configuration Validation at Startup**
  - **Validates: Requirements 12.2, 12.3**

- [x] 1.2 Write property test for successful startup
  - **Property 23: Successful Startup**
  - **Validates: Requirements 12.6**

- [x] 2.1 Create UserProfile and SessionContext data classes
  - Defined UserProfile with age_group, education_level, technical_expertise, communication_preference, occupation_category, inferred fields
  - Defined SessionContext with session_id, location, activity_profile, health_profile, user_profile, current_aqi, recommendation, conversation_history, current_state, created_at, last_updated fields
  - _Requirements: 13.1, 16.1_

- [x] 2.2 Implement session_manager.py core functions
  - Implemented create_session() to generate unique session IDs and initialize SessionContext
  - Implemented get_session(session_id) to retrieve sessions with expiration checking
  - Implemented update_session(session_id, updates) to modify session fields
  - Implemented delete_session(session_id) to remove sessions
  - Implemented cleanup_expired_sessions() to remove sessions older than TTL
  - _Requirements: 13.1, 13.2, 13.4, 13.5_

- [-] 2.3 Write property tests for session management (IN PROGRESS)
  - **Property 24: Session State Maintenance**
  - **Property 26: Session Context Persistence**
  - **Property 27: Session Cleanup**

## Tasks

- [x] 1. Set up project structure and configuration
  - Create chatbot module directory structure (session_manager.py, user_profiler.py, conversation_manager.py, response_generator.py, bedrock_adapter.py, backend_integration.py, chatbot_config.py, chatbot_interface.py)
  - Define ChatbotConfig class with session TTL, activity options, health sensitivity options, response templates, and vocabulary levels
  - Implement configuration validation at startup
  - Set up logging configuration for chatbot components
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6_

- [x] 1.1 Write property test for configuration validation
  - **Property 22: Configuration Validation at Startup**
  - **Validates: Requirements 12.2, 12.3**

- [x] 1.2 Write property test for successful startup
  - **Property 23: Successful Startup**
  - **Validates: Requirements 12.6**

- [-] 2. Implement session management
  - [x] 2.1 Create UserProfile and SessionContext data classes
    - Define UserProfile with age_group, education_level, technical_expertise, communication_preference, occupation_category, inferred fields
    - Define SessionContext with session_id, location, activity_profile, health_profile, user_profile, current_aqi, recommendation, conversation_history, current_state, created_at, last_updated fields
    - _Requirements: 13.1, 16.1_

  - [x] 2.2 Implement session_manager.py core functions
    - Write create_session() to generate unique session IDs and initialize SessionContext
    - Write get_session(session_id) to retrieve sessions with expiration checking
    - Write update_session(session_id, updates) to modify session fields
    - Write delete_session(session_id) to remove sessions
    - Write cleanup_expired_sessions() to remove sessions older than TTL
    - _Requirements: 13.1, 13.2, 13.4, 13.5_

  - [-] 2.3 Write property tests for session management
    - **Property 24: Session State Maintenance**
    - **Validates: Requirements 13.1**
    - **Property 26: Session Context Persistence**
    - **Validates: Requirements 13.4**
    - **Property 27: Session Cleanup**
    - **Validates: Requirements 13.5**

  - [x] 2.4 Write unit tests for session manager
    - Test session creation generates unique IDs
    - Test session retrieval and expiration
    - Test session updates and deletion
    - Test cleanup of expired sessions

- [x] 3. Implement user profiling and adaptive communication
  - [x] 3.1 Create user_profiler.py with profile collection functions
    - Write collect_user_profile_interactive(session_id) to prompt for demographic information
    - Write infer_user_profile(conversation_history) to analyze vocabulary and sentence complexity
    - Write update_profile_from_feedback(profile, feedback) to adjust based on user requests
    - Write get_communication_style(profile) to return vocabulary_level, sentence_complexity, explanation_depth, include_technical_details
    - _Requirements: 16.1, 16.2, 16.10_

  - [ ] 3.2 Write property tests for user profiling
    - **Property 35: User Profile Inference**
    - **Validates: Requirements 16.2**
    - **Property 41: Dynamic Style Adjustment**
    - **Validates: Requirements 16.10**

  - [ ] 3.3 Write unit tests for user profiler
    - Test profile inference from simple vs technical vocabulary
    - Test profile update from feedback
    - Test communication style parameters for different profiles

- [x] 4. Implement backend integration layer
  - [x] 4.1 Create backend_integration.py with unified backend interface
    - Write resolve_location(location_query) to call data_fetcher.get_location with error translation
    - Write fetch_current_aqi(location) to call data_fetcher and aqi_calculator
    - Write fetch_historical_data(location, hours) to retrieve historical measurements
    - Write generate_recommendation(overall_aqi, activity, health_sensitivity, historical_data) to call bedrock_client
    - Write generate_fallback_recommendation(overall_aqi, activity, health_sensitivity) for rule-based recommendations
    - _Requirements: 1.1, 1.2, 4.1, 4.2, 5.1, 6.2, 7.1, 7.3, 7.4, 9.2, 9.4_

  - [ ] 4.2 Write property tests for backend integration
    - **Property 1: Location Resolution**
    - **Validates: Requirements 1.1, 1.2**
    - **Property 6: Recommendation Request Completeness**
    - **Validates: Requirements 2.4, 3.4, 4.1, 4.2**
    - **Property 16: Missing Data Error Handling**
    - **Validates: Requirements 7.1, 7.2**
    - **Property 17: Partial Data Handling**
    - **Validates: Requirements 7.3**
    - **Property 18: Critical Data Requirement**
    - **Validates: Requirements 7.4**
    - **Property 20: Bedrock Failure Detection**
    - **Validates: Requirements 9.1**
    - **Property 21: Bedrock Fallback Behavior**
    - **Validates: Requirements 9.2, 9.3, 9.4, 9.5**

  - [ ] 4.3 Write unit tests for backend integration
    - Test location resolution success and failure
    - Test AQI fetch with no data error
    - Test recommendation generation with Bedrock failure
    - Test fallback recommendation generation

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Bedrock adapter for adaptive communication
  - [x] 6.1 Create bedrock_adapter.py with Claude Opus 4.6 integration
    - Write generate_adaptive_response(prompt, user_profile, context) to call Claude with profile context
    - Write construct_adaptive_prompt(base_prompt, user_profile, context) to add communication style instructions
    - Write call_claude_opus(prompt, parameters) with authentication, retry logic, and error handling
    - _Requirements: 4.1, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8_

  - [ ] 6.2 Write unit tests for Bedrock adapter
    - Test prompt construction with different user profiles
    - Test Claude API call with retry logic
    - Test error handling for Bedrock failures

- [x] 7. Implement response generation and formatting
  - [x] 7.1 Create response_generator.py with adaptive formatting functions
    - Write generate_response(message_type, data, user_profile) as main entry point
    - Write format_aqi_explanation(aqi, user_profile) to adapt technical detail based on profile
    - Write format_recommendation(recommendation, user_profile) to adjust explanation depth
    - Write format_time_windows(time_windows, user_profile) to format predictions conversationally
    - Write format_error_message(error_type, details, suggestions) for user-friendly errors
    - Write adapt_vocabulary(text, vocabulary_level) to simplify or enhance vocabulary
    - Write adapt_sentence_complexity(text, complexity_level) to adjust sentence structure
    - _Requirements: 4.3, 4.5, 5.3, 5.4, 5.5, 6.3, 6.5, 8.1, 8.2, 8.3, 8.4, 15.1, 15.2, 15.3, 15.4, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.11_

  - [ ] 7.2 Write property tests for response generation
    - **Property 2: Location Confirmation**
    - **Validates: Requirements 1.3**
    - **Property 8: Recommendation Presentation**
    - **Validates: Requirements 4.3**
    - **Property 9: Hazardous Condition Response**
    - **Validates: Requirements 4.4, 10.1, 10.2, 10.4**
    - **Property 11: Time Window Presentation**
    - **Validates: Requirements 5.3, 5.5**
    - **Property 12: Empty Time Window Explanation**
    - **Validates: Requirements 5.4**
    - **Property 15: Trend Data Formatting**
    - **Validates: Requirements 6.3, 6.5**
    - **Property 19: Stale Data Handling**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**
    - **Property 32: User-Friendly Error Messages**
    - **Validates: Requirements 15.1, 15.2**
    - **Property 33: Error Recovery Guidance**
    - **Validates: Requirements 15.3, 15.4**
    - **Property 36: Vocabulary Adaptation**
    - **Validates: Requirements 16.3, 16.4, 16.12**
    - **Property 37: Communication Detail Adaptation**
    - **Validates: Requirements 16.5, 16.6**
    - **Property 38: Recommendation Explanation Adaptation**
    - **Validates: Requirements 16.7**
    - **Property 39: AQI Presentation Adaptation**
    - **Validates: Requirements 16.8**
    - **Property 42: Vocabulary Complexity Matching**
    - **Validates: Requirements 16.11**

  - [ ] 7.3 Write unit tests for response generator
    - Test AQI formatting for basic vs technical profiles
    - Test recommendation formatting for concise vs detailed preferences
    - Test error message formatting
    - Test vocabulary adaptation for different age groups

- [x] 8. Implement conversation flow management
  - [x] 8.1 Create ConversationState enum and conversation_manager.py
    - Define ConversationState enum with GREETING, LOCATION_COLLECTION, ACTIVITY_SELECTION, HEALTH_PROFILE_SELECTION, USER_PROFILE_COLLECTION, RECOMMENDATION_GENERATION, RECOMMENDATION_PRESENTATION, FOLLOW_UP, ERROR_RECOVERY, GOODBYE states
    - Write process_user_input(session_id, user_input) as main entry point
    - Write determine_next_state(session) to analyze context completeness
    - _Requirements: 14.1, 14.2, 14.3_

  - [x] 8.2 Implement conversation state handlers
    - Write handle_greeting(session) to generate welcome message
    - Write handle_location_collection(session, user_input) to validate and store location
    - Write handle_activity_selection(session, user_input) to present options and validate selection
    - Write handle_health_profile_selection(session, user_input) to present options and validate selection
    - Write handle_recommendation_generation(session) to fetch AQI and generate recommendations
    - Write handle_recommendation_presentation(session) to format and display recommendations
    - Write handle_follow_up(session, user_input) to determine intent and route to appropriate handler
    - Write handle_error_recovery(session, error) to translate errors and provide guidance
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.3, 4.4, 5.1, 6.1, 6.2, 10.1, 10.2, 10.3, 10.4, 11.1, 11.2, 11.3, 11.4, 11.5, 14.1, 14.2, 14.3, 14.4, 14.5, 14.6_

  - [ ] 8.3 Write property tests for conversation flow
    - **Property 3: Mid-Session Location Update**
    - **Validates: Requirements 1.5, 11.2, 11.3, 11.4**
    - **Property 4: Invalid Location Change Preservation**
    - **Validates: Requirements 11.5**
    - **Property 5: Session Context Updates**
    - **Validates: Requirements 2.2, 3.2, 13.2, 16.1**
    - **Property 7: Recommendation Trigger Condition**
    - **Validates: Requirements 4.1**
    - **Property 10: Time Window Request Handling**
    - **Validates: Requirements 5.1**
    - **Property 13: Trend Options Presentation**
    - **Validates: Requirements 6.1**
    - **Property 14: Trend Data Retrieval**
    - **Validates: Requirements 6.2**
    - **Property 25: Session Context Usage**
    - **Validates: Requirements 13.3**
    - **Property 28: Initial Greeting**
    - **Validates: Requirements 14.1**
    - **Property 29: Missing Information Prompt**
    - **Validates: Requirements 14.3**
    - **Property 30: Response Completeness**
    - **Validates: Requirements 14.4, 14.6**
    - **Property 31: Context-Aware Responses**
    - **Validates: Requirements 14.5**
    - **Property 34: Error Logging**
    - **Validates: Requirements 15.5**
    - **Property 40: Communication Style Consistency**
    - **Validates: Requirements 16.9**

  - [ ] 8.4 Write unit tests for conversation manager
    - Test greeting state returns welcome message
    - Test location collection with valid and invalid input
    - Test activity selection with valid and invalid choices
    - Test recommendation generation with complete context
    - Test mid-session location change
    - Test follow-up question handling

- [x] 9. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement chat interface
  - [x] 10.1 Create chatbot_interface.py with CLI or Streamlit interface
    - Implement user input handling and sanitization
    - Implement conversation history display
    - Implement special command handling (help, restart, change location)
    - Wire interface to conversation_manager.process_user_input()
    - _Requirements: 14.1, 14.2, 14.6_

  - [ ] 10.2 Write unit tests for chat interface
    - Test input sanitization
    - Test special command handling
    - Test conversation history display

## Priority Tasks

- [ ] 3. Implement backend integration layer (CRITICAL - needed for core functionality)
  - [x] 3.1 Create backend_integration.py with unified backend interface
    - Write resolve_location(location_query) to call data_fetcher.get_location with error translation
    - Write fetch_current_aqi(location) to call data_fetcher and aqi_calculator
    - Write fetch_historical_data(location, hours) to retrieve historical measurements
    - Write generate_recommendation(overall_aqi, activity, health_sensitivity, historical_data) to call bedrock_client
    - Write generate_fallback_recommendation(overall_aqi, activity, health_sensitivity) for rule-based recommendations
    - _Requirements: 1.1, 1.2, 4.1, 4.2, 5.1, 6.2, 7.1, 7.3, 7.4, 9.2, 9.4_

  - [ ]* 3.2 Write property tests for backend integration
    - **Property 1: Location Resolution**
    - **Validates: Requirements 1.1, 1.2**
    - **Property 6: Recommendation Request Completeness**
    - **Validates: Requirements 2.4, 3.4, 4.1, 4.2**
    - **Property 16: Missing Data Error Handling**
    - **Validates: Requirements 7.1, 7.2**
    - **Property 17: Partial Data Handling**
    - **Validates: Requirements 7.3**
    - **Property 18: Critical Data Requirement**
    - **Validates: Requirements 7.4**
    - **Property 20: Bedrock Failure Detection**
    - **Validates: Requirements 9.1**
    - **Property 21: Bedrock Fallback Behavior**
    - **Validates: Requirements 9.2, 9.3, 9.4, 9.5**

  - [ ]* 3.3 Write unit tests for backend integration
    - Test location resolution success and failure
    - Test AQI fetch with no data error
    - Test recommendation generation with Bedrock failure
    - Test fallback recommendation generation

- [ ] 4. Implement basic response generation (CRITICAL - needed for user interaction)
  - [x] 4.1 Create response_generator.py with core formatting functions
    - Write generate_response(message_type, data, user_profile) as main entry point
    - Write format_aqi_explanation(aqi, user_profile) for basic AQI presentation
    - Write format_recommendation(recommendation, user_profile) for recommendation display
    - Write format_error_message(error_type, details, suggestions) for user-friendly errors
    - _Requirements: 4.3, 15.1, 15.2, 15.3, 15.4_

  - [x]* 4.2 Write unit tests for basic response generation
    - Test AQI formatting
    - Test recommendation formatting
    - Test error message formatting

- [x] 5. Implement conversation flow management (CRITICAL - core chatbot logic)
  - [x] 5.1 Create ConversationState enum and conversation_manager.py
    - Define ConversationState enum with GREETING, LOCATION_COLLECTION, ACTIVITY_SELECTION, HEALTH_PROFILE_SELECTION, RECOMMENDATION_GENERATION, RECOMMENDATION_PRESENTATION, FOLLOW_UP, ERROR_RECOVERY, GOODBYE states
    - Write process_user_input(session_id, user_input) as main entry point
    - Write determine_next_state(session) to analyze context completeness
    - _Requirements: 14.1, 14.2, 14.3_

  - [x] 5.2 Implement core conversation state handlers
    - Write handle_greeting(session) to generate welcome message
    - Write handle_location_collection(session, user_input) to validate and store location
    - Write handle_activity_selection(session, user_input) to present options and validate selection
    - Write handle_health_profile_selection(session, user_input) to present options and validate selection
    - Write handle_recommendation_generation(session) to fetch AQI and generate recommendations
    - Write handle_recommendation_presentation(session) to format and display recommendations
    - Write handle_error_recovery(session, error) to translate errors and provide guidance
    - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 4.3, 4.4, 14.1, 14.2, 14.3, 14.4, 14.6_

  - [ ]* 5.3 Write property tests for core conversation flow
    - **Property 5: Session Context Updates**
    - **Validates: Requirements 2.2, 3.2, 13.2, 16.1**
    - **Property 7: Recommendation Trigger Condition**
    - **Validates: Requirements 4.1**
    - **Property 28: Initial Greeting**
    - **Validates: Requirements 14.1**
    - **Property 29: Missing Information Prompt**
    - **Validates: Requirements 14.3**
    - **Property 30: Response Completeness**
    - **Validates: Requirements 14.4, 14.6**

  - [ ]* 5.4 Write unit tests for conversation manager
    - Test greeting state returns welcome message
    - Test location collection with valid and invalid input
    - Test activity selection with valid and invalid choices
    - Test recommendation generation with complete context

- [ ] 6. Checkpoint - Core functionality complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement chat interface (HIGH PRIORITY - user-facing component)
  - [x] 7.1 Create chatbot_interface.py with CLI or Streamlit interface
    - Implement user input handling and sanitization
    - Implement conversation history display
    - Implement special command handling (help, restart)
    - Wire interface to conversation_manager.process_user_input()
    - _Requirements: 14.1, 14.2, 14.6_

  - [ ]* 7.2 Write unit tests for chat interface
    - Test input sanitization
    - Test special command handling
    - Test conversation history display

- [ ] 8. Implement follow-up conversation features (MEDIUM PRIORITY)
  - [x] 8.1 Add follow-up handler to conversation_manager.py
    - Write handle_follow_up(session, user_input) to determine intent and route to appropriate handler
    - Add support for location changes mid-session
    - Add support for time window requests
    - Add support for trend requests
    - _Requirements: 1.5, 5.1, 6.1, 6.2, 11.1, 11.2, 11.3, 11.4, 11.5, 14.5_

  - [x] 8.2 Add time window and trend formatting to response_generator.py
    - Write format_time_windows(time_windows, user_profile) to format predictions conversationally
    - Write format_trend_data(historical_data, user_profile) for trend presentation
    - _Requirements: 5.3, 5.4, 5.5, 6.3, 6.5_

  - [ ]* 8.3 Write property tests for follow-up features
    - **Property 3: Mid-Session Location Update**
    - **Validates: Requirements 1.5, 11.2, 11.3, 11.4**
    - **Property 4: Invalid Location Change Preservation**
    - **Validates: Requirements 11.5**
    - **Property 10: Time Window Request Handling**
    - **Validates: Requirements 5.1**
    - **Property 11: Time Window Presentation**
    - **Validates: Requirements 5.3, 5.5**
    - **Property 13: Trend Options Presentation**
    - **Validates: Requirements 6.1**
    - **Property 14: Trend Data Retrieval**
    - **Validates: Requirements 6.2**

  - [ ]* 8.4 Write unit tests for follow-up features
    - Test mid-session location change
    - Test time window request handling
    - Test trend request handling

- [x] 9. Checkpoint - MVP functionality complete
  - Ensure all tests pass, ask the user if questions arise.

## Advanced Features (Lower Priority)

- [ ] 10. Implement user profiling and adaptive communication
  - [x] 10.1 Create user_profiler.py with profile collection functions
    - Write collect_user_profile_interactive(session_id) to prompt for demographic information
    - Write infer_user_profile(conversation_history) to analyze vocabulary and sentence complexity
    - Write update_profile_from_feedback(profile, feedback) to adjust based on user requests
    - Write get_communication_style(profile) to return vocabulary_level, sentence_complexity, explanation_depth, include_technical_details
    - _Requirements: 16.1, 16.2, 16.10_

  - [ ]* 10.2 Write property tests for user profiling
    - **Property 35: User Profile Inference**
    - **Validates: Requirements 16.2**
    - **Property 41: Dynamic Style Adjustment**
    - **Validates: Requirements 16.10**

  - [ ]* 10.3 Write unit tests for user profiler
    - Test profile inference from simple vs technical vocabulary
    - Test profile update from feedback
    - Test communication style parameters for different profiles

- [x] 11. Implement Bedrock adapter for adaptive communication
  - [x] 11.1 Create bedrock_adapter.py with Claude Opus 4.6 integration
    - Write generate_adaptive_response(prompt, user_profile, context) to call Claude with profile context
    - Write construct_adaptive_prompt(base_prompt, user_profile, context) to add communication style instructions
    - Write call_claude_opus(prompt, parameters) with authentication, retry logic, and error handling
    - _Requirements: 4.1, 16.3, 16.4, 16.5, 16.6, 16.7, 16.8_

  - [ ]* 11.2 Write unit tests for Bedrock adapter
    - Test prompt construction with different user profiles
    - Test Claude API call with retry logic
    - Test error handling for Bedrock failures

- [x] 12. Enhance response generation with adaptive features
  - [x] 12.1 Add adaptive formatting to response_generator.py
    - Write adapt_vocabulary(text, vocabulary_level) to simplify or enhance vocabulary
    - Write adapt_sentence_complexity(text, complexity_level) to adjust sentence structure
    - Enhance format_aqi_explanation() to adapt technical detail based on profile
    - Enhance format_recommendation() to adjust explanation depth
    - _Requirements: 16.3, 16.4, 16.5, 16.6, 16.7, 16.8, 16.11_

  - [ ]* 12.2 Write property tests for adaptive response generation
    - **Property 2: Location Confirmation**
    - **Validates: Requirements 1.3**
    - **Property 8: Recommendation Presentation**
    - **Validates: Requirements 4.3**
    - **Property 9: Hazardous Condition Response**
    - **Validates: Requirements 4.4, 10.1, 10.2, 10.4**
    - **Property 36: Vocabulary Adaptation**
    - **Validates: Requirements 16.3, 16.4, 16.12**
    - **Property 37: Communication Detail Adaptation**
    - **Validates: Requirements 16.5, 16.6**
    - **Property 38: Recommendation Explanation Adaptation**
    - **Validates: Requirements 16.7**
    - **Property 39: AQI Presentation Adaptation**
    - **Validates: Requirements 16.8**
    - **Property 42: Vocabulary Complexity Matching**
    - **Validates: Requirements 16.11**

  - [ ]* 12.3 Write unit tests for adaptive response generation
    - Test AQI formatting for basic vs technical profiles
    - Test recommendation formatting for concise vs detailed preferences
    - Test vocabulary adaptation for different age groups

- [x] 13. Add advanced conversation flow features
  - [ ]* 13.1 Write property tests for advanced conversation flow
    - **Property 25: Session Context Usage**
    - **Validates: Requirements 13.3**
    - **Property 31: Context-Aware Responses**
    - **Validates: Requirements 14.5**
    - **Property 34: Error Logging**
    - **Validates: Requirements 15.5**
    - **Property 40: Communication Style Consistency**
    - **Validates: Requirements 16.9**

## Testing and Polish

- [x] 14. Integration and end-to-end testing
  - [x]* 14.1 Create integration test fixtures and mocks
    - Create mock data_fetcher, aqi_calculator, bedrock_client
    - Create fixtures for common response patterns (valid location, no data, stale data)
    - Create fixtures for different user profiles
    - Set up time mocking with freezegun for session expiration tests
    - _Requirements: All_

  - [x]* 14.2 Write end-to-end conversation flow tests
    - Test complete onboarding flow: Greeting → Location → Activity → Health → Recommendation
    - Test location change mid-session: Initial recommendation → Change location → New recommendation
    - Test follow-up questions: Recommendation → Time windows request → Trends request
    - Test error recovery: Invalid location → Correction → Success
    - Test adaptive communication: Basic user profile → Technical question → Simplified response

  - [x]* 14.3 Write error recovery flow tests
    - Test backend failure during onboarding → Fallback → Retry → Success
    - Test session expiration during conversation → New session → Context recovery
    - Test invalid input handling → Clarification → Valid input → Continue
    - Test Bedrock unavailable → Rule-based recommendation → Bedrock restored → AI recommendation

  - [ ]* 14.4 Write backend integration flow tests
    - Test location resolution → AQI fetch → Recommendation generation → Response formatting
    - Test historical data fetch → Trend analysis → Presentation
    - Test time window prediction → Formatting → User selection
    - Test partial data handling → Limited recommendation → Warning display

- [x] 15. Final checkpoint and documentation
  - Ensure all tests pass (unit, property-based, integration)
  - Verify test coverage meets goals (>85% line coverage, >80% branch coverage)
  - Add docstrings to all public functions and classes
  - Create README with setup instructions and usage examples
  - Document configuration parameters and environment variables
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end conversation flows
- The chatbot integrates with existing O-Zone MVP backend services (data_fetcher.py, aqi_calculator.py, bedrock_client.py)
- Implementation uses Python with pytest and Hypothesis for testing
- Bedrock adapter (advanced feature) uses Amazon Bedrock Claude Opus 4.6 for adaptive communication

## Task Prioritization Rationale

**Priority Tasks (3-9)** deliver a functional chatbot that can:
- Resolve locations and fetch air quality data
- Guide users through activity and health profile selection
- Generate and present recommendations
- Handle errors gracefully
- Provide a working CLI/Streamlit interface

**Advanced Features (10-13)** add sophistication:
- User profiling for demographic-aware communication
- AI-powered adaptive responses via Claude Opus 4.6
- Vocabulary and complexity adaptation
- Enhanced formatting for different user types

**Testing and Polish (14-15)** ensure production readiness:
- Comprehensive integration tests
- End-to-end conversation flow validation
- Error recovery testing
- Documentation and deployment guides

