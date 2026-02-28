# Pre-Flight Check: React UI Backend Integration

## Date: 2026-02-28

## 1. React UI Structure ✅ CONFIRMED

### Pages Available:
- ✅ `/` - Login
- ✅ `/dashboard` - Dashboard (location selector, AQI display, quick actions)
- ✅ `/activity` - Activity recommendations
- ✅ `/globe` - Global map visualization
- ✅ `/trends` - Historical trends
- ✅ `/clean-room` - Clean room monitoring
- ✅ `/chat` - Chat interface
- ✅ `/safety` - Safety monitoring
- ✅ `/pollutants` - Pollutant details
- ✅ `/notifications` - Notifications

### Components Available:
- ✅ `AQICard.tsx` - AQI display component
- ✅ `AQIChart.tsx` - Chart visualization
- ✅ `HealthRecommendations.tsx` - Health recommendations
- ✅ `PollutantCard.tsx` - Pollutant breakdown

### Context:
- ✅ `UserContext.tsx` - User profile management (name, asthma, allergies, sensitivity level)

### Current State:
- **Mock data**: All pages currently use hardcoded data
- **No API integration**: No backend calls yet
- **Ready for integration**: Components are well-structured and ready to connect to APIs

### Key Findings:
1. Dashboard has location selector with hardcoded cities (San Francisco, LA, NY, Seattle)
2. Chat page has mock conversation with simulated bot responses
3. Activity page has activity selection (easy/hard) with mock recommendations
4. Globe page has global city list with mock AQI values
5. All pages use React Router for navigation
6. UserContext provides profile data (name, health conditions)

---

## 2. Chatbot Modules ✅ EASILY EXTRACTABLE

### Chatbot Architecture:
```
src/chatbot/
├── __init__.py                  # Public API exports
├── chatbot_interface.py         # CLI interface (can be adapted for REST)
├── conversation_manager.py      # State machine and conversation flow
├── session_manager.py           # In-memory session storage
├── backend_integration.py       # Integrates with data_fetcher, aqi_calculator, bedrock_client
├── response_generator.py        # Formats responses
├── bedrock_adapter.py           # AWS Bedrock integration
├── chatbot_config.py            # Configuration
├── user_profiler.py             # User profiling
└── logging_config.py            # Logging setup
```

### Key Functions for REST API:
```python
# From chatbot/__init__.py
from .session_manager import create_session, get_session, update_session
from .conversation_manager import process_user_input

# Usage in REST API:
# 1. POST /api/chat (no session_id) -> create_session() -> returns session_id
# 2. POST /api/chat (with session_id) -> process_user_input(session_id, message)
```

### Conversation States:
- GREETING
- LOCATION_COLLECTION
- ACTIVITY_SELECTION
- HEALTH_PROFILE_SELECTION
- RECOMMENDATION_GENERATION
- RECOMMENDATION_PRESENTATION
- FOLLOW_UP
- ERROR_RECOVERY
- GOODBYE

### Session Management:
- **In-memory storage**: Uses Python dict `_session_store`
- **TTL**: 30 minutes (configurable via `ChatbotConfig.SESSION_TTL_MINUTES`)
- **Session cleanup**: `cleanup_expired_sessions()` function available
- **Session data**: Stores location, activity, health profile, AQI, recommendations, conversation history

### Integration Points:
- Uses `data_fetcher.py` for location resolution and AQI data
- Uses `aqi_calculator.py` for AQI calculations
- Uses `bedrock_client.py` for AI recommendations
- Uses `demo_data.py` for fallback data

### Extraction Strategy:
✅ **EASY** - Chatbot is already modular and decoupled from Streamlit
- Create REST endpoint that calls `process_user_input(session_id, message)`
- Return JSON response with bot message and session_id
- No refactoring needed - just wrap existing functions

---

## 3. AWS Credentials & Bedrock Access ⚠️ NEEDS ATTENTION

### Provided Credentials:
```
AWS_DEFAULT_REGION: us-east-1
AWS_ACCESS_KEY_ID: <redacted>
AWS_SECRET_ACCESS_KEY: <redacted>
AWS_SESSION_TOKEN: <redacted>
```

### Bedrock Model:
```
Model ID: arn:aws:bedrock:us-east-1:559050222547:inference-profile/global.anthropic.claude-opus-4-6-v1
Model Name: Claude Opus 4.6 (via inference profile)
```

### Test Result:
❌ **FAILED** - "The security token included in the request is invalid"

### Possible Issues:
1. **Session token expired**: AWS session tokens typically expire after 1-12 hours
2. **Credentials not refreshed**: Need to regenerate credentials from AWS console
3. **IAM permissions**: May need to verify Bedrock access permissions

### Action Required:
🔴 **CRITICAL**: Need fresh AWS credentials before deployment

