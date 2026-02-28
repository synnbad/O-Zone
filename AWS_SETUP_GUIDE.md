# AWS Setup Guide for O-Zone MVP

This guide will walk you through setting up AWS services for the O-Zone application.

## What You Need from AWS

### Required Service: Amazon Bedrock
- **Purpose**: Powers AI recommendations using Claude 3.5 Sonnet
- **Cost**: ~$0.004 per recommendation (pay-as-you-go)
- **Region**: us-east-1 (recommended) or other Bedrock-supported regions

### Required Credentials
1. AWS Access Key ID
2. AWS Secret Access Key
3. AWS Region

---

## Step-by-Step Setup

### Step 1: Enable Amazon Bedrock Model Access

1. **Log into AWS Console**
   - Go to https://console.aws.amazon.com/
   - Sign in with your AWS account

2. **Navigate to Amazon Bedrock**
   - Search for "Bedrock" in the top search bar
   - Click on "Amazon Bedrock"

3. **Request Model Access**
   - In the left sidebar, click **"Model access"**
   - Click **"Manage model access"** button (orange button, top right)
   
4. **Enable Claude 3.5 Sonnet**
   - Scroll down to find **"Anthropic"** section
   - Check the box next to **"Claude 3.5 Sonnet v2"**
   - Model ID should be: `anthropic.claude-3-5-sonnet-20241022-v2:0`
   - Click **"Request model access"** at the bottom
   
5. **Wait for Approval**
   - Status will show "In progress" initially
   - Usually takes 1-2 minutes
   - Refresh the page until status shows **"Access granted"** (green checkmark)
   - If it takes longer than 5 minutes, you may need to verify your AWS account

---

### Step 2: Create IAM User for the Application

1. **Navigate to IAM Service**
   - Search for "IAM" in the top search bar
   - Click on "IAM" (Identity and Access Management)

2. **Create New User**
   - Click **"Users"** in the left sidebar
   - Click **"Create user"** button (orange button)
   - User name: `ozone-app-user` (or any name you prefer)
   - Click **"Next"**

3. **Create Custom Policy**
   - Select **"Attach policies directly"**
   - Click **"Create policy"** (opens in new tab)
   
