# Requirements Document

## Introduction

This document specifies requirements for redesigning the existing Streamlit application UI to match the modern React design mockup for a hackathon demo. The goal is to update the Streamlit app's visual appearance and layout while keeping all existing functionality (AQI data, chatbot, recommendations) intact. The updated Streamlit app will then be deployed to AWS for the hackathon demonstration.

## Glossary

- **Streamlit_App**: Existing Python/Streamlit application with AQI data, chatbot, and recommendations
- **React_UI_Design**: Visual design reference from "O-Zone UI" folder showing desired look and feel
- **UI_Components**: Streamlit custom components and CSS styling to replicate React design
- **Chatbot_Integration**: Existing chatbot functionality to be integrated into new UI layout
- **OpenAQ_Service**: External API providing real-time air quality data (with demo fallback)
- **Bedrock_Service**: AWS Claude 3.5 Sonnet for AI recommendations and chatbot
- **Deployment_Platform**: AWS hosting solution for Streamlit app (EC2, App Runner, or ECS)
- **Demo_Mode**: Fallback mode using demo data when external APIs unavailable
- **Hackathon_Demo**: Time-constrained demonstration focusing on visual appeal and core features

## Requirements

### Requirement 1: Dashboard UI Redesign

**User Story:** As a hackathon judge, I want to see a modern, polished dashboard, so that the app makes a strong visual impression.

#### Acceptance Criteria

1. THE Streamlit_App SHALL display a header with app logo, location selector, and notification icon
2. THE Streamlit_App SHALL display large circular AQI indicator with color coding (green/yellow/orange/red)
3. THE Streamlit_App SHALL show AQI category text (Good, Moderate, Unhealthy, etc.)
4. THE Streamlit_App SHALL display quick action cards in grid layout (Activity, Globe, Trends, Chat, Safety, Pollutants)
5. THE Streamlit_App SHALL use custom CSS to match React_UI_Design color scheme and typography
6. THE Streamlit_App SHALL display user profile info if available (name, health conditions)
7. THE Streamlit_App SHALL show map preview with station markers
8. THE Streamlit_App SHALL use card-based layout with rounded corners and shadows
9. THE Streamlit_App SHALL be mobile-responsive using existing responsive_styles.py
10. THE Streamlit_App SHALL maintain all existing functionality (location search, AQI calculation)

### Requirement 2: Chat Interface Redesign

**User Story:** As a user, I want a modern chat interface, so that interacting with the AI assistant feels natural and engaging.

#### Acceptance Criteria

1. THE Streamlit_App SHALL display chat interface with message bubbles (user on right, bot on left)
2. THE Streamlit_App SHALL show bot avatar icon and user avatar icon
3. THE Streamlit_App SHALL display message timestamps
4. THE Streamlit_App SHALL show quick question buttons for common queries
5. THE Streamlit_App SHALL use custom CSS for chat bubble styling (rounded, colored backgrounds)
6. THE Streamlit_App SHALL integrate existing chatbot functionality (session_manager, conversation_manager)
7. THE Streamlit_App SHALL show typing indicator while bot is responding
8. THE Streamlit_App SHALL maintain conversation history in session state
9. THE Streamlit_App SHALL display personalized greetings using user profile
10. THE Streamlit_App SHALL use st.chat_message or custom HTML for message display

### Requirement 3: Navigation and Page Structure

**User Story:** As a user, I want easy navigation between features, so that I can explore all app capabilities.

#### Acceptance Criteria

1. THE Streamlit_App SHALL use st.sidebar or custom navigation for page switching
2. THE Streamlit_App SHALL support pages: Dashboard, Activity, Globe, Trends, Chat, Safety, Pollutants, Notifications
3. THE Streamlit_App SHALL highlight active page in navigation
4. THE Streamlit_App SHALL use icons for navigation items (matching React_UI_Design)
5. THE Streamlit_App SHALL maintain session state across page navigation
6. THE Streamlit_App SHALL show back button on detail pages
7. THE Streamlit_App SHALL use st.navigation or custom page routing
8. THE Streamlit_App SHALL preserve user selections (location, activity, health profile) across pages
9. THE Streamlit_App SHALL load pages quickly without full app reload
10. THE Streamlit_App SHALL use consistent header/footer across all pages

### Requirement 4: Visual Styling and Theming

**User Story:** As a hackathon judge, I want the app to look professional and modern, so that it stands out visually.

#### Acceptance Criteria

1. THE Streamlit_App SHALL use custom CSS matching React_UI_Design color palette
2. THE Streamlit_App SHALL use rounded corners on cards and buttons (border-radius: 12-20px)
3. THE Streamlit_App SHALL use box shadows for depth (shadow-lg equivalent)
4. THE Streamlit_App SHALL use gradient backgrounds where appropriate
5. THE Streamlit_App SHALL use consistent spacing and padding (4px, 8px, 12px, 16px, 24px)
6. THE Streamlit_App SHALL use custom fonts if specified in React_UI_Design
7. THE Streamlit_App SHALL use color-coded AQI indicators (green, yellow, orange, red, purple, maroon)
8. THE Streamlit_App SHALL hide Streamlit default header/footer/menu for cleaner look
9. THE Streamlit_App SHALL use icons from lucide-react equivalent or emoji
10. THE Streamlit_App SHALL inject CSS via st.markdown with unsafe_allow_html=True

### Requirement 5: Globe/Map Page Enhancement

