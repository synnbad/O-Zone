# O-Zone Architecture Documentation

This document describes the two deployment architectures for the O-Zone Air Quality Decision Platform.

---

## System 1: Streamlit Application (Development/Prototype)

### Architecture Overview

```mermaid
graph TB
    subgraph "User Device"
        Browser[Web Browser]
    end
    
    subgraph "Local/Server Deployment"
        StreamlitApp[Streamlit Application<br/>Python + Streamlit]
        
        subgraph "Embedded Components"
            UI[UI Layer<br/>Streamlit Components]
            DataFetcher[Data Fetcher<br/>OpenAQ Client]
            AQICalc[AQI Calculator<br/>EPA Standards]
            AIClient[Bedrock Client<br/>Claude Integration]
        end
    end
    
    subgraph "External Services"
        OpenAQ[OpenAQ API<br/>Air Quality Data]
        Bedrock[AWS Bedrock<br/>Claude 3.5 Sonnet]
        Nominatim[Nominatim API<br/>Geocoding]
    end
    
    Browser -->|HTTP :8501| StreamlitApp
    StreamlitApp --> UI
    UI --> DataFetcher
    UI --> AQICalc
    UI --> AIClient
    
    DataFetcher -->|REST API| OpenAQ
    DataFetcher -->|REST API| Nominatim
    AIClient -->|AWS SDK| Bedrock
    
    style StreamlitApp fill:#4A90E2
    style Browser fill:#50C878
    style OpenAQ fill:#FF6B6B
    style Bedrock fill:#FF9500
    style Nominatim fill:#9B59B6
```

### Component Details

**Technology Stack:**
- **Frontend**: Streamlit (Python-based UI framework)
- **Backend**: Embedded Python modules
- **Visualization**: Plotly, Folium (OpenStreetMap)
- **Deployment**: Single server (local or cloud VM)

**Key Features:**
- Monolithic architecture (UI + Backend in one app)
- Real-time interactive components
- Session-based state management
- Direct API calls from server

**Deployment Options:**
- Local: `streamlit run src/app.py`
- Server: Streamlit Cloud, EC2, or any Python hosting

**Limitations:**
- Single server scalability
- Limited mobile optimization
- Stateful sessions (not horizontally scalable)

---

## System 2: React + AWS Serverless (Production)

### Architecture Overview

```mermaid
graph TB
    subgraph "User Devices"
        Desktop[Desktop Browser]
        Mobile[Mobile Browser]
        PWA[PWA App]
    end
    
    subgraph "AWS Amplify - Frontend Hosting"
        AmplifyApp[Amplify Hosting<br/>CDN + Static Assets]
        ReactApp[React Application<br/>TypeScript + Vite]
        
        subgraph "React Components"
            UIComponents[UI Components<br/>Material-UI + Radix]
            StateManagement[State Management<br/>React Hooks]
            APIClient[API Client<br/>Axios]
        end
    end
    
    subgraph "AWS API Gateway"
        HTTPGateway[HTTP API Gateway<br/>z027fnomoh]
    end
    
    subgraph "AWS Lambda"
        LambdaFunction[Lambda Function<br/>o-zone-api<br/>Python 3.14]
        
        subgraph "FastAPI Application"
            FastAPI[FastAPI Framework<br/>Mangum Adapter]
            LocationRouter[Location Router<br/>/api/locations]
            StationRouter[Station Router<br/>/api/stations]
            RecommendRouter[Recommendation Router<br/>/api/recommendations]
            ChatRouter[Chat Router<br/>/api/chat]
        end
    end
    
    subgraph "External Services"
        OpenAQ2[OpenAQ API<br/>Air Quality Data]
        Bedrock2[AWS Bedrock<br/>Claude Opus 4.6]
        Nominatim2[Nominatim API<br/>Geocoding]
    end
    
    Desktop -->|HTTPS| AmplifyApp
    Mobile -->|HTTPS| AmplifyApp
    PWA -->|HTTPS| AmplifyApp
    
    AmplifyApp --> ReactApp
    ReactApp --> UIComponents
    ReactApp --> StateManagement
    ReactApp --> APIClient
    
    APIClient -->|REST API<br/>HTTPS| HTTPGateway
    HTTPGateway -->|Lambda Proxy| LambdaFunction
    
    LambdaFunction --> FastAPI
    FastAPI --> LocationRouter
    FastAPI --> StationRouter
    FastAPI --> RecommendRouter
    FastAPI --> ChatRouter
    
    LocationRouter -->|REST API| Nominatim2
    StationRouter -->|REST API| OpenAQ2
    RecommendRouter -->|REST API| OpenAQ2
    RecommendRouter -->|AWS SDK| Bedrock2
    ChatRouter -->|AWS SDK| Bedrock2
    
    style AmplifyApp fill:#FF9900
    style LambdaFunction fill:#FF9900
    style HTTPGateway fill:#FF9900
    style Bedrock2 fill:#FF9500
    style ReactApp fill:#61DAFB
    style FastAPI fill:#009688
    style Desktop fill:#50C878
    style Mobile fill:#50C878
    style PWA fill:#50C878
```

