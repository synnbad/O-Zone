# Implementation Plan: Amplify Backend Deployment

## Overview

This implementation plan consolidates the O-Zone FastAPI backend deployment into the existing AWS Amplify build system. The approach extends amplify.yml to include a backend build phase that installs Python dependencies, packages the FastAPI application, and deploys it alongside the frontend. This eliminates the manual Lambda deployment workflow and provides a unified deployment process triggered by Git commits.

## Tasks

- [x] 1. Update amplify.yml with backend build configuration
  - Add backend section with preBuild and build phases
  - Configure Python 3.11 dependency installation with pip
  - Set up source code copying to backend_package directory
  - Define artifacts configuration for backend deployment
  - Ensure backend phase executes before frontend phase
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 7.2, 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 2. Configure environment variables in Amplify Console
  - Document the required environment variables (AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BEDROCK_MODEL_ID, OPENAQ_API_KEY)
  - Create a configuration guide for setting variables in Amplify Console UI
  - Add instructions to verify variables are accessible in backend runtime
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Verify FastAPI application Lambda compatibility
  - [x] 3.1 Confirm Mangum handler is properly configured in src/api/main.py
    - Verify handler = Mangum(app) is exported
    - Check that all routes use /api prefix
    - Ensure CORS middleware is configured
    - _Requirements: 2.3, 2.5, 4.3, 5.1, 5.2, 5.3, 5.4_
  
  - [ ]* 3.2 Write property test for Mangum handler invocation
    - **Property 1: Mangum Handler Invocation**
    - **Validates: Requirements 2.5**
    - Test that any valid API Gateway event (GET, POST, PUT, DELETE) to /api/* endpoints returns valid response with status code and headers
  
  - [ ]* 3.3 Write property test for API prefix routing
    - **Property 3: API Prefix Routing**
    - **Validates: Requirements 4.3**
    - Test that requests with /api/ prefix route to handlers while requests without prefix are not processed

- [x] 4. Implement environment variable handling with fallbacks
  - [x] 4.1 Update src/config.py to handle missing environment variables
    - Add logging for missing environment variables
    - Implement fallback to default values where applicable
    - Raise errors for required variables without defaults
    - _Requirements: 3.6, 9.3_
  
  - [ ]* 4.2 Write property test for environment variable fallback
    - **Property 2: Environment Variable Fallback**
    - **Validates: Requirements 3.6, 9.3**
    - Test that missing environment variables trigger warning logs and use documented defaults
  
  - [ ]* 4.3 Write unit tests for environment variable loading
    - Test application starts with all variables set
    - Test warning logged when optional variable missing
    - Test error raised when required variable missing
    - _Requirements: 3.6, 9.3_

- [x] 5. Verify and enhance CORS configuration
  - [x] 5.1 Review CORS middleware settings in src/api/main.py
    - Confirm allow_origins includes Amplify domain
    - Verify allow_methods includes all HTTP methods
    - Check allow_headers and allow_credentials settings
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  
  - [ ]* 5.2 Write property test for CORS headers in responses
    - **Property 4: CORS Headers in Responses**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
    - Test that all responses include required CORS headers
  
  - [ ]* 5.3 Write property test for CORS preflight handling
    - **Property 5: CORS Preflight Handling**
    - **Validates: Requirements 5.5**
    - Test that OPTIONS requests return 200 with CORS headers without invoking endpoint handler
  
  - [ ]* 5.4 Write unit tests for CORS configuration
    - Test CORS headers present in GET requests
    - Test CORS headers present in POST requests
    - Test OPTIONS preflight returns 200
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6. Checkpoint - Verify local testing
  - Test FastAPI application locally with uvicorn
  - Simulate API Gateway events to test Mangum handler
  - Ensure all tests pass, ask the user if questions arise

- [x] 7. Enhance health check endpoint
  - [x] 7.1 Review health check implementation in src/api/routers/health.py
    - Verify endpoint returns status 200
    - Confirm JSON response includes service name and version
    - Check response time is under 5 seconds
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [ ]* 7.2 Write unit tests for health check endpoint
    - Test /api/health returns 200 status
    - Test response contains correct JSON structure
    - Test response includes version information
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 8. Implement error handling and logging
  - [x] 8.1 Add error handling for external API calls
    - Implement timeout handling for OpenAQ API requests
    - Add error handling for AWS Bedrock API calls
    - Return appropriate HTTP status codes (504 for timeout, 502 for external errors)
    - _Requirements: 9.1, 9.2, 9.4, 10.5_
  
  - [x] 8.2 Configure logging throughout the application
    - Set up logging format with timestamp, level, and message
    - Add request logging (method, path, status, duration)
    - Log environment variable loading with warnings for missing vars
    - Log external API calls with URL, status, and duration
    - _Requirements: 9.3, 9.5_
  
  - [ ]* 8.3 Write unit tests for error handling
    - Test 404 returned for non-existent endpoint
    - Test 400 returned for invalid request body
    - Test 504 returned on timeout
    - Test error response format is correct
    - _Requirements: 10.5_

- [-] 9. Deploy to Amplify and verify integration
  - [x] 9.1 Commit amplify.yml changes and push to repository
    - Commit updated amplify.yml with backend configuration
    - Push to feature branch to trigger Amplify preview build
    - Monitor build logs for both frontend and backend phases
    - _Requirements: 7.1, 7.2, 7.3, 7.5_
  
  - [ ] 9.2 Verify backend deployment in Amplify Console
    - Check that backend build phase completes successfully
    - Verify deployment artifact includes all dependencies and source code
    - Confirm API endpoint URL is generated
    - Test health check endpoint returns 200
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 6.5_
  
  - [ ] 9.3 Test API endpoints from frontend
    - Verify /api/health is accessible via HTTPS
    - Test /api/locations endpoint with sample request
    - Test /api/chat endpoint with sample message
    - Check CORS headers in browser console
    - Verify response times meet performance requirements
    - _Requirements: 4.2, 4.3, 4.4, 5.1, 10.2, 10.3_
  
  - [ ] 9.4 Verify error scenarios
    - Test backend behavior with missing environment variables
    - Verify build fails gracefully if dependency installation fails
    - Check that build logs capture errors appropriately
    - _Requirements: 1.5, 9.1, 9.2, 9.4_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify deployment to preview environment is successful
  - Ensure all tests pass, ask the user if questions arise

- [x] 11. Create deployment documentation
  - [x] 11.1 Document environment variable configuration steps
    - List all required environment variables with descriptions
    - Provide step-by-step guide for setting variables in Amplify Console
    - Include screenshots or CLI commands for reference
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 11.2 Document deployment verification steps
    - Provide checklist for verifying successful deployment
    - Include health check endpoint testing instructions
    - Document how to access build logs and troubleshoot issues
    - _Requirements: 6.1, 6.2, 6.3, 9.5_
  
  - [x] 11.3 Update existing deployment guide
    - Remove manual Lambda deployment instructions
    - Add unified Amplify deployment workflow
    - Include rollback procedures if needed
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 12. Final checkpoint and production deployment
  - Merge feature branch to main branch
  - Monitor production deployment in Amplify Console
  - Verify production API endpoint is accessible
  - Run smoke tests against production environment
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across all inputs
- Unit tests validate specific examples and edge cases
- The design document uses Python, so all implementation will be in Python
- Amplify build system handles deployment automatically after build completes
