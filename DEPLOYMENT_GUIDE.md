# O-Zone Hackathon Deployment Guide

## Quick Deployment to AWS Amplify

### Prerequisites
- AWS Account with Amplify access
- Git repository with code pushed
- AWS credentials configured

### Step 1: Create Amplify App

```bash
# Install AWS CLI if not already installed
# pip install awscli

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and Region (us-east-1)

# Create Amplify app
aws amplify create-app --name o-zone-hackathon --region us-east-1
```

### Step 2: Connect Git Repository

1. Go to AWS Amplify Console: https://console.aws.amazon.com/amplify/
2. Click "New app" → "Host web app"
3. Select your Git provider (GitHub, GitLab, etc.)
4. Authorize AWS Amplify to access your repository
5. Select the repository and branch (main)
6. Click "Next"

### Step 3: Configure Build Settings

1. Amplify will detect the `amplify.yml` file automatically
2. Click "Advanced settings"
3. Add environment variables:

```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-aws-access-key-id>
AWS_SECRET_ACCESS_KEY=<your-aws-secret-access-key>
AWS_SESSION_TOKEN=<your-aws-session-token>
BEDROCK_MODEL_ID=arn:aws:bedrock:us-east-1:559050222547:inference-profile/global.anthropic.claude-opus-4-6-v1
OPENAQ_API_KEY=<your-openaq-api-key>
```

4. Click "Next" → "Save and deploy"

### Step 4: Set Up Backend API (Lambda + API Gateway)

Since Amplify primarily hosts static sites, we need to deploy the backend separately:

#### Option A: AWS Lambda + API Gateway (Recommended for Hackathon)

1. **Package the backend:**
```bash
cd O-Zone
pip install -r requirements.txt -t package/
cp -r src package/
cp .env package/
cd package
zip -r ../function.zip .
cd ..
```

2. **Create Lambda function:**
```bash
aws lambda create-function \
  --function-name o-zone-api \
  --runtime python3.11 \
  --role arn:aws:iam::559050222547:role/lambda-execution-role \
  --handler src.api.main.handler \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 512 \
  --environment Variables="{AWS_REGION=us-east-1,AWS_ACCESS_KEY_ID=<your-key>,AWS_SECRET_ACCESS_KEY=<your-secret>,AWS_SESSION_TOKEN=<your-token>,BEDROCK_MODEL_ID=arn:aws:bedrock:us-east-1:559050222547:inference-profile/global.anthropic.claude-opus-4-6-v1,OPENAQ_API_KEY=<your-openaq-key>}"
```

3. **Create API Gateway:**
```bash
# Create REST API
aws apigateway create-rest-api --name o-zone-api --region us-east-1

# Get API ID from output, then create resources and methods
# This is complex - use AWS Console instead for hackathon speed
```

**Easier: Use AWS Console**
1. Go to Lambda Console
2. Create function "o-zone-api" with Python 3.11
3. Upload function.zip
4. Add API Gateway trigger
5. Configure CORS
6. Copy API Gateway URL

4. **Update Frontend Environment:**
```bash
# Update O-Zone UI/.env.production with API Gateway URL
VITE_API_URL=https://your-api-id.execute-api.us-east-1.amazonaws.com
```

5. **Redeploy Amplify app** (it will pick up the new environment variable)

#### Option B: Deploy Backend to EC2 (Alternative)

```bash
# Launch EC2 instance (t2.micro for free tier)
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Install dependencies
sudo yum update -y
sudo yum install python3-pip -y
sudo pip3 install uvicorn fastapi mangum python-dotenv boto3

# Copy code to instance
scp -i your-key.pem -r O-Zone ec2-user@your-instance-ip:~/

# Run server
cd O-Zone
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Update frontend to use EC2 public IP
VITE_API_URL=http://your-ec2-ip:8000
```

### Step 5: Test Deployment

1. Wait for Amplify build to complete (5-10 minutes)
2. Click on the Amplify app URL
3. Test features:
   - Location search
   - AQI display
   - Chat functionality
   - Recommendations
   - Map visualization

### Step 6: Share Demo URL

Your app will be available at:
```
https://main.your-app-id.amplifyapp.com
```

Share this URL with hackathon judges!

## Troubleshooting

### Build Fails
- Check Amplify build logs in console
- Verify `amplify.yml` is in repository root
- Ensure all dependencies are in `package.json` and `requirements.txt`

### API Not Working
- Check Lambda function logs in CloudWatch
- Verify environment variables are set correctly
- Test Lambda function directly in console
- Check API Gateway CORS configuration

### Frontend Can't Connect to Backend
- Verify `VITE_API_URL` is set correctly
- Check browser console for CORS errors
- Ensure API Gateway has CORS enabled
- Test API endpoints directly with curl

## Cost Estimate

For 3-day hackathon:
- Amplify Hosting: ~$0 (free tier)
- Lambda: ~$0-5 (free tier covers most usage)
- API Gateway: ~$0-3
- **Total: < $10**

## Cleanup After Hackathon

```bash
# Delete Amplify app
aws amplify delete-app --app-id your-app-id

# Delete Lambda function
aws lambda delete-function --function-name o-zone-api

# Delete API Gateway
aws apigateway delete-rest-api --rest-api-id your-api-id
```

## Quick Demo Script

1. **Show Dashboard**: "Here's the real-time air quality for San Francisco"
2. **Search Location**: "Let me check another city..." (search for "New York")
3. **View AQI Details**: "You can see the breakdown by pollutant"
4. **Chat with AI**: "Let's ask the AI assistant for recommendations"
5. **Activity Planning**: "Here's what it suggests for running today"
6. **Global Map**: "And here's air quality around the world"

Good luck with your hackathon! 🚀
