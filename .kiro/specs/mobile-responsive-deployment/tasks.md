# Implementation Plan: Mobile-Responsive Deployment

## Overview

Transform the O-Zone Streamlit air quality monitoring application into a mobile-responsive Progressive Web App (PWA) deployed on AWS App Runner. Implementation prioritizes essential features for tomorrow's hackathon presentation with cost optimization and rapid deployment.

## Tasks

- [ ] 1. Create responsive CSS module
  - [x] 1.1 Create src/responsive_styles.py with CSS generation functions
    - Implement `get_responsive_css()` returning complete responsive CSS string
    - Implement `inject_responsive_styles()` for Streamlit injection
    - Include mobile breakpoint (@media max-width: 768px) with single-column layout
    - Include tablet breakpoint (@media min-width: 769px and max-width: 1024px) with two-column layout
    - Include desktop breakpoint (@media min-width: 1025px) preserving existing layout
    - Define CSS classes: `.mobile-header`, `.mobile-stack`, `.touch-target`, `.collapsible-section`
    - Set touch target minimum sizing: 44px height, 44px width, 8px spacing
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3_
  
  - [ ]* 1.2 Write property test for responsive breakpoints
    - **Property 1: Responsive CSS Contains Required Breakpoints**
    - **Validates: Requirements 1.4**
    - Generate random CSS modifications, verify @media queries at 768px and 1024px always present
    - Run 100 iterations with hypothesis
    - _Requirements: 1.4_
  
  - [ ]* 1.3 Write property test for touch target sizing
    - **Property 2: Touch Targets Meet Accessibility Standards**
    - **Validates: Requirements 2.1, 2.2, 2.3**
    - Parse CSS and verify all touch target selectors have min 44px dimensions and 8px spacing
    - Run 100 iterations with hypothesis
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 2. Create PWA configuration module
  - [x] 2.1 Create src/pwa_config.py with PWA generation functions
    - Implement `generate_manifest()` returning manifest.json dictionary
    - Implement `generate_service_worker()` returning service worker JavaScript
    - Implement `setup_pwa_files()` creating manifest.json and sw.js in static/ directory
    - Manifest must include: name, short_name, start_url, display="standalone", background_color, theme_color
    - Manifest must include icons: 192x192 and 512x512 pixel sizes
    - Service worker: cache-first for static assets, network-first for API calls
    - _Requirements: 5.1, 5.2, 5.3, 5.5_
  
  - [ ]* 2.2 Write property test for PWA manifest completeness
    - **Property 3: PWA Manifest Completeness**
    - **Validates: Requirements 5.1, 5.2, 5.5**
    - Generate manifests with random app names and colors
    - Verify all required fields present, display="standalone", icons include 192x192 and 512x512
    - Run 100 iterations with hypothesis
    - _Requirements: 5.1, 5.2, 5.5_

- [ ] 3. Create static assets for PWA
  - [x] 3.1 Create static/ directory and placeholder icon files
    - Create static/icon-192.png (192x192 placeholder)
    - Create static/icon-512.png (512x512 placeholder)
    - Create static/offline.html (offline fallback page)
    - _Requirements: 5.2_

- [ ] 4. Modify app.py for responsive and PWA support
  - [x] 4.1 Add responsive CSS injection to main() function
    - Import inject_responsive_styles from responsive_styles module
    - Call inject_responsive_styles() at app startup
    - Add error handling with try-except and fallback to default styles
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 4.2 Add PWA setup to main() function
    - Import setup_pwa_files from pwa_config module
    - Call setup_pwa_files() at app startup
    - Add error handling with try-except and info message if PWA unavailable
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [-] 4.3 Add mobile-responsive classes to location input rendering
    - Modify render_location_input() to include `.mobile-header` CSS class
    - Collapse location input and map toggle into compact header on mobile
    - _Requirements: 9.1_
  
  - [ ] 4.4 Add mobile-responsive classes to current conditions rendering
    - Stack current conditions and activity input vertically on mobile
    - Add `.mobile-stack` CSS class to relevant components
    - _Requirements: 9.2_
  
  - [ ] 4.5 Add collapsible menu for historical trends on mobile
    - Implement collapsible section for historical trends using `.collapsible-section`
    - Preserve desktop navigation for larger screens
    - _Requirements: 9.3, 9.4_
  
  - [ ] 4.6 Implement lazy loading for globe visualization
    - Add lazy loading logic to defer globe rendering until user interaction
    - Optimize for mobile performance
    - _Requirements: 6.5_
  
  - [ ] 4.7 Implement location state preservation across view mode switches
    - Ensure selected location persists in session state when switching between text input and globe view
    - _Requirements: 9.5_
  
  - [ ]* 4.8 Write property test for location state preservation
    - **Property 5: Location State Preservation**
    - **Validates: Requirements 9.5**
    - Generate random location data and view modes, verify state unchanged after switch
    - Run 100 iterations with hypothesis
    - _Requirements: 9.5_