### Steps to Fix:
1. Log into AWS Console with hackathon account
2. Navigate to IAM or AWS CloudShell
3. Generate new temporary credentials:
   ```bash
   aws sts get-session-token --duration-seconds 43200  # 12 hours
   ```
4. Or use AWS SSO/IAM Identity Center for longer-lived credentials
5. Update `.env` file with new credentials

### Alternative for Demo:
- Use demo mode (rule-based recommendations) if Bedrock unavailable
- Existing `demo_data.py` provides fallback for OpenAQ API
- Can implement rule-based chatbot responses as fallback

---

## 4. Implementation Plan Adjustments

### Based on Findings:

#### ✅ No Changes Needed:
- React UI structure matches plan expectations
- Chatbot extraction is straightforward
- All existing Python modules are ready to use

#### ⚠️ Adjustments Required:

1. **AWS Credentials**:
   - Add task: "Refresh AWS credentials before deployment"
   - Add fallback: "Implement demo mode for chatbot if Bedrock unavailable"

2. **React UI Pages**:
   - Confirmed all planned pages exist
   - Add: CleanRoom page (bonus feature not in original plan)
   - Add: Login page (can skip for hackathon demo)

3. **Chatbot API Endpoint**:
   - Simpler than expected - just wrap `process_user_input()`
   - No refactoring needed
   - Session management already implemented

#### 📋 Updated Priority:
1. **URGENT**: Get fresh AWS credentials
2. Backend API extraction (Tasks 1-6)
3. Frontend API integration (Tasks 8-10)
4. Amplify deployment (Tasks 12-13)
5. Validation (Tasks 14-15)

---

## 5. Risk Assessment

### 🟢 Low Risk:
- React UI integration (well-structured, ready for APIs)
- Chatbot extraction (already modular)
- Backend API creation (reusing existing modules)
- Demo data fallback (already implemented)

### 🟡 Medium Risk:
- Amplify deployment (first time setup, may have learning curve)
- API Gateway configuration (manual setup in console)
- CORS configuration (common deployment issue)

### 🔴 High Risk:
- **AWS credentials expired** - BLOCKS deployment
- **Bedrock access** - May need IAM policy updates
- **Session token refresh** - Need mechanism for long-running demo

---

## 6. Recommendations

### Before Starting Implementation:

1. **Get Fresh AWS Credentials** (CRITICAL):
   - Contact hackathon organizers or AWS account admin
   - Request credentials with 12-hour+ validity
   - Verify Bedrock access with test script

2. **Test Bedrock Access**:
   ```bash
   python test_bedrock.py
   ```
   Should see: "✅ Bedrock access verified!"

3. **Set Up Environment Files**:
   ```bash
   # O-Zone/.env
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=<new_key>
   AWS_SECRET_ACCESS_KEY=<new_secret>
   AWS_SESSION_TOKEN=<new_token>
   
   # O-Zone UI/.env
   VITE_API_URL=http://localhost:8000
   ```

4. **Install Dependencies**:
   ```bash
   # Backend
   cd O-Zone
   pip install fastapi mangum uvicorn boto3
   
   # Frontend
   cd "O-Zone UI"
   npm install axios
   ```

### During Implementation:

1. **Start with Backend** (Tasks 1-6):
   - FastAPI setup is quick
   - Test locally before deploying
   - Verify fallback data works

2. **Test Incrementally**:
   - Run checkpoint tests (Tasks 7, 11, 15)
   - Don't skip validation steps

3. **Have Fallback Plan**:
   - If Bedrock fails, use rule-based recommendations
   - If OpenAQ fails, use demo data
   - If Amplify is complex, consider EC2 or App Runner

---

## 7. Go/No-Go Decision

### ✅ GO - Proceed with Implementation:
- React UI is ready
- Chatbot is easily extractable
- Existing modules are solid
- Demo data fallback exists

### ⚠️ CONDITIONAL - Fix AWS Credentials First:
- **MUST** get fresh credentials before deployment
- **SHOULD** verify Bedrock access
- **CAN** proceed with local development using demo mode

### 🔴 NO-GO Conditions:
- None identified (all blockers are fixable)

---

## Next Steps

1. **Immediate**: Get fresh AWS credentials from hackathon organizers
2. **Then**: Run `test_bedrock.py` to verify access
3. **Then**: Start Task 1 (FastAPI backend setup)
4. **Monitor**: AWS session token expiry during development

---

## Summary

✅ **React UI**: Ready for integration
✅ **Chatbot**: Easily extractable
⚠️ **AWS Credentials**: Need refresh (CRITICAL)
✅ **Implementation Plan**: Solid and achievable

**Estimated Time to First Working Demo**: 4-6 hours (after AWS credentials fixed)
