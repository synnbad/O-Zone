# Amplify Environment Variables Configuration Guide

## Required Environment Variables

The O-Zone backend requires the following environment variables to be configured in the AWS Amplify Console:

**IMPORTANT**: Amplify does not allow environment variables starting with `AWS_*`. We use `OZONE_AWS_*` prefix instead.

| Variable Name | Description | Example Value |
|---------------|-------------|---------------|
| `OZONE_AWS_REGION` | AWS service region for Bedrock and other services | `us-east-1` |
| `OZONE_AWS_ACCESS_KEY_ID` | AWS access key for authentication | `AKIA...` |
| `OZONE_AWS_SECRET_ACCESS_KEY` | AWS secret key for authentication | `secret...` |
| `OZONE_AWS_SESSION_TOKEN` | AWS session token (for temporary credentials) | `IQoJb3JpZ2luX2VjEJ3...` |
| `BEDROCK_MODEL_ID` | ARN of the Bedrock model to use | `arn:aws:bedrock:us-east-1:559050222547:inference-profile/global.anthropic.claude-opus-4-6-v1` |
| `OPENAQ_API_KEY` | API key for OpenAQ air quality data | `0ff845...` |

## Configuration Steps

### Option 1: Using AWS Amplify Console (Recommended)

1. **Navigate to Amplify Console**
   - Go to https://console.aws.amazon.com/amplify/
   - Select your O-Zone application

2. **Access Environment Variables**
   - Click on "App settings" in the left sidebar
   - Click on "Environment variables"

3. **Add Each Variable**
   - Click "Add variable" button
   - Enter the variable name (e.g., `AWS_REGION`)
   - Enter the variable value
   - Click "Save"

4. **Repeat for All Variables**
   - Add all 5 required environment variables listed above
   - Ensure there are no typos in variable names

5. **Verify Configuration**
   - Review the list of environment variables
   - Ensure all 5 variables are present
   - Click "Save" to apply changes

### Option 2: Using AWS CLI

```bash
# Set your Amplify app ID
APP_ID="your-app-id"

# Add environment variables (note: use OZONE_AWS_* prefix for Amplify)
aws amplify update-app \
  --app-id $APP_ID \
  --environment-variables \
    OZONE_AWS_REGION=us-east-1 \
    OZONE_AWS_ACCESS_KEY_ID=your-access-key \
    OZONE_AWS_SECRET_ACCESS_KEY=your-secret-key \
    OZONE_AWS_SESSION_TOKEN=your-session-token \
    BEDROCK_MODEL_ID=arn:aws:bedrock:us-east-1:559050222547:inference-profile/global.anthropic.claude-opus-4-6-v1 \
    OPENAQ_API_KEY=your-openaq-key
```

## Verification

After configuring the environment variables:

1. **Trigger a New Build**
   - Push a commit to your repository, or
   - Click "Redeploy this version" in the Amplify Console

2. **Check Build Logs**
   - Monitor the build logs for the backend phase
   - Look for any warnings about missing environment variables

3. **Test the Backend**
   - Once deployed, test the health endpoint:
   ```bash
   curl https://your-app-id.amplifyapp.com/api/health
   ```
   - Should return: `{"status": "healthy", "service": "O-Zone API", "version": "1.0.0"}`

4. **Check Backend Logs**
   - If the backend logs warnings about missing variables, double-check the configuration
   - Ensure variable names match exactly (case-sensitive)

## Security Best Practices

- **Never commit credentials to Git**: Environment variables should only be set in Amplify Console
- **Use IAM roles when possible**: Consider using IAM roles instead of access keys for better security
- **Rotate credentials regularly**: Update AWS credentials periodically
- **Limit permissions**: Ensure the AWS credentials have only the necessary permissions for Bedrock and other services

## Troubleshooting

### Variables Not Available in Backend

**Symptom**: Backend logs show warnings about missing environment variables

**Solution**:
1. Verify variables are set in Amplify Console under "Environment variables"
2. Check for typos in variable names (they are case-sensitive)
3. Redeploy the application after adding variables
4. Check that variables are set at the app level, not branch level

### Backend Fails to Start

**Symptom**: Backend deployment fails or returns 502 errors

**Solution**:
1. Check build logs for Python dependency installation errors
2. Verify all required environment variables are set
3. Test the backend locally with the same environment variables
4. Check CloudWatch logs for detailed error messages

### CORS Errors in Frontend

**Symptom**: Frontend cannot connect to backend due to CORS errors

**Solution**:
1. Verify CORS middleware is configured in `src/api/main.py`
2. Check that `allow_origins` includes the Amplify frontend domain
3. Test API endpoints directly with curl to isolate CORS issues

## Next Steps

After configuring environment variables:
1. Proceed to Task 3: Verify FastAPI application Lambda compatibility
2. Test the backend locally before deploying
3. Monitor the first Amplify build with backend configuration
