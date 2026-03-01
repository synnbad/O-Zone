# Requirements Document

## Introduction

This feature enables unified deployment of the O-Zone FastAPI backend alongside the existing frontend through AWS Amplify. Currently, the frontend deploys via amplify.yml while the backend requires separate Lambda packaging and manual deployment. This feature consolidates both deployments into a single Amplify build process, eliminating manual Lambda deployment steps and providing a single API endpoint accessible to the frontend.

## Glossary

- **Amplify_Build_System**: AWS Amplify's CI/CD service that builds and deploys web applications
- **FastAPI_Backend**: The Python-based REST API application in the src/ directory using FastAPI framework
- **Frontend**: The React-based user interface in the O-Zone-UI directory
- **Backend_Build_Phase**: The section of amplify.yml that installs dependencies and prepares the FastAPI application
- **API_Endpoint**: The URL where the deployed FastAPI backend is accessible
- **Environment_Variables**: Configuration values required by the backend (AWS credentials, API keys, model IDs)
- **Deployment_Artifact**: The packaged backend code and dependencies ready for deployment
- **CORS_Configuration**: Cross-Origin Resource Sharing settings allowing frontend to call backend
- **Health_Check_Endpoint**: The /api/health endpoint used to verify backend deployment status

## Requirements

### Requirement 1: Backend Build Configuration

**User Story:** As a developer, I want the Amplify build system to install Python dependencies and prepare the FastAPI backend, so that the backend is ready for deployment alongside the frontend.

#### Acceptance Criteria

1. WHEN the Amplify build starts, THE Amplify_Build_System SHALL install Python 3.11 or higher
2. WHEN Python is installed, THE Amplify_Build_System SHALL install all dependencies from requirements.txt
3. WHEN dependencies are installed, THE Amplify_Build_System SHALL copy the src/ directory to the deployment artifact
4. THE Backend_Build_Phase SHALL complete before the frontend build phase starts
5. IF dependency installation fails, THEN THE Amplify_Build_System SHALL halt the build and report the error

### Requirement 2: Backend Deployment Artifact

**User Story:** As a developer, I want the backend code and dependencies packaged correctly, so that the FastAPI application can run in the Amplify hosting environment.

#### Acceptance Criteria

1. THE Deployment_Artifact SHALL include all Python dependencies from requirements.txt
2. THE Deployment_Artifact SHALL include the complete src/ directory structure
3. THE Deployment_Artifact SHALL include the FastAPI application entry point (src/api/main.py)
4. THE Deployment_Artifact SHALL exclude unnecessary files (.pyc, __pycache__, .env files)
5. WHEN the artifact is deployed, THE FastAPI_Backend SHALL be executable via the Mangum handler

### Requirement 3: Environment Variable Configuration

**User Story:** As a developer, I want to configure backend environment variables through Amplify, so that the backend can access AWS services and external APIs without hardcoding credentials.

#### Acceptance Criteria

1. THE Amplify_Build_System SHALL support configuration of AWS_REGION as an environment variable
2. THE Amplify_Build_System SHALL support configuration of AWS_ACCESS_KEY_ID as an environment variable
3. THE Amplify_Build_System SHALL support configuration of AWS_SECRET_ACCESS_KEY as an environment variable
4. THE Amplify_Build_System SHALL support configuration of BEDROCK_MODEL_ID as an environment variable
5. THE Amplify_Build_System SHALL support configuration of OPENAQ_API_KEY as an environment variable
6. WHEN environment variables are not set, THE FastAPI_Backend SHALL log a warning and use default values where applicable

### Requirement 4: API Endpoint Accessibility

**User Story:** As a frontend developer, I want a stable API endpoint for the backend, so that the frontend can make HTTP requests to backend services.

#### Acceptance Criteria

1. WHEN the backend is deployed, THE Amplify_Build_System SHALL provide an API_Endpoint URL
2. THE API_Endpoint SHALL be accessible via HTTPS protocol
3. THE API_Endpoint SHALL route requests with /api prefix to the FastAPI_Backend
4. WHEN a request is made to the API_Endpoint, THE FastAPI_Backend SHALL respond within 30 seconds
5. THE API_Endpoint SHALL remain stable across deployments (not change with each build)