### Detailed Component Architecture

```mermaid
graph LR
    subgraph "Frontend Layer"
        A[React App<br/>Amplify Hosted]
        A1[Location Search]
        A2[Map Visualization]
        A3[AQI Display]
        A4[Recommendations]
        A5[Chat Interface]
    end
    
    subgraph "API Layer"
        B[API Gateway<br/>HTTP API]
        B1[CORS Config]
        B2[Request Routing]
        B3[Lambda Integration]
    end
    
    subgraph "Business Logic Layer"
        C[Lambda Function<br/>FastAPI]
        C1[Location Service]
        C2[AQI Calculator]
        C3[Recommendation Engine]
        C4[Chat Service]
    end
    
    subgraph "Data Layer"
        D1[OpenAQ API]
        D2[Nominatim API]
        D3[Demo Data Store]
    end
    
    subgraph "AI Layer"
        E[AWS Bedrock<br/>Claude Opus 4.6]
    end
    
    A --> A1 & A2 & A3 & A4 & A5
    A1 & A2 & A3 & A4 & A5 --> B
    B --> B1 & B2 & B3
    B3 --> C
    C --> C1 & C2 & C3 & C4
    C1 --> D2
    C2 --> D1 & D3
    C3 --> D1 & D3 & E
    C4 --> E
    
    style A fill:#61DAFB
    style B fill:#FF9900
    style C fill:#009688
    style E fill:#FF9500
```

### Technology Stack

**Frontend:**
- React 18.3.1 + TypeScript
- Vite 6.3.5 (build tool)
- Material-UI 7.3.5
- Radix UI (accessible components)
- Axios (HTTP client)
- React Router 7.13.0

**Backend:**
- FastAPI (Python web framework)
- Mangum (AWS Lambda adapter)
- Pydantic 2.10+ (data validation)
- Python 3.14

**AWS Services:**
- Amplify (frontend hosting + CI/CD)
- Lambda (serverless compute)
- API Gateway (HTTP API)
- Bedrock (AI/ML inference)
- S3 (Lambda package storage)

**External APIs:**
- OpenAQ (air quality data)
- Nominatim (geocoding)

### Data Flow

```mermaid
sequenceDiagram
    participant User
    participant React as React App<br/>(Amplify)
    participant Gateway as API Gateway
    participant Lambda as Lambda Function<br/>(FastAPI)
    participant OpenAQ as OpenAQ API
    participant Bedrock as AWS Bedrock
    
    User->>React: Search Location "London"
    React->>Gateway: GET /api/locations/search?q=London
    Gateway->>Lambda: Invoke Lambda
    Lambda->>OpenAQ: Query location data
    OpenAQ-->>Lambda: Location + coordinates
    Lambda-->>Gateway: JSON response
    Gateway-->>React: Location data
    React-->>User: Display location
    
    User->>React: Select activity "Walking"
    React->>Gateway: GET /api/recommendations?location=London&activity=Walking
    Gateway->>Lambda: Invoke Lambda
    Lambda->>OpenAQ: Get current AQI
    OpenAQ-->>Lambda: AQI data
    Lambda->>Bedrock: Generate recommendation<br/>(Claude Opus 4.6)
    Bedrock-->>Lambda: AI recommendation
    Lambda-->>Gateway: JSON response
    Gateway-->>React: Recommendation data
    React-->>User: Display recommendation
```

### Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        Dev[Developer]
        Git[GitHub Repository]
    end
    
    subgraph "CI/CD Pipeline"
        Amplify[AWS Amplify<br/>Build & Deploy]
        CloudShell[AWS CloudShell<br/>Lambda Package Build]
    end
    
    subgraph "Production Environment"
        subgraph "Frontend"
            CDN[CloudFront CDN]
            S3Frontend[S3 Bucket<br/>Static Assets]
        end
        
        subgraph "Backend"
            APIGW[API Gateway<br/>z027fnomoh]
            LambdaFunc[Lambda Function<br/>o-zone-api]
            S3Lambda[S3 Bucket<br/>Lambda Package]
        end
    end
    
    subgraph "Monitoring"
        CloudWatch[CloudWatch Logs]
    end
    
    Dev -->|git push| Git
    Git -->|webhook| Amplify
    Amplify -->|deploy| CDN
    CDN --> S3Frontend
    
    Dev -->|build script| CloudShell
    CloudShell -->|upload| S3Lambda
    S3Lambda -->|update code| LambdaFunc
    
    APIGW --> LambdaFunc
    LambdaFunc -->|logs| CloudWatch
    
    style Amplify fill:#FF9900
    style CDN fill:#FF9900
    style APIGW fill:#FF9900
    style LambdaFunc fill:#FF9900
    style CloudWatch fill:#FF9900
