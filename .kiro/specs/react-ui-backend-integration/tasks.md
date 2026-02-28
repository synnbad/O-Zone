# Implementation Plan: React UI Backend Integration

## Overview

This plan implements a hackathon-ready integration between the React UI and Python backend, focusing on rapid deployment to AWS Amplify. The approach prioritizes the 6 core API endpoints, demo reliability with fallback data, and minimal configuration complexity suitable for a time-constrained demo environment.

## Tasks

- [x] 1. Set up FastAPI backend structure
  - Create `src/api/` directory structure with `main.py`, `routers/`, and `session.py`
  - Install FastAPI, Mangum (Lambda adapter), and dependencies in `requirements.txt`
  - Configure CORS middleware to allow all origins for demo
  - Set up Mangum handler for AWS Lambda compatibility
  - _Requirements: 1.8, 1.10_

- [x] 2. Implement location endpoints
  - [x] 2.1 Create location router with search endpoint
    - Implement `GET /api/locations/search?q={query}` using existing `data_fetcher.py`
    - Add fallback to `demo_data.py` when OpenAQ API fails
    - Return JSON with location results and metadata indicating data source
    - _Requirements: 1.1, 1.6, 1.7_
  
  - [x] 2.2 Create AQI data endpoint
    - Implement `GET /api/locations/{location_id}/aqi` using `aqi_calculator.py`
    - Fetch measurements from OpenAQ or demo data
    - Calculate overall AQI and pollutant breakdown
    - Return JSON with AQI data, pollutants array, and metadata
    - _Requirements: 1.2, 1.6, 1.7, 1.9_

- [x] 3. Implement chat endpoint with session management
  - [x] 3.1 Create session manager module
    - Implement in-memory session storage with TTL (30 minutes)
    - Add session creation, retrieval, update, and cleanup methods
    - Use UUID for session IDs
    - _Requirements: 1.7_
  
  - [x] 3.2 Create chat router
    - Implement `POST /api/chat` accepting message and optional session_id
    - Integrate existing `chatbot/` module and `bedrock_client.py`
    - Create new session if session_id not provided
    - Store conversation history in session
    - Return response with session_id for continuity
    - _Requirements: 1.3, 1.6, 1.7_

- [x] 4. Implement recommendations endpoint
  - Create recommendations router with `GET /api/recommendations` endpoint
  - Accept query params: location, activity, health sensitivity
  - Use `bedrock_client.py` for AI-powered recommendations
  - Implement rule-based fallback when Bedrock unavailable
  - Return safety assessment, precautions, time windows, and reasoning
  - _Requirements: 1.4, 1.6, 1.7_

- [x] 5. Implement map stations endpoint
  - Create map router with `GET /api/stations/map` endpoint
  - Accept optional bounds query params (north, south, east, west)
  - Use `data_fetcher.py` to fetch global station data
  - Fall back to `demo_data.py` for demo reliability
  - Return array of stations with coordinates and current AQI
  - _Requirements: 1.5, 1.6, 1.7_

- [x] 6. Implement health check endpoint
  - Create health router with `GET /api/health` endpoint
  - Return 200 OK with service status
  - Include timestamp and version info
  - _Requirements: 1.9_

- [x] 7. Checkpoint - Test backend API locally
  - Run FastAPI locally with `uvicorn src.api.main:app --reload`
  - Test all 6 endpoints with curl or Postman
  - Verify fallback data works when external APIs unavailable
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Set up React frontend API integration
  - [x] 8.1 Create API client and service layer
    - Create `src/api/client.ts` with axios instance and interceptors
    - Configure base URL from `VITE_API_URL` environment variable
    - Add request/response logging and error handling
    - Create service modules: `locationService.ts`, `chatService.ts`, `recommendationService.ts`, `mapService.ts`
    - _Requirements: 2.6, 2.7, 2.8_
  
  - [x] 8.2 Create TypeScript type definitions
    - Define interfaces matching backend API contracts in `src/types/`
    - Create types for: Location, AQIData, Pollutant, ChatMessage, Recommendation, Station
    - Export all types from `src/types/index.ts`
    - _Requirements: 2.9_

- [x] 9. Implement custom React hooks for API calls
  - [x] 9.1 Create location hooks
    - Implement `useLocationSearch` hook with debouncing
    - Implement `useAQIData` hook with auto-refresh
    - Add loading and error state management
    - _Requirements: 2.1, 2.2, 2.7, 2.8_
  
  - [x] 9.2 Create chat hook
    - Implement `useChat` hook managing session and message history
    - Store session_id in localStorage for persistence
    - Add message sending and response handling
    - _Requirements: 2.3, 2.7, 2.8_
  
  - [x] 9.3 Create recommendations and map hooks
    - Implement `useRecommendations` hook with activity/health params
    - Implement `useMapStations` hook with bounds filtering
    - Add loading and error state management
    - _Requirements: 2.4, 2.5, 2.7, 2.8_