### Requirement 5: CORS Configuration

**User Story:** As a frontend developer, I want the backend to accept requests from the frontend domain, so that browser security policies allow API calls.

#### Acceptance Criteria

1. THE CORS_Configuration SHALL allow requests from the Amplify frontend domain
2. THE CORS_Configuration SHALL allow all HTTP methods (GET, POST, PUT, DELETE, OPTIONS)
3. THE CORS_Configuration SHALL allow all standard headers
4. THE CORS_Configuration SHALL allow credentials in requests
5. WHEN a preflight OPTIONS request is received, THE FastAPI_Backend SHALL respond with appropriate CORS headers

### Requirement 6: Health Check and Verification

**User Story:** As a developer, I want to verify the backend is running correctly after deployment, so that I can confirm the deployment succeeded.

#### Acceptance Criteria

1. THE FastAPI_Backend SHALL expose a Health_Check_Endpoint at /api/health
2. WHEN the Health_Check_Endpoint is called, THE FastAPI_Backend SHALL return HTTP status 200
3. WHEN the Health_Check_Endpoint is called, THE FastAPI_Backend SHALL return a JSON response with service status
4. THE Health_Check_Endpoint SHALL respond within 5 seconds
5. WHEN the backend deployment completes, THE Amplify_Build_System SHALL verify the Health_Check_Endpoint is accessible

### Requirement 7: Unified Deployment Process

**User Story:** As a developer, I want to deploy both frontend and backend with a single command, so that I can streamline the deployment workflow.

#### Acceptance Criteria

1. WHEN amplify.yml is committed to the repository, THE Amplify_Build_System SHALL automatically trigger a build
2. THE Amplify_Build_System SHALL build both the frontend and backend in a single build process
3. WHEN the build completes successfully, THE Amplify_Build_System SHALL deploy both frontend and backend
4. IF either frontend or backend build fails, THEN THE Amplify_Build_System SHALL not deploy either component
5. THE Amplify_Build_System SHALL provide build logs for both frontend and backend phases

### Requirement 8: Backward Compatibility

**User Story:** As a developer, I want the existing frontend deployment to continue working, so that adding backend deployment doesn't break the current setup.

#### Acceptance Criteria

1. THE Frontend SHALL continue to build using the existing npm build process
2. THE Frontend SHALL continue to deploy to the same Amplify hosting location
3. THE Frontend artifacts SHALL remain in the O-Zone-UI/dist directory
4. THE Frontend cache configuration SHALL remain unchanged
5. WHEN backend deployment is added, THE Frontend deployment process SHALL not be modified

### Requirement 9: Error Handling and Logging

**User Story:** As a developer, I want clear error messages when deployment fails, so that I can quickly identify and fix issues.

#### Acceptance Criteria

1. WHEN a Python dependency fails to install, THE Amplify_Build_System SHALL log the specific package name and error
2. WHEN the backend build fails, THE Amplify_Build_System SHALL display the error in the build console
3. WHEN environment variables are missing, THE FastAPI_Backend SHALL log which variables are not configured
4. WHEN the backend fails to start, THE Amplify_Build_System SHALL capture and display the startup error
5. THE Amplify_Build_System SHALL retain build logs for at least 30 days

### Requirement 10: Performance and Resource Limits

**User Story:** As a developer, I want the backend to handle expected load, so that the application performs well for users.

#### Acceptance Criteria

1. THE FastAPI_Backend SHALL handle at least 100 concurrent requests
2. THE FastAPI_Backend SHALL respond to /api/locations requests within 2 seconds
3. THE FastAPI_Backend SHALL respond to /api/chat requests within 10 seconds
4. WHEN memory usage exceeds 512 MB, THE FastAPI_Backend SHALL log a warning
5. WHEN request timeout is reached, THE FastAPI_Backend SHALL return HTTP status 504 with a timeout message
