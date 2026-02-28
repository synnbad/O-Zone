# Getting Started with O-Zone MVP

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure AWS Credentials

Edit the `.env` file and add your AWS credentials:

```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
```

**Don't have AWS credentials yet?** See [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md) for detailed instructions.

### 3. Run the Application

**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
streamlit run src/app.py
```

The app will open in your browser at `http://localhost:8501`

### 4. Try It Out

1. Enter a city name (e.g., "Los Angeles", "Beijing", "London")
2. Select your planned activity
3. Set your health sensitivity
4. Get AI-powered recommendations!

---

## What You Need from AWS

### Required: Amazon Bedrock Access

You need:
1. ✅ AWS Account (free to create)
2. ✅ Amazon Bedrock model access (Claude 3.5 Sonnet)
3. ✅ IAM user with Bedrock permissions
4. ✅ Access Key ID and Secret Access Key

**Cost**: ~$0.004 per recommendation (less than half a cent)

**Setup Time**: ~10 minutes

**Detailed Guide**: See [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md)

---

## AWS Setup Summary

### Step 1: Enable Bedrock Model Access
1. Go to AWS Console → Amazon Bedrock
2. Click "Model access" → "Manage model access"
3. Enable "Claude 3.5 Sonnet v2" (Anthropic)
4. Wait for "Access granted" status

### Step 2: Create IAM User
1. Go to IAM → Users → Create user
2. Name: `ozone-app-user`
3. Create policy with this JSON:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["bedrock:InvokeModel"],
            "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
        }
    ]
}
```
4. Attach policy to user

### Step 3: Generate Access Keys
1. Click on user → Security credentials
2. Create access key → "Application running outside AWS"
3. Copy Access Key ID and Secret Access Key
4. Add to `.env` file

**Full instructions**: [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md)

---

## Features

✅ **Real-time Air Quality Data**
- Global coverage via OpenAQ
- 6 pollutants: PM2.5, PM10, CO, NO2, O3, SO2
- EPA-standard AQI calculations

✅ **AI-Powered Recommendations**
- Personalized guidance via Claude 3.5 Sonnet
- Activity-specific advice
- Health sensitivity considerations
- Optimal time window predictions

✅ **Historical Analysis**
- 24-hour trend charts
- Pollutant tracking
- Pattern analysis

---

## Project Structure

```
O-Zone/
├── src/
│   ├── app.py              # Streamlit UI (main application)
│   ├── config.py           # Configuration & EPA AQI tables
│   ├── models.py           # Data models
│   ├── aqi_calculator.py   # AQI calculation logic
│   ├── data_fetcher.py     # OpenAQ API client
│   ├── bedrock_client.py   # Amazon Bedrock AI client
│   └── prompts.py          # AI prompt templates
├── tests/
│   └── conftest.py         # Test fixtures
├── .env                    # Your AWS credentials (DO NOT COMMIT)
├── .env.example            # Template for .env
├── requirements.txt        # Python dependencies
├── README.md              # Full documentation
├── AWS_SETUP_GUIDE.md     # Detailed AWS setup
└── GETTING_STARTED.md     # This file
```

---

## Troubleshooting

### "Bedrock service unavailable"
- Check AWS credentials in `.env`
- Verify Claude 3.5 Sonnet model access is enabled
- Confirm IAM user has correct permissions

### "Location not found"
- Try a major city name
- Use coordinates format: `latitude,longitude`
- Example: `37.7749,-122.4194` for San Francisco

### "No recent air quality data"
- Location may not have active monitoring stations
- Try a nearby major city
- Check [OpenAQ website](https://openaq.org/) for coverage

### Import errors
```bash
pip install -r requirements.txt
```

---

## Cost Monitoring

### View Your AWS Costs
1. AWS Console → Cost Explorer
2. Filter by "Amazon Bedrock"
3. View daily/monthly usage

### Set Budget Alerts
1. AWS Billing Dashboard → Budgets
2. Create budget (e.g., $10/month)
3. Set email alerts

**Typical usage**: 100 recommendations = ~$0.40

---

## Example Usage

### Search by City
```
Enter: San Francisco
Result: Current AQI, pollutant breakdown, AI recommendations
```

### Search by Coordinates
```
Enter: 37.7749,-122.4194
Result: Air quality for that exact location
```

### Activity Examples
- Walking (low intensity)
- Jogging/Running (high intensity)
- Cycling (moderate intensity)
- Outdoor Study/Work (stationary)
- Sports Practice (high intensity)
- Child Outdoor Play (sensitive group)

### Health Sensitivity
- None (general population)
- Allergies (pollen/air quality sensitive)
- Asthma/Respiratory (breathing conditions)
- Child/Elderly (vulnerable groups)
- Pregnant (extra precautions)

---

## Development

### Run Tests
```bash
pytest tests/
```

### Run with Coverage
```bash
pytest --cov=src tests/
```

### Code Structure
- **Models**: Data structures (Location, Measurement, AQI, etc.)
- **Calculator**: EPA AQI algorithm implementation
- **Fetcher**: OpenAQ API integration with caching
- **Bedrock**: AI recommendation generation
- **App**: Streamlit UI with session state management

---

## Security Notes

⚠️ **IMPORTANT**:
- Never commit `.env` file to git
- Keep AWS credentials secure
- Rotate access keys every 90 days
- Use minimal IAM permissions
- Monitor AWS costs regularly

✅ The `.gitignore` file already excludes `.env`

---

## Support

- **Documentation**: See [README.md](README.md)
- **AWS Setup**: See [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md)
- **Issues**: Create GitHub issue
- **AWS Support**: https://console.aws.amazon.com/support/

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure AWS (see AWS_SETUP_GUIDE.md)
3. ✅ Run the application
4. ✅ Test with your location
5. ✅ Monitor AWS costs
6. 🎉 Enjoy AI-powered air quality insights!

---

**Ready to start?** Run `streamlit run src/app.py` or `run.bat` (Windows)
