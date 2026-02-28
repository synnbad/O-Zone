# AWS Hackathon Setup Guide

## Quick Setup for Provisioned Hackathon Accounts

If you've been provided AWS credentials for a hackathon, follow these simplified steps:

---

## What You Need

Your hackathon organizers should have provided:
1. ✅ AWS Access Key ID
2. ✅ AWS Secret Access Key
3. ✅ AWS Region (usually `us-east-1`)
4. ✅ (Possibly) Bedrock model access already enabled

---

## Step 1: Add Credentials to .env File

Open the `.env` file in your project root and add your credentials:

```env
# AWS Configuration (from hackathon organizers)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# OpenAQ API (Optional)
OPENAQ_API_KEY=
```

**Important**: Replace the placeholder values with your actual credentials.

---

## Step 2: Verify Credentials

Test if your credentials work:

```bash
python -c "import boto3; client = boto3.client('bedrock-runtime', region_name='us-east-1'); print('✓ AWS credentials working!')"
```

If you see `✓ AWS credentials working!`, you're good to go!

---

## Step 3: Check Bedrock Model Access

Hackathon accounts usually have Bedrock pre-configured. Let's verify:

```bash
python -c "import boto3; client = boto3.client('bedrock', region_name='us-east-1'); response = client.list_foundation_models(); print(f'✓ Found {len(response[\"modelSummaries\"])} models available')"
```

---

## Step 4: Test the Application

Run the app:

```bash
streamlit run src/app.py
```

Or on Windows:
```bash
run.bat
```

The app should now show:
- ✅ "AI-powered recommendations via Claude 3.5 Sonnet" (instead of "Rule-based")
- ✅ Time window predictions
- ✅ Advanced reasoning

---

## Common Hackathon Account Scenarios

### Scenario 1: Credentials Provided Directly
- You received: Access Key ID + Secret Access Key
- Action: Add to `.env` file (Step 1)
- Region: Usually `us-east-1`

### Scenario 2: AWS Console Access
- You have: Console login (username/password)
- Action: Create access keys yourself
  1. Log into AWS Console
  2. Go to IAM → Users → Your username
  3. Security credentials tab
  4. Create access key → "Application running outside AWS"
  5. Copy keys to `.env` file

### Scenario 3: Temporary Credentials (AWS Workshop Studio)
- You have: Temporary session credentials
- Action: These expire after a few hours
- Note: You may need to refresh them periodically

### Scenario 4: IAM Role (EC2/Cloud9)
- You're running on: AWS EC2 or Cloud9
- Action: No `.env` needed! Credentials are automatic
- Just run: `streamlit run src/app.py`

---

## Troubleshooting

### Error: "AccessDeniedException"

**Cause**: Your account doesn't have Bedrock permissions

**Solution**: Ask hackathon organizers to enable Bedrock access for your account

### Error: "ValidationException: The provided model identifier is invalid"

**Cause**: Claude 3.5 Sonnet not available in your region

**Solution**: Try changing region in `.env`:
```env
AWS_REGION=us-west-2
```

### Error: "ExpiredToken"

**Cause**: Temporary credentials expired (common in workshops)

**Solution**: Get fresh credentials from hackathon dashboard

### Error: "ThrottlingException"

**Cause**: Too many requests (rate limit)

**Solution**: Wait 30 seconds and try again

---

## Testing Your Setup

### Test 1: Basic Credentials
```bash
python -c "import boto3; boto3.client('sts').get_caller_identity(); print('✓ Credentials valid')"
```

### Test 2: Bedrock Access
```bash
python -c "from src.bedrock_client import _call_bedrock; print('Testing...'); result = _call_bedrock('Say hello in 5 words'); print(f'✓ Bedrock working: {result[:50]}...')"
```

### Test 3: Full Flow
```bash
python -c "from src.data_fetcher import get_location, get_current_measurements; from src.aqi_calculator import calculate_overall_aqi; from src.bedrock_client import get_recommendation; loc = get_location('San Francisco'); measurements = get_current_measurements(loc); aqi = calculate_overall_aqi(measurements); rec = get_recommendation(aqi, 'Walking', 'None'); print(f'✓ Full flow working! Safety: {rec.safety_assessment}')"
```

---

## What's Different from Regular AWS Setup?

| Step | Regular AWS | Hackathon AWS |
|------|-------------|---------------|
| Create account | ✅ Required | ❌ Already done |
| Enable Bedrock | ✅ Required | ✅ Usually pre-enabled |
| Create IAM user | ✅ Required | ❌ Already done |
| Create access keys | ✅ Required | ✅ Provided or easy to create |
| Set up billing | ✅ Required | ❌ Handled by organizers |
| Cost monitoring | ✅ Your responsibility | ✅ Organizers handle it |

---

## Hackathon Best Practices

### ✅ DO:
- Test your credentials immediately
- Save your credentials securely
- Monitor your usage (if dashboard provided)
- Ask organizers if something doesn't work
- Use the provided region

### ❌ DON'T:
- Share your credentials with others
- Commit `.env` to git
- Try to create new AWS resources outside the scope
- Exceed rate limits (be reasonable with requests)
- Use credentials after hackathon ends

---

## Quick Reference

**Add credentials to `.env`:**
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

**Run the app:**
```bash
streamlit run src/app.py
```

**Test a city:**
- Enter: "San Francisco"
- Activity: "Walking"
- Sensitivity: "None"
- See AI-powered recommendation!

---

## Need Help?

1. **Credentials not working?** → Ask hackathon organizers
2. **Bedrock access denied?** → Request Bedrock permissions
3. **App errors?** → Check `AWS_SETUP_GUIDE.md` for detailed troubleshooting
4. **General questions?** → See `README.md`

---

## Next Steps

1. ✅ Add credentials to `.env`
2. ✅ Test credentials (Step 2)
3. ✅ Run the app
4. ✅ Try different cities and scenarios
5. 🎉 Build your hackathon project!

---

**Ready?** Add your credentials to `.env` and run `streamlit run src/app.py`!