- [x] 10. Connect React UI components to backend
  - [x] 10.1 Integrate Dashboard location selector
    - Update Dashboard to use `useLocationSearch` hook
    - Call location search API on user input
    - Display search results and handle selection
    - _Requirements: 2.1, 2.9_
  
  - [x] 10.2 Integrate AQI display components
    - Update AQI card to use `useAQIData` hook
    - Display overall AQI with category and color
    - Show pollutant breakdown with individual AQI values
    - Handle demo data indicator in UI
    - _Requirements: 2.2, 2.9, 2.10_
  
  - [x] 10.3 Integrate Chat page
    - Update Chat page to use `useChat` hook
    - Send messages via `/api/chat` endpoint
    - Display conversation history with proper styling
    - Show loading indicator during AI response
    - _Requirements: 2.3, 2.9_
  
  - [x] 10.4 Integrate Activity recommendations page
    - Update Activity page to use `useRecommendations` hook
    - Pass activity type and health sensitivity to API
    - Display safety assessment and precautions
    - Show time windows with expected AQI ranges
    - _Requirements: 2.4, 2.9_
  
  - [x] 10.5 Integrate Globe map visualization
    - Update Globe page to use `useMapStations` hook
    - Fetch stations based on visible map bounds
    - Display stations with AQI color coding
    - Handle demo data gracefully
    - _Requirements: 2.5, 2.9, 2.10_

- [x] 11. Checkpoint - Test frontend-backend integration locally
  - Run backend with `uvicorn src.api.main:app`
  - Run frontend with `npm run dev`
  - Test all features end-to-end: search, AQI display, chat, recommendations, map
  - Verify error handling and loading states
  - Ensure all tests pass, ask the user if questions arise.

- [x] 12. Configure AWS Amplify deployment
  - [x] 12.1 Create Amplify configuration files
    - Create `amplify.yml` build specification for monorepo
    - Configure frontend build: `cd O-Zone\ UI && npm ci && npm run build`
    - Configure backend package: `cd O-Zone && pip install -r requirements.txt -t ./lib && zip -r function.zip .`
    - Set output directories: frontend `O-Zone UI/dist`, backend `O-Zone/function.zip`
    - _Requirements: 3.1, 3.2, 3.6_
  
  - [x] 12.2 Configure environment variables
    - Create `.env.production` for frontend with `VITE_API_URL`
    - Document required Amplify environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
    - Add environment variable configuration to Amplify console
    - _Requirements: 2.6, 3.4, 3.8_
  
  - [x] 12.3 Set up Lambda function configuration
    - Configure Python 3.11 runtime for Lambda
    - Set handler to `src.api.main.handler`
    - Configure timeout (30 seconds) and memory (512 MB)
    - Add environment variables for AWS Bedrock access
    - _Requirements: 3.2, 3.8_

- [ ] 13. Deploy to AWS Amplify
  - [x] 13.1 Initialize Amplify app
    - Connect Git repository to Amplify console
    - Configure branch (main) for auto-deployment
    - Set up build settings using `amplify.yml`
    - _Requirements: 3.1, 3.7_
  
  - [x] 13.2 Configure API Gateway integration
    - Set up API Gateway REST API for Lambda function
    - Configure routes: `/api/locations/*`, `/api/chat`, `/api/recommendations`, `/api/stations/map`, `/api/health`
    - Enable CORS on API Gateway
    - Link API Gateway URL to frontend `VITE_API_URL`
    - _Requirements: 3.3, 3.9_
  
  - [x] 13.3 Deploy and verify
    - Trigger initial deployment from Amplify console
    - Monitor build logs for errors
    - Test deployed app at Amplify HTTPS URL
    - Verify all endpoints accessible and functional
    - _Requirements: 3.5, 3.6, 3.9_

- [ ] 14. Final validation and demo preparation
  - [x] 14.1 Test all features on deployed app
    - Test location search with various queries
    - Verify AQI data displays correctly with color coding
    - Test chatbot conversation flow
    - Verify AI recommendations with different activities
    - Test map visualization with station data
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 14.2 Verify fallback data handling
    - Simulate OpenAQ API failure (disconnect or rate limit)
    - Confirm demo data loads automatically
    - Verify UI shows appropriate indicators for demo mode
    - Test Bedrock fallback with rule-based recommendations
    - _Requirements: 1.6, 2.10_
  
  - [x] 14.3 Performance and reliability check
    - Test app responsiveness under normal conditions
    - Verify loading states appear during API calls
    - Confirm error messages are user-friendly
    - Test session persistence across page refreshes
    - _Requirements: 2.7, 2.8_

- [x] 15. Final checkpoint - Demo readiness
  - Verify all core features working on live Amplify URL
  - Test demo scenario: search location → view AQI → get recommendations → chat with AI → explore map
  - Confirm fallback data works if external APIs fail during demo
  - Document demo URL and any known limitations
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Focus on hackathon speed: working demo over production polish
- All endpoints use existing Python modules (no new business logic needed)
- Demo data fallback ensures reliability even if external APIs fail
- Single Lambda function simplifies deployment (no microservices complexity)
- No authentication needed for public demo
- CORS allows all origins for demo flexibility
- Session management is in-memory (acceptable for demo, no DynamoDB needed)
- Each task builds incrementally: backend → frontend → integration → deployment
- Checkpoints ensure validation at key milestones
- Tasks reference specific requirements for traceability