- [ ] 5. Implement browser detection and warnings
  - [ ] 5.1 Create browser detection function in src/responsive_styles.py
    - Parse user agent string to detect browser and version
    - Return warning message for unsupported browsers (Chrome <90, Safari <14, Firefox <88, Edge <90)
    - Include supported browser recommendations in warning
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 5.2 Write property test for browser detection warnings
    - **Property 4: Browser Detection Warnings**
    - **Validates: Requirements 7.5**
    - Generate random user agent strings for unsupported browsers
    - Verify function returns warning message with recommendations
    - Run 100 iterations with hypothesis
    - _Requirements: 7.5_

- [ ] 6. Checkpoint - Test responsive features locally
  - Run Streamlit app locally and verify responsive CSS loads
  - Test on browser with responsive design mode (mobile, tablet, desktop)
  - Verify PWA manifest and service worker files are created
  - Ensure all tests pass, ask the user if questions arise

- [ ] 7. Create Docker container configuration
  - [ ] 7.1 Create Dockerfile in project root
    - Use python:3.11-slim as base image
    - Set WORKDIR to /app
    - Copy requirements.txt and run pip install --no-cache-dir
    - Copy src/ and static/ directories
    - Expose port 8501
    - Add HEALTHCHECK with curl to /_stcore/health endpoint
    - Set CMD to run streamlit with port 8501 and address 0.0.0.0
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 7.2 Write unit tests for Dockerfile validation
    - Test Dockerfile contains Python 3.11 base image
    - Test Dockerfile copies requirements.txt and runs pip install
    - Test Dockerfile exposes port 8501
    - Test Dockerfile has CMD to launch Streamlit
    - Test Dockerfile includes HEALTHCHECK instruction
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 8. Create AWS App Runner configuration
  - [ ] 8.1 Create apprunner.yaml in project root
    - Set runtime to python311
    - Configure build commands to install requirements.txt
    - Configure run command to launch Streamlit on port 8501
    - Set network port to 8501
    - Add environment variable for AWS_DEFAULT_REGION
    - _Requirements: 4.1, 4.5_
  
  - [ ]* 8.2 Write unit tests for App Runner configuration validation
    - Test apprunner.yaml references ECR or container registry
    - Test configuration sets min=1, max=2 instances
    - Test configuration includes environment variables
    - Test configuration sets 1 vCPU
    - Test configuration sets 2 GB memory
    - Test configuration sets auto-pause to 5 minutes
    - _Requirements: 4.1, 4.2, 4.5, 8.1, 8.2, 8.3_

- [ ] 9. Create deployment automation script
  - [ ] 9.1 Create deploy.sh in project root
    - Add shebang and usage instructions
    - Implement build_docker_image() function
    - Implement push_to_ecr() function with AWS CLI commands
    - Implement create_or_update_apprunner() function
    - Add validation for AWS credentials and ECR repository existence
    - Add error handling with clear error messages
    - Output public URL after successful deployment
    - Make script executable (chmod +x)
    - _Requirements: 10.3, 10.4_
  
  - [ ]* 9.2 Write unit tests for deployment script validation
    - Test deploy.sh exists and is executable
    - Test script contains required functions
    - _Requirements: 10.3, 10.4_

- [ ] 10. Create deployment documentation
  - [ ] 10.1 Create DEPLOYMENT.md in project root
    - Document prerequisites: AWS CLI, Docker, AWS credentials
    - Document step-by-step deployment instructions
    - Document how to create ECR repository
    - Document how to configure App Runner service settings (CPU, memory, auto-pause)
    - Document how to access deployed application URL
    - Document cost optimization settings
    - Document troubleshooting common deployment issues
    - _Requirements: 10.5_
  
  - [ ]* 10.2 Write unit test for deployment documentation existence
    - Test DEPLOYMENT.md exists
    - Test Dockerfile exists
    - Test apprunner.yaml exists
    - _Requirements: 10.1, 10.2, 10.5_

- [ ] 11. Final checkpoint and integration testing
  - Build Docker image locally and test container runs
  - Deploy to AWS App Runner using deploy.sh script
  - Verify deployment completes within 10 minutes
  - Test deployed application on actual mobile device
  - Test PWA install prompt on mobile browser
  - Verify touch targets are easily tappable
  - Verify no horizontal scrolling on mobile
  - Test location input and globe view on mobile
  - Verify App Runner auto-pause after 5 minutes of inactivity
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Focus on tasks 1-6 first to get responsive UI working locally before deployment
- Tasks 7-10 handle Docker and AWS deployment configuration
- Each task references specific requirements for traceability
- Property tests use hypothesis library (already in requirements.txt) with 100 iterations each
- Manual integration testing checklist in task 11 for hackathon demo validation
- Cost optimization: 1 vCPU, 2 GB memory, auto-pause after 5 minutes, max 2 instances
- Existing AWS Bedrock and OpenAQ integrations remain unchanged