```

### API Endpoints

**Base URL:** `https://z027fnomoh.execute-api.us-east-1.amazonaws.com`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/locations/search` | GET | Search locations by name |
| `/api/stations/map` | GET | Get global monitoring stations |
| `/api/recommendations` | GET | Get AI-powered recommendations |
| `/api/chat` | POST | Chat with AI assistant |

### Environment Configuration

**Amplify Environment Variables:**
```
VITE_API_URL=https://z027fnomoh.execute-api.us-east-1.amazonaws.com
```

**Lambda Environment Variables:**
```
OZONE_AWS_REGION=us-east-1
OZONE_AWS_ACCESS_KEY_ID=<credentials>
OZONE_AWS_SESSION_TOKEN=<token>
BEDROCK_MODEL_ID=arn:aws:bedrock:us-east-1:559050222547:inference-profile/global.anthropic.claude-opus-4-6-v1
OPENAQ_API_KEY=<api-key>
```

### Scalability & Performance

**Frontend (Amplify):**
- Global CDN distribution
- Automatic scaling
- Edge caching
- HTTPS by default

**Backend (Lambda):**
- Auto-scaling (0 to 1000s of concurrent executions)
- Pay-per-request pricing
- 512 MB memory allocation
- 30-second timeout
- Cold start: ~2 seconds
- Warm execution: ~100-300ms

**API Gateway:**
- 10,000 requests/second default limit
- Automatic DDoS protection
- Request throttling
- CORS enabled

### Security

**Frontend:**
- HTTPS only
- Content Security Policy
- XSS protection
- CORS configured

**Backend:**
- IAM role-based access
- API Gateway authorization
- Lambda execution role
- Environment variable encryption
- VPC isolation (optional)

**AI/ML:**
- Bedrock IAM permissions
- Model access controls
- Request/response logging

---

## Comparison: Streamlit vs React + Lambda

| Feature | Streamlit App | React + Lambda |
|---------|---------------|----------------|
| **Architecture** | Monolithic | Microservices |
| **Scalability** | Vertical (single server) | Horizontal (serverless) |
| **Cost** | Fixed (server cost) | Variable (pay-per-use) |
| **Deployment** | Manual or Streamlit Cloud | Automated CI/CD |
| **Mobile Support** | Basic responsive | Full PWA support |
| **API** | Internal functions | RESTful API |
| **State Management** | Server-side sessions | Client-side + API |
| **Cold Start** | N/A (always running) | ~2 seconds |
| **Concurrent Users** | Limited by server | Unlimited (auto-scale) |
| **Development Speed** | Fast (Python only) | Moderate (Full-stack) |
| **Production Ready** | Prototype/Demo | Enterprise-grade |
| **Maintenance** | Server management | Serverless (AWS managed) |

---

## Recommended Use Cases

### Streamlit App
- Internal tools and dashboards
- Data science prototypes
- Quick MVPs and demos
- Development and testing
- Small user base (<100 concurrent)

### React + Lambda
- Production applications
- Public-facing websites
- Mobile-first applications
- High-traffic scenarios
- Enterprise deployments
- Global user base

---

## URLs

**Streamlit App (Local):**
- `http://localhost:8501`

**React + Lambda (Production):**
- Frontend: `https://main.d32w9y2132m03m.amplifyapp.com`
- Backend API: `https://z027fnomoh.execute-api.us-east-1.amazonaws.com`

---

## Cost Estimation (React + Lambda)

**Monthly Costs (estimated for 10,000 users):**

| Service | Usage | Cost |
|---------|-------|------|
| Amplify Hosting | 100 GB bandwidth | $1.50 |
| Lambda | 1M requests, 512MB | $0.20 |
| API Gateway | 1M requests | $1.00 |
| Bedrock (Claude) | 100K recommendations | $40.00 |
| CloudWatch Logs | 10 GB | $5.00 |
| **Total** | | **~$48/month** |

**Streamlit App (EC2 t3.medium):**
- Fixed cost: ~$30-40/month (24/7 running)
- Does not auto-scale

---

## Future Enhancements

**Potential Additions:**
- DynamoDB for caching AQI data
- ElastiCache for session management
- Cognito for user authentication
- S3 for user preferences storage
- CloudFront for additional caching
- WAF for advanced security
- Route53 for custom domain

---

*Last Updated: March 1, 2026*
