# Amplify Backend Deployment Checklist

## Pre-Deployment Steps

### 1. Review Changes
- [x] amplify.yml updated with backend build configuration
- [x] Environment variable handling enhanced in src/config.py
- [x] Error handling improved in data_fetcher.py
- [x] Request logging added to src/api/main.py
- [x] CORS configuration verified
- [x] Health check endpoint verified

### 2. Local Testing
Before deploying to Amplify, test the backend locally:

```bash
# Navigate to project directory
cd O-Zone

# Test FastAPI import
python -c "from src.api.main import app, handler; print('✓ Backend imports successfully')"

# Start local server (optional)
python -m uvicorn src.api.main:app --reload

# Test health endpoint (in another terminal)
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "service": "O-Zone API"
}
```

## Deployment Steps

### 3. Configure Environment Variables in Amplify Console

**CRITICAL**: Before pushing code, configure these environment variables in Amplify Console:

1. Go to https://console.aws.amazon.com/amplify/
2. Select your O-Zone application
3. Click "App settings" > "Environment variables"
4. Add the following variables:

| Variable Name | Value | Notes |
|---------------|-------|-------|
| `AWS_REGION` | `us-east-1` | AWS service region |
| `AWS_ACCESS_KEY_ID` | `<your-key>` | From your AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | `<your-secret>` | From your AWS credentials |
| `AWS_SESSION_TOKEN` | `<your-token>` | Optional, for temporary credentials |
| `BEDROCK_MODEL_ID` | `arn:aws:bedrock:us-east-1:559050222547:inference-profile/global.anthropic.claude-opus-4-6-v1` | Claude Opus 4.6 model |
| `OPENAQ_API_KEY` | `<your-key>` | From OpenAQ dashboard |

5. Click "Save"

### 4. Commit and Push Changes

```bash
# Check git status
git status

# Add all changes
git add amplify.yml src/config.py src/data_fetcher.py src/api/main.py

# Commit with descriptive message
git commit -m "feat: Add Amplify backend deployment configuration

- Update amplify.yml with backend build phase
- Enhance environment variable handling with logging
- Improve error handling for external API calls
- Add request logging middleware
- Configure backend deployment artifacts"

# Push to trigger Amplify build
git push origin main
```

### 5. Monitor Amplify Build

1. Go to Amplify Console: https://console.aws.amazon.com/amplify/
2. Select your O-Zone application
3. Click on the latest build
4. Monitor build logs for:
   - Backend preBuild phase (pip install)
   - Backend build phase
   - Frontend preBuild phase (npm ci)
   - Frontend build phase (npm run build)
   - Deployment phase

**Expected Build Time**: 5-10 minutes

### 6. Verify Backend Deployment

Once the build completes:

```bash
# Test health endpoint (replace with your Amplify URL)
curl https://your-app-id.amplifyapp.com/api/health

# Expected response:
# {"status":"healthy","timestamp":"...","version":"1.0.0","service":"O-Zone API"}
```

### 7. Test API Endpoints

```bash
# Set your Amplify URL
AMPLIFY_URL="https://your-app-id.amplifyapp.com"

# Test health endpoint
curl $AMPLIFY_URL/api/health

# Test locations search
curl "$AMPLIFY_URL/api/locations/search?q=San+Francisco"

# Test chat endpoint
curl -X POST $AMPLIFY_URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Is it safe to go running today?","session_id":"test-123"}'
```

### 8. Verify Frontend Integration

1. Open your Amplify frontend URL in a browser
2. Open browser DevTools (F12) > Network tab
3. Test features that call the backend:
   - Location search
   - AQI display
   - Chat functionality
   - Activity recommendations
4. Check for:
   - Successful API calls (200 status)
   - No CORS errors
   - Proper response data

## Troubleshooting

### Build Fails - Backend Phase

**Symptom**: Build fails during "pip install" step

**Solutions**:
1. Check requirements.txt for invalid package names
2. Verify Python version compatibility (3.11+)
3. Check build logs for specific package errors
4. Try building locally first: `pip install -r requirements.txt`

### Build Fails - Missing Dependencies

**Symptom**: Build fails with "ModuleNotFoundError"

**Solutions**:
1. Ensure all dependencies are in requirements.txt
2. Check that src/ directory is being copied correctly
3. Verify amplify.yml syntax is correct

### Backend Returns 502 Error

**Symptom**: API endpoints return 502 Bad Gateway

**Solutions**:
1. Check CloudWatch logs for Lambda errors
2. Verify environment variables are set in Amplify Console
3. Test Mangum handler locally
4. Check that handler is exported in src/api/main.py

### Backend Returns 504 Timeout

**Symptom**: API endpoints timeout after 30 seconds

**Solutions**:
1. Check external API calls (OpenAQ, Bedrock) are responding
2. Verify AWS credentials are valid
3. Check CloudWatch logs for slow operations
4. Consider increasing Lambda timeout (if using Lambda)

### CORS Errors in Browser

**Symptom**: Frontend shows CORS errors in console

**Solutions**:
1. Verify CORS middleware is configured in src/api/main.py
2. Check that allow_origins includes "*" or your Amplify domain
3. Test API directly with curl to isolate CORS issue
4. Check that preflight OPTIONS requests return 200

### Environment Variables Not Available

**Symptom**: Backend logs show warnings about missing variables

**Solutions**:
1. Verify variables are set in Amplify Console
2. Check variable names match exactly (case-sensitive)
3. Redeploy after adding variables
4. Check that variables are at app level, not branch level

## Post-Deployment Verification

### Checklist

- [ ] Build completed successfully
- [ ] Backend health endpoint returns 200
- [ ] Frontend loads without errors
- [ ] Location search works
- [ ] AQI data displays correctly
- [ ] Chat functionality works
- [ ] Activity recommendations work
- [ ] No CORS errors in browser console
- [ ] API response times are acceptable (<5s)
- [ ] CloudWatch logs show no errors

### Performance Checks

```bash
# Test response times
time curl https://your-app-id.amplifyapp.com/api/health
time curl "https://your-app-id.amplifyapp.com/api/locations/search?q=San+Francisco"
```

Expected response times:
- Health endpoint: <1 second
- Location search: <3 seconds
- Chat endpoint: <10 seconds

## Rollback Procedure

If deployment fails or causes issues:

1. **Revert Git Commit**:
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **Or Redeploy Previous Version**:
   - Go to Amplify Console
   - Click on a previous successful build
   - Click "Redeploy this version"

3. **Or Disable Backend**:
   - Edit amplify.yml
   - Remove backend section
   - Commit and push

## Next Steps

After successful deployment:

1. Update frontend .env.production with Amplify API URL
2. Test all features end-to-end
3. Monitor CloudWatch logs for errors
4. Set up CloudWatch alarms for errors/timeouts
5. Document the deployed API URL for team
6. Update DEPLOYMENT_GUIDE.md with Amplify-specific instructions

## Support Resources

- Amplify Documentation: https://docs.aws.amazon.com/amplify/
- FastAPI Documentation: https://fastapi.tiangolo.com/
- Mangum Documentation: https://mangum.io/
- CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/

## Success Criteria

Deployment is successful when:
- ✅ Amplify build completes without errors
- ✅ Backend health endpoint returns 200
- ✅ All API endpoints are accessible
- ✅ Frontend can communicate with backend
- ✅ No CORS errors
- ✅ Response times meet requirements
- ✅ CloudWatch logs show no critical errors
