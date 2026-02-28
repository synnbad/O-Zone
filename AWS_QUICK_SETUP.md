# AWS Quick Setup for O-Zone

## Simplified Setup Process (Post-2024 AWS Updates)

AWS has simplified Bedrock access! Models are now automatically enabled when first invoked.

---

## Step 1: Get Your AWS Credentials

### Option A: Use Existing Credentials
If you already have AWS access keys, skip to Step 2.

### Option B: Create New IAM User (Recommended)

1. **Go to IAM Console**
   - Open: https://console.aws.amazon.com/iam/
   - Click "Users" → "Create user"

2. **Create User**
   - User name: `ozone-bedrock-user`
   - Click "Next"

3. **Set Permissions**
   - Select "Attach policies directly"
   - Click "Create policy" (opens new tab)
   
4. **Create Policy (in new tab)**
   - Click "JSON" tab
   - Paste this policy:
   
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "BedrockInvokeModel",
               "Effect": "Allow",
               "Action": [
                   "bedrock:InvokeModel",
                   "bedrock:InvokeModelWithResponseStream"
               ],
               "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-sonnet-*"
           }
       ]
   }
   ```
   
   - Click "Next"
   - Policy name: `OZoneBedrockInvokeOnly`
   - Click "Create policy"

5. **Attach Policy to User**
   - Return to user creation tab
   - Refresh policies
   - Search for `OZoneBedrockInvokeOnly`
   - Check the box
   - Click "Next" → "Create user"

6. **Create Access Keys**
   - Click on the new user
   - Go to "Security credentials" tab
   - Click "Create access key"
   - Select "Application running outside AWS"
   - Check confirmation box
   - Click "Next" → "Create access key"
   
7. **Save Your Credentials** ⚠️
   - Copy **Access key ID** (starts with AKIA...)
   - Copy **Secret access key** (long random string)
   - Download CSV file as backup
   - **You won't see the secret key again!**

---

## Step 2: Configure O-Zone

Edit the `.env` file in your project root:

```env
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

# OpenAQ API (Optional)
OPENAQ_API_KEY=
```

---

## Step 3: Test the Connection

Run this command to verify your AWS credentials:

```bash
python -c "import boto3; client = boto3.client('bedrock-runtime', region_name='us-east-1'); print('✓ AWS credentials working!')"
```

If successful, you'll see: `✓ AWS credentials working!`

---

## Step 4: Run the App

```bash
streamlit run src/app.py
```

The app will automatically detect AWS credentials and enable AI recommendations!

---

## Troubleshooting

### "NoCredentialsError"
→ Check that `.env` file has correct AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

### "AccessDeniedException"
→ Verify IAM policy is attached to your user

### "ValidationException: The provided model identifier is invalid"
→ Make sure you're using Claude 3.5 Sonnet (model ID in config.py is correct)

### First-time Anthropic users
→ You may need to submit use case details on first invocation
→ Follow the prompts in AWS Console if this happens

---

## Cost Monitoring

### View Costs
1. AWS Console → Cost Explorer
2. Filter by "Amazon Bedrock"
3. View daily/monthly usage

### Set Budget Alert
1. AWS Billing Dashboard → Budgets
2. Create budget (e.g., $10/month)
3. Set email alerts at 80% and 100%

**Typical costs**: 
- Per recommendation: ~$0.004
- 100 recommendations: ~$0.40
- 1,000 recommendations: ~$4.00

---

## Security Best Practices

✅ **DO:**
- Store credentials in `.env` file only
- Use IAM user with minimal permissions
- Rotate access keys every 90 days
- Enable MFA on AWS root account
- Monitor usage regularly

❌ **DON'T:**
- Commit `.env` to version control
- Share access keys
- Use root account credentials
- Give broader permissions than needed

---

## Next Steps

1. ✅ Create IAM user with Bedrock permissions
2. ✅ Generate access keys
3. ✅ Add credentials to `.env` file
4. ✅ Test connection
5. ✅ Run the app
6. 🎉 Enjoy AI-powered recommendations!

---

**Need help?** The AWS documentation MCP server is configured and ready to assist with any AWS-specific questions.
