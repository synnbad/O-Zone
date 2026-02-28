# O-Zone MVP - Air Quality Decision Platform

AI-powered outdoor activity recommendations based on real-time air quality data.

## Features

- 🌍 Real-time air quality data from OpenAQ (global coverage)
- 📊 EPA-standard AQI calculations for 6 pollutants (PM2.5, PM10, CO, NO2, O3, SO2)
- 🤖 AI-powered personalized recommendations via Amazon Bedrock (Claude 3.5 Sonnet)
- 📈 Historical trend analysis (24-hour charts)
- 🏃 Activity-specific guidance (walking, running, cycling, etc.)
- 💊 Health sensitivity considerations (asthma, allergies, pregnancy, etc.)

## Quick Start

### Option 1: Test Without AWS (Demo Mode)

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

The app works immediately with rule-based recommendations! See [TEST_WITHOUT_AWS.md](TEST_WITHOUT_AWS.md) for details.

### Option 2: Full AI Mode (Requires AWS)

1. Install dependencies: `pip install -r requirements.txt`
2. Configure AWS credentials (see [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md))
3. Run: `streamlit run src/app.py`

---

## Prerequisites

- Python 3.10 or higher
- AWS Account with Bedrock access
- OpenAQ API access (free tier available)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd ozone-mvp
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your credentials:
   ```env
   # AWS Configuration (Required for AI recommendations)
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   
   # OpenAQ API (Optional - free tier works without key)
   OPENAQ_API_KEY=your_openaq_key_here
   ```

## AWS Setup for Bedrock

### Required AWS Services

1. **Amazon Bedrock** - For AI-powered recommendations using Claude 3.5 Sonnet

### Step-by-Step AWS Configuration

#### 1. Enable Amazon Bedrock Model Access

1. Log into AWS Console
2. Navigate to **Amazon Bedrock** service
3. Go to **Model access** in the left sidebar
4. Click **Manage model access**
5. Find **Anthropic** section
6. Enable **Claude 3.5 Sonnet v2** (model ID: `anthropic.claude-3-5-sonnet-20241022-v2:0`)
7. Click **Save changes**
8. Wait for status to change to "Access granted" (usually takes 1-2 minutes)

#### 2. Create IAM User for Application

1. Navigate to **IAM** service
2. Click **Users** → **Create user**
3. User name: `ozone-app-user`
4. Click **Next**
5. Select **Attach policies directly**
6. Click **Create policy** (opens new tab)
7. Use JSON editor and paste:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "bedrock:InvokeModel"
               ],
               "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
           }
       ]
   }
   ```
8. Name the policy: `OZoneBedrockAccess`
9. Click **Create policy**
10. Return to user creation tab, refresh policies, and select `OZoneBedrockAccess`
11. Click **Next** → **Create user**

#### 3. Generate Access Keys

1. Click on the newly created user `ozone-app-user`
2. Go to **Security credentials** tab
3. Scroll to **Access keys** section
4. Click **Create access key**
5. Select **Application running outside AWS**
6. Click **Next** → **Create access key**
7. **IMPORTANT**: Copy both:
   - Access key ID
   - Secret access key
8. Add these to your `.env` file

### AWS Region Selection

The application defaults to `us-east-1`. If you want to use a different region:

1. Verify Claude 3.5 Sonnet is available in your region
2. Update `AWS_REGION` in your `.env` file

Available regions for Bedrock (as of 2024):
- `us-east-1` (N. Virginia) - Recommended
- `us-west-2` (Oregon)
- `eu-central-1` (Frankfurt)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)

### Cost Considerations

**Amazon Bedrock Pricing** (Claude 3.5 Sonnet):
- Input: ~$3 per million tokens
- Output: ~$15 per million tokens

**Estimated costs for O-Zone**:
- Per recommendation: ~500 input tokens + ~200 output tokens
- Cost per recommendation: ~$0.004 (less than half a cent)
- 1000 recommendations: ~$4

**Free tier**: AWS offers free tier credits for new accounts.

## OpenAQ API Setup (Optional)

OpenAQ provides free access to air quality data:

1. Visit [OpenAQ API](https://openaq.org/)
2. Sign up for free API access (optional - works without key)
3. If you get an API key, add it to `.env`

**Note**: The free tier works without an API key, but having one provides higher rate limits.

## Running the Application

Start the Streamlit app:

```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. **Enter a location**: Type a city name (e.g., "San Francisco") or coordinates (e.g., "37.7749,-122.4194")
2. **View current AQI**: See overall air quality and individual pollutant levels
3. **Select your activity**: Choose what you plan to do outdoors
4. **Set health sensitivity**: Indicate any health concerns
5. **Get AI recommendation**: Receive personalized guidance from Claude

## Project Structure

```
ozone-mvp/
├── src/
│   ├── app.py              # Streamlit UI
│   ├── config.py           # Configuration and constants
│   ├── models.py           # Data models
│   ├── aqi_calculator.py   # AQI calculation logic
│   ├── data_fetcher.py     # OpenAQ API client
│   ├── bedrock_client.py   # Amazon Bedrock client
│   └── prompts.py          # AI prompt templates
├── tests/
│   ├── conftest.py         # Test fixtures
│   ├── unit/               # Unit tests
│   ├── property/           # Property-based tests
│   └── integration/        # Integration tests
├── .env.example            # Environment variables template
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Troubleshooting

### "Bedrock service unavailable"
- Verify AWS credentials in `.env`
- Check that Claude 3.5 Sonnet model access is enabled
- Verify IAM user has `bedrock:InvokeModel` permission
- Check AWS region supports Bedrock

### "Location not found"
- Try a major city name
- Verify coordinates format: `latitude,longitude`
- Check internet connection

### "No recent air quality data"
- Location may not have active monitoring stations
- Try a nearby major city
- Check OpenAQ website for station availability

## Development

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Air quality data: [OpenAQ](https://openaq.org/)
- AI recommendations: [Amazon Bedrock](https://aws.amazon.com/bedrock/)
- AQI standards: [US EPA](https://www.epa.gov/aqi)