**User Story:** As a user, I want to explore air quality globally, so that I can see pollution patterns worldwide.

#### Acceptance Criteria

1. THE Streamlit_App SHALL display interactive map using streamlit-folium
2. THE Streamlit_App SHALL show station markers color-coded by AQI
3. THE Streamlit_App SHALL display station popups with AQI details on click
4. THE Streamlit_App SHALL support map zoom and pan
5. THE Streamlit_App SHALL show station count indicator
6. THE Streamlit_App SHALL use existing demo_data.get_demo_global_stations() for station data
7. THE Streamlit_App SHALL display map legend explaining AQI color coding
8. THE Streamlit_App SHALL center map on selected location or world view
9. THE Streamlit_App SHALL show loading indicator while fetching station data
10. THE Streamlit_App SHALL allow selecting location from map click

### Requirement 6: Activity and Recommendations Page

**User Story:** As a user, I want personalized activity recommendations, so that I can plan outdoor activities safely.

#### Acceptance Criteria

1. THE Streamlit_App SHALL display activity selector (Walking, Running, Cycling, etc.)
2. THE Streamlit_App SHALL display health sensitivity selector (None, Asthma, Allergies, etc.)
3. THE Streamlit_App SHALL show safety assessment badge (Safe, Moderate Risk, Unsafe)
4. THE Streamlit_App SHALL display AI-generated recommendation text
5. THE Streamlit_App SHALL show precautions list in expandable section
6. THE Streamlit_App SHALL show optimal time windows if available
7. THE Streamlit_App SHALL use existing get_recommendation() function
8. THE Streamlit_App SHALL update recommendations when activity or health sensitivity changes
9. THE Streamlit_App SHALL show loading indicator while generating recommendations
10. THE Streamlit_App SHALL display mode indicator (AI-powered vs rule-based)

### Requirement 7: Trends and Historical Data Page

**User Story:** As a user, I want to see air quality trends, so that I can understand pollution patterns over time.

#### Acceptance Criteria

1. THE Streamlit_App SHALL display 24-hour pollutant concentration chart using plotly
2. THE Streamlit_App SHALL show summary statistics (min, avg, max) for each pollutant
3. THE Streamlit_App SHALL use tabs for different time ranges (24 Hours, Summary)
4. THE Streamlit_App SHALL use existing get_historical_measurements() function
5. THE Streamlit_App SHALL display line chart with multiple pollutant traces
6. THE Streamlit_App SHALL show hover tooltips with exact values
7. THE Streamlit_App SHALL handle missing historical data gracefully
8. THE Streamlit_App SHALL use color coding for different pollutants
9. THE Streamlit_App SHALL display chart legend
10. THE Streamlit_App SHALL show "No data available" message when appropriate

### Requirement 8: Pollutants Detail Page

**User Story:** As a user, I want detailed pollutant information, so that I can understand what's affecting air quality.

#### Acceptance Criteria

1. THE Streamlit_App SHALL display individual pollutant cards (PM2.5, PM10, CO, NO2, O3, SO2)
2. THE Streamlit_App SHALL show pollutant AQI value and category for each
3. THE Streamlit_App SHALL use color coding matching overall AQI categories
4. THE Streamlit_App SHALL display pollutant concentration values with units
5. THE Streamlit_App SHALL show health effects for each pollutant
6. THE Streamlit_App SHALL highlight dominant pollutant
7. THE Streamlit_App SHALL use card grid layout (2 columns on mobile, 3 on desktop)
8. THE Streamlit_App SHALL use existing individual_results from calculate_overall_aqi()
9. THE Streamlit_App SHALL show "No data" for pollutants without measurements
10. THE Streamlit_App SHALL display last updated timestamp

### Requirement 9: Safety and Notifications Page

**User Story:** As a user, I want safety alerts and notifications, so that I'm warned about dangerous air quality conditions.

#### Acceptance Criteria

1. THE Streamlit_App SHALL display safety alerts based on current AQI
2. THE Streamlit_App SHALL show health warnings for sensitive groups
3. THE Streamlit_App SHALL display notification history (if implemented)
4. THE Streamlit_App SHALL use alert styling (colored backgrounds, icons)
5. THE Streamlit_App SHALL show precautions specific to user health profile
6. THE Streamlit_App SHALL display emergency contact information for severe AQI
7. THE Streamlit_App SHALL use st.warning, st.error for alert styling
8. THE Streamlit_App SHALL show "All clear" message when AQI is good
9. THE Streamlit_App SHALL prioritize alerts by severity
10. THE Streamlit_App SHALL allow dismissing notifications

### Requirement 10: AWS App Runner Deployment for Hackathon

**User Story:** As a hackathon participant, I want to deploy the Streamlit app to AWS App Runner, so that judges can access a live demo URL quickly and reliably.

#### Acceptance Criteria

1. THE Streamlit_App SHALL be deployed to AWS App Runner
2. THE deployment SHALL use existing requirements.txt for dependencies
3. THE deployment SHALL configure environment variables via App Runner console (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
4. THE deployment SHALL provide HTTPS URL automatically via App Runner
5. THE deployment SHALL complete within 15 minutes from start
6. THE deployment SHALL use Dockerfile with Python 3.11 base image
7. THE deployment SHALL auto-restart on failure via App Runner health checks
8. THE deployment SHALL expose port 8501 for Streamlit
9. THE Dockerfile SHALL include CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
10. THE deployment documentation SHALL include step-by-step App Runner setup instructions with screenshots