4. **Configure Policy (in new tab)**
   - Click on **"JSON"** tab
   - Replace the default JSON with:
   
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "BedrockInvokeModel",
               "Effect": "Allow",
               "Action": [
                   "bedrock:InvokeModel"
               ],
               "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
           }
       ]
   }
   ```
   
   - Click **"Next"**
   - Policy name: `OZoneBedrockAccess`
   - Description: `Allows O-Zone app to invoke Claude 3.5 Sonnet via Bedrock`
   - Click **"Create policy"**

5. **Attach Policy to User (return to first tab)**
   - Click the refresh icon next to "Create policy" button
   - Search for `OZoneBedrockAccess`
   - Check the box next to your new policy
   - Click **"Next"**
   - Review and click **"Create user"**

---

### Step 3: Generate Access Keys

1. **Open User Details**
   - Click on the newly created user `ozone-app-user`
   
2. **Create Access Key**
   - Click on **"Security credentials"** tab
   - Scroll down to **"Access keys"** section
   - Click **"Create access key"**
   
3. **Select Use Case**
   - Choose **"Application running outside AWS"**
   - Check the confirmation box at the bottom
   - Click **"Next"**
   
4. **Add Description (Optional)**
   - Description tag: `O-Zone MVP Application`
   - Click **"Create access key"**

5. **Save Your Credentials** ⚠️ IMPORTANT
   - You'll see two values:
     - **Access key ID**: Starts with `AKIA...`
     - **Secret access key**: Long random string (only shown once!)
   
   - **COPY BOTH VALUES IMMEDIATELY**
   - Click **"Download .csv file"** for backup
   - Store securely (you won't be able to see the secret key again)
   - Click **"Done"**

---

### Step 4: Configure O-Zone Application

1. **Open the `.env` file** in your O-Zone project folder

2. **Add your AWS credentials**:
   ```env
   # AWS Configuration (Required for AI recommendations)
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=AKIA...your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
   
   # OpenAQ API (Optional - free tier works without key)
   OPENAQ_API_KEY=
   ```

3. **Save the file**

---

## Verification

Test your AWS setup:

```bash
python -c "import boto3; client = boto3.client('bedrock-runtime', region_name='us-east-1'); print('✓ AWS credentials configured correctly')"
```

If successful, you should see: `✓ AWS credentials configured correctly`

---

## Region Selection

### Recommended Region: us-east-1 (N. Virginia)
- Most stable
- Lowest latency for most users
- All Bedrock features available

### Alternative Regions (if needed)
- `us-west-2` (Oregon)
- `eu-central-1` (Frankfurt)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)

**To change region:**
1. Verify Claude 3.5 Sonnet is available in your chosen region
2. Update `AWS_REGION` in `.env` file
3. Ensure model access is granted in that region

---

## Cost Breakdown

### Amazon Bedrock Pricing (Claude 3.5 Sonnet)

**Input tokens**: ~$3.00 per million tokens
**Output tokens**: ~$15.00 per million tokens

### O-Zone Usage Estimates

**Per recommendation**:
- Input: ~500 tokens (AQI data + user profile + prompt)
- Output: ~200 tokens (recommendation + precautions + time windows)
- **Cost per recommendation**: ~$0.004 (less than half a cent)

**Monthly estimates**:
- 100 recommendations: ~$0.40
- 500 recommendations: ~$2.00
- 1,000 recommendations: ~$4.00
- 10,000 recommendations: ~$40.00

### Free Tier
- AWS offers free tier credits for new accounts
- Check your AWS Free Tier dashboard for available credits

---

## Security Best Practices

### ✅ DO:
- Store credentials in `.env` file (never commit to git)
- Use IAM user with minimal permissions (only Bedrock access)
- Rotate access keys every 90 days
- Enable MFA on your AWS root account
- Monitor usage in AWS Cost Explorer

### ❌ DON'T:
- Share your access keys with anyone
- Commit `.env` file to version control
- Use root account credentials
- Give broader permissions than needed
- Hardcode credentials in source code

---

## Troubleshooting

### Error: "Could not connect to the endpoint URL"
**Solution**: Check your AWS_REGION in `.env` matches where you enabled Bedrock

### Error: "AccessDeniedException"
**Solution**: 
1. Verify model access is granted (Step 1)
2. Check IAM policy is attached to user (Step 2)
3. Ensure access keys are correct (Step 3)

### Error: "ValidationException: The provided model identifier is invalid"
**Solution**: Verify you enabled Claude 3.5 Sonnet v2 specifically (not v1)

### Error: "ThrottlingException"
**Solution**: You're making too many requests. Wait a moment and try again.

### Model access stuck on "In progress"
**Solution**: 
1. Wait 5 minutes and refresh
2. Check if your AWS account is verified (may need to add payment method)
3. Contact AWS support if it persists

---

## Monitoring Usage

### View Costs
1. Go to AWS Console
2. Search for "Cost Explorer"
3. Filter by service: "Amazon Bedrock"
4. View daily/monthly costs

### Set Budget Alerts
1. Go to AWS Billing Dashboard
2. Click "Budgets"
3. Create budget (e.g., $10/month)
4. Set email alerts at 80% and 100%

---

## Need Help?

- **AWS Documentation**: https://docs.aws.amazon.com/bedrock/
- **AWS Support**: https://console.aws.amazon.com/support/
- **O-Zone Issues**: Create an issue in the GitHub repository

---

## Quick Reference

**What you need in `.env`**:
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
```

**IAM Policy Name**: `OZoneBedrockAccess`

**Model ID**: `anthropic.claude-3-5-sonnet-20241022-v2:0`

**Estimated Cost**: ~$0.004 per recommendation

---

## Next Steps

Once AWS is configured:

1. Run the application:
   ```bash
   streamlit run src/app.py
   ```
   
   Or on Windows:
   ```bash
   run.bat
   ```

2. Test with a location (e.g., "San Francisco")

3. Verify AI recommendations are working

4. Monitor your AWS costs in the first few days

---

**Setup Complete!** 🎉

Your O-Zone application is now ready to provide AI-powered air quality recommendations.
