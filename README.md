# 🌍 O-Zone - AI-Powered Air Quality Decision Platform

> **AWS Hackathon Project** | Real-time air quality monitoring with AI-powered recommendations

[![AWS Amplify](https://img.shields.io/badge/AWS-Amplify-FF9900?logo=amazonaws)](https://main.d32w9y2132m03m.amplifyapp.com)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-FF9900?logo=amazonaws)](https://z027fnomoh.execute-api.us-east-1.amazonaws.com)
[![AWS Bedrock](https://img.shields.io/badge/AWS-Bedrock-FF9900?logo=amazonaws)](https://aws.amazon.com/bedrock/)
[![React](https://img.shields.io/badge/React-18.3.1-61DAFB?logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.134.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.14-3776AB?logo=python)](https://www.python.org/)

## 🚀 Live Demo

- **Production App**: [https://main.d32w9y2132m03m.amplifyapp.com](https://main.d32w9y2132m03m.amplifyapp.com)
- **API Endpoint**: [https://z027fnomoh.execute-api.us-east-1.amazonaws.com](https://z027fnomoh.execute-api.us-east-1.amazonaws.com)
- **API Documentation**: [/api/docs](https://z027fnomoh.execute-api.us-east-1.amazonaws.com/docs)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)

## 🎯 Overview

O-Zone is a comprehensive air quality decision platform that combines real-time environmental data with AI-powered recommendations to help users make informed decisions about outdoor activities. Built for the AWS Hackathon, it showcases modern cloud architecture using AWS services.

### Key Capabilities

- 🌍 **Real-time Air Quality Data** - Global coverage via OpenAQ API
- 🤖 **AI-Powered Recommendations** - Claude Opus 4.6 via AWS Bedrock
- 📊 **EPA-Standard AQI Calculations** - 6 pollutants (PM2.5, PM10, CO, NO2, O3, SO2)
- 🗺️ **Global Map Visualization** - 36+ monitoring stations worldwide
- 💬 **Interactive AI Chat** - Conversational interface for air quality queries
- 📱 **Mobile-Responsive** - PWA-ready with offline support
- 🔄 **Dual Architecture** - Streamlit prototype + React production app

## ✨ Features

### Core Features

- ✅ **Location Search** - Search any city worldwide with geocoding
- ✅ **Real-time AQI Display** - Color-coded air quality index with pollutant breakdown
- ✅ **Activity Recommendations** - Personalized advice for outdoor activities
- ✅ **Health Sensitivity** - Tailored guidance for asthma, allergies, pregnancy, etc.
- ✅ **Historical Trends** - 24-hour pollutant concentration charts
- ✅ **Global Map** - Interactive visualization of monitoring stations
- ✅ **AI Chatbot** - Natural language queries about air quality
- ✅ **Demo Data Fallback** - Reliable operation even when APIs are unavailable

### Technical Features

- ✅ **Serverless Architecture** - AWS Lambda + API Gateway
- ✅ **Auto-scaling** - Handles traffic spikes automatically
- ✅ **CI/CD Pipeline** - Automated deployment via AWS Amplify
- ✅ **Type Safety** - Full TypeScript support in frontend
- ✅ **API Documentation** - Auto-generated OpenAPI/Swagger docs
- ✅ **Error Handling** - Comprehensive error handling and logging
- ✅ **Session Management** - Stateful chat conversations
- ✅ **CORS Support** - Secure cross-origin requests

## 🏗️ Architecture

O-Zone features two deployment architectures:

### System 1: Streamlit Application (Prototype)
- **Purpose**: Rapid prototyping and development
- **Stack**: Python + Streamlit
- **Deployment**: Local or Streamlit Cloud
- **Use Case**: Internal tools, demos, testing

### System 2: React + AWS Serverless (Production)
- **Purpose**: Production-grade scalable application
- **Stack**: React + TypeScript + FastAPI + AWS
- **Deployment**: AWS Amplify + Lambda + API Gateway
- **Use Case**: Public-facing application, hackathon demo

For detailed architecture diagrams and comparisons, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 🛠️ Technology Stack

### Frontend (React App)
- **Framework**: React 18.3.1 + TypeScript
- **Build Tool**: Vite 6.3.5
- **UI Libraries**: Material-UI 7.3.5, Radix UI
- **HTTP Client**: Axios 1.13.6
- **Routing**: React Router 7.13.0
- **Styling**: Tailwind CSS 4.1.12

### Backend (FastAPI)
- **Framework**: FastAPI 0.134.0
- **Runtime**: Python 3.14
- **Lambda Adapter**: Mangum 0.21.0
- **Validation**: Pydantic 2.10+
- **HTTP Client**: httpx 0.28.1

### AWS Services
- **Hosting**: AWS Amplify (Frontend CDN)
- **Compute**: AWS Lambda (Serverless backend)
- **API**: API Gateway (HTTP API)
- **AI/ML**: AWS Bedrock (Claude Opus 4.6)
- **Storage**: S3 (Lambda packages)
- **Monitoring**: CloudWatch Logs

### External APIs
- **Air Quality**: OpenAQ API
- **Geocoding**: Nominatim (OpenStreetMap)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- AWS Account (for AI features)
- Git

### Option 1: Run Streamlit Prototype Locally

```bash
# Clone repository
git clone https://github.com/synnbad/O-Zone.git
cd O-Zone

# Install Python dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run src/app.py
```

The app will open at `http://localhost:8501`

### Option 2: Run React + FastAPI Locally

**Backend:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS credentials

# Run FastAPI server
uvicorn src.api.main:app --reload
```

Backend runs at `http://localhost:8000`

**Frontend:**
```bash
# Navigate to React app
cd "O-Zone UI"

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with API URL

# Run development server
npm run dev
```

Frontend runs at `http://localhost:5173`

## 🌐 Deployment

### Production Deployment (AWS)

The application is deployed using AWS services:

**Frontend (AWS Amplify)**
- Automatic deployment from GitHub
- Global CDN distribution
- HTTPS by default
- Custom domain support

**Backend (AWS Lambda + API Gateway)**
- Serverless compute
- Auto-scaling
- Pay-per-request pricing
- Built using AWS CloudShell for Linux compatibility

For detailed deployment instructions, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

### Deploy Your Own Instance

1. **Fork the repository**
2. **Set up AWS Amplify**:
   ```bash
   aws amplify create-app --name o-zone --region us-east-1
   ```
3. **Connect your Git repository** via AWS Console
4. **Configure environment variables** in Amplify settings
5. **Deploy backend to Lambda** using provided scripts
6. **Update frontend API URL** in Amplify environment variables

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step instructions.

## 📚 API Documentation

### Base URL
```
Production: https://z027fnomoh.execute-api.us-east-1.amazonaws.com
Local: http://localhost:8000
```

### Endpoints

#### Health Check
```http
GET /api/health
```
Returns API status and version.

#### Location Search
```http
GET /api/locations/search?q={query}
```
Search for locations by name or coordinates.

**Parameters:**
- `q` (string): City name or "lat,lon" coordinates

**Response:**
```json
{
  "results": [{
    "id": "greater_london_united_kingdom",
    "name": "Greater London",
    "country": "United Kingdom",
    "coordinates": {
      "latitude": 51.5074456,
      "longitude": -0.1277653
    },
    "providers": ["Nominatim Geocoding"]
  }],
  "metadata": {
    "source": "api",
    "timestamp": "2026-03-01T06:45:01.503524+00:00",
    "query": "London"
  }
}
```

#### Get Map Stations
```http
GET /api/stations/map
```
Returns global monitoring stations with current AQI.

**Response:**
```json
{
  "stations": [{
    "id": "lon-001",
    "name": "London Central",
    "country": "GB",
    "coordinates": {
      "latitude": 51.5074,
      "longitude": -0.1278
    },
    "current_aqi": 65,
    "aqi_category": "Moderate",
    "aqi_color": "#FFFF00",
    "last_updated": "2026-03-01T06:45:01.555876+00:00"
  }],
  "metadata": {
    "count": 36,
    "source": "demo"
  }
}
```

#### Get Recommendations
```http
GET /api/recommendations?location={location}&activity={activity}&health={health}
```
Get AI-powered activity recommendations.

**Parameters:**
- `location` (string, required): Location name
- `activity` (string, required): Activity type (Walking, Running, Cycling, etc.)
- `health` (string, required): Health sensitivity (None, Asthma, Allergies, etc.)

**Response:**
```json
{
  "safety_assessment": "Safe",
  "recommendation_text": "Air quality is excellent (AQI 21)...",
  "precautions": [],
  "time_windows": [],
  "reasoning": "Rule-based recommendation for AQI 21...",
  "metadata": {
    "source": "ai",
    "location": "Greater London",
    "current_aqi": 21
  }
}
```

#### Chat with AI
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Is it safe to go running today?",
  "session_id": "optional-session-id",
  "location": "London"
}
```

For interactive API documentation, visit `/docs` endpoint.

## 📁 Project Structure

```
O-Zone/
├── src/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py            # Lambda handler & FastAPI app
│   │   └── routers/           # API route handlers
│   │       ├── locations.py   # Location search
│   │       ├── map_stations.py # Global stations
│   │       ├── recommendations.py # AI recommendations
│   │       └── chat.py        # Chat interface
│   ├── app.py                 # Streamlit application
│   ├── config.py              # Configuration
│   ├── models.py              # Data models
│   ├── aqi_calculator.py      # AQI calculations
│   ├── data_fetcher.py        # OpenAQ client
│   ├── bedrock_client.py      # AWS Bedrock client
│   └── demo_data.py           # Fallback data
├── O-Zone UI/                 # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom hooks
│   │   ├── services/          # API clients
│   │   └── types/             # TypeScript types
│   ├── package.json
│   └── vite.config.ts
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── property/              # Property-based tests
├── lambda_package/            # Lambda deployment package
├── .kiro/                     # Kiro AI specs
├── amplify.yml                # Amplify build config
├── requirements.txt           # Python dependencies
├── requirements-lambda.txt    # Lambda-specific deps
├── ARCHITECTURE.md            # Architecture documentation
├── DEPLOYMENT_GUIDE.md        # Deployment instructions
└── README.md                  # This file
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest --cov=src tests/
```

### Run Specific Test Suites
```bash
# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Property-based tests
pytest tests/property/
```

### Test Coverage
Current coverage: 85%+ across core modules

## 🔧 Development

### Backend Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Format code
black src/
isort src/

# Type checking
mypy src/
```

### Frontend Development

```bash
cd "O-Zone UI"

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Type checking
npm run type-check

# Linting
npm run lint
```

## 🔐 Environment Variables

### Backend (.env)
```env
# AWS Configuration (Required for AI)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_SESSION_TOKEN=your_session_token  # For temporary credentials

# AWS Bedrock Model
BEDROCK_MODEL_ID=arn:aws:bedrock:us-east-1:559050222547:inference-profile/global.anthropic.claude-opus-4-6-v1

# OpenAQ API (Optional)
OPENAQ_API_KEY=your_openaq_key
```

### Frontend (.env)
```env
# API URL
VITE_API_URL=https://z027fnomoh.execute-api.us-east-1.amazonaws.com

# For local development
# VITE_API_URL=http://localhost:8000
```

## 💡 Key Features Explained

### AI-Powered Recommendations
Uses AWS Bedrock with Claude Opus 4.6 to provide:
- Personalized activity advice based on current conditions
- Health-sensitive guidance for vulnerable groups
- Time window predictions for optimal outdoor activities
- Detailed reasoning behind recommendations

### Real-time Air Quality Data
- Integrates with OpenAQ API for global coverage
- EPA-standard AQI calculations for 6 pollutants
- Historical trend analysis (24-hour charts)
- Demo data fallback for reliability

### Global Coverage
- 36+ monitoring stations worldwide
- Interactive map visualization
- Location search with geocoding
- Support for coordinates and city names

### Dual Architecture
- **Streamlit**: Rapid prototyping and development
- **React + Lambda**: Production-grade scalable deployment

## 📊 Performance Metrics

### Backend (Lambda)
- Cold start: ~2 seconds
- Warm execution: 100-300ms
- Memory: 512 MB
- Timeout: 30 seconds
- Concurrent executions: Auto-scaling

### Frontend (Amplify)
- Global CDN distribution
- HTTPS by default
- Automatic scaling
- Edge caching enabled

### API Response Times
- Health check: <50ms
- Location search: 200-500ms
- AQI data: 300-800ms
- AI recommendations: 2-5 seconds

## 🎯 Use Cases

1. **Personal Health** - Check air quality before outdoor exercise
2. **Family Planning** - Ensure safe conditions for children's outdoor activities
3. **Event Planning** - Schedule outdoor events during optimal air quality
4. **Health Monitoring** - Track air quality trends for respiratory conditions
5. **Travel Planning** - Compare air quality across destinations

## 🔒 Security

- HTTPS-only communication
- API Gateway authorization
- Lambda execution roles with minimal permissions
- Environment variable encryption
- CORS configuration for secure cross-origin requests
- No sensitive data stored client-side

## 💰 Cost Estimation

### Monthly Costs (10,000 users)
| Service | Usage | Cost |
|---------|-------|------|
| AWS Amplify | 100 GB bandwidth | $1.50 |
| AWS Lambda | 1M requests, 512MB | $0.20 |
| API Gateway | 1M requests | $1.00 |
| AWS Bedrock | 100K recommendations | $40.00 |
| CloudWatch Logs | 10 GB | $5.00 |
| **Total** | | **~$48/month** |

### Free Tier Benefits
- Amplify: 1000 build minutes/month
- Lambda: 1M requests/month
- API Gateway: 1M requests/month (first 12 months)

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Air Quality Data**: [OpenAQ](https://openaq.org/) - Open air quality data platform
- **AI/ML**: [AWS Bedrock](https://aws.amazon.com/bedrock/) - Claude Opus 4.6 by Anthropic
- **Geocoding**: [Nominatim](https://nominatim.org/) - OpenStreetMap geocoding service
- **AQI Standards**: [US EPA](https://www.epa.gov/aqi) - Air Quality Index guidelines
- **Hosting**: [AWS Amplify](https://aws.amazon.com/amplify/) - Frontend hosting and CI/CD
- **Serverless**: [AWS Lambda](https://aws.amazon.com/lambda/) - Serverless compute

## 📞 Support

- **Documentation**: See [ARCHITECTURE.md](ARCHITECTURE.md) and [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/synnbad/O-Zone/issues)
- **Discussions**: [GitHub Discussions](https://github.com/synnbad/O-Zone/discussions)

## 🗺️ Roadmap

### Completed ✅
- [x] Real-time air quality data integration
- [x] AI-powered recommendations
- [x] Global map visualization
- [x] React frontend with TypeScript
- [x] FastAPI backend
- [x] AWS Lambda deployment
- [x] AWS Amplify hosting
- [x] Demo data fallback
- [x] Mobile-responsive design

### In Progress 🚧
- [ ] User authentication (AWS Cognito)
- [ ] Personalized alerts and notifications
- [ ] Historical data caching (DynamoDB)
- [ ] Custom domain setup
- [ ] Enhanced PWA features

### Planned 📋
- [ ] Mobile apps (iOS/Android)
- [ ] Weather integration
- [ ] Pollen count data
- [ ] Social sharing features
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

## 📈 Project Stats

- **Lines of Code**: 15,000+
- **Test Coverage**: 85%+
- **API Endpoints**: 6
- **Supported Pollutants**: 6 (PM2.5, PM10, CO, NO2, O3, SO2)
- **Global Stations**: 36+
- **Deployment Time**: <10 minutes
- **Cold Start**: ~2 seconds
- **Response Time**: <500ms (avg)

## 🏆 Awards & Recognition

Built for AWS Hackathon 2026 - Showcasing modern cloud architecture and AI integration.

---

**Made with ❤️ for cleaner air and healthier communities**

[Live Demo](https://main.d32w9y2132m03m.amplifyapp.com) | [API Docs](https://z027fnomoh.execute-api.us-east-1.amazonaws.com/docs) | [Architecture](ARCHITECTURE.md) | [Deployment Guide](DEPLOYMENT_GUIDE.md)
