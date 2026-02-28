# Testing O-Zone Without AWS

You can test the O-Zone application without configuring AWS credentials! The app will use rule-based recommendations instead of AI.

## Quick Start (No AWS Required)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application

**Windows:**
```bash
run.bat
```

**Mac/Linux:**
```bash
streamlit run src/app.py
```

The app will automatically detect that AWS is not configured and use fallback mode.

---

## What Works Without AWS

✅ **Full Functionality:**
- Real-time air quality data from OpenAQ
- EPA-standard AQI calculations
- Current conditions display
- Historical trend charts (24 hours)
- Activity and health sensitivity selection
- **Rule-based recommendations** (instead of AI)

❌ **Not Available:**
- AI-powered personalized recommendations via Claude
- Optimal time window predictions
- Advanced reasoning and context analysis

---

## Demo Mode Features

### Rule-Based Recommendations

The app provides intelligent recommendations based on:
- Current AQI level (0-500)
- Activity intensity (walking, running, cycling, etc.)
- Health sensitivity (none, allergies, asthma, etc.)
- EPA guidelines and best practices

### Example Recommendations

**AQI 50 (Good):**
- "Air quality is excellent. Perfect conditions for all outdoor activities."
- No precautions needed

**AQI 100 (Moderate):**
- "Air quality is acceptable. Most people can enjoy activities without concerns."
- Sensitive individuals should monitor symptoms

**AQI 150 (Unhealthy for Sensitive Groups):**
- "Consider reducing intensity or duration for high-intensity activities."
- Precautions for sensitive groups

**AQI 200+ (Unhealthy/Very Unhealthy):**
- "Outdoor activities should be avoided or significantly limited."
- Detailed precautions and safety measures

---

## Testing the Application

### 1. Start the App
```bash
streamlit run src/app.py
```

You'll see a notice: "Running in Demo Mode - AWS Bedrock not configured"

### 2. Try Different Locations

**Major Cities:**
- San Francisco
- Los Angeles
- New York
- Beijing
- London
- Delhi
- Tokyo

**Coordinates:**
- `37.7749,-122.4194` (San Francisco)
- `39.9042,116.4074` (Beijing)
- `51.5074,-0.1278` (London)

### 3. Test Different Scenarios

**Low AQI (Good Air Quality):**
- Try: San Francisco, Seattle, Portland
- Activity: Any
- Sensitivity: None
- Expected: "Safe" assessment, no precautions

**Moderate AQI:**
- Try: Los Angeles, Phoenix
- Activity: Jogging/Running
- Sensitivity: Asthma/Respiratory
- Expected: "Moderate Risk", some precautions

**High AQI (Poor Air Quality):**
- Try: Delhi, Beijing (depending on season)
- Activity: Sports Practice
- Sensitivity: Child/Elderly
- Expected: "Unsafe", detailed precautions

---

## Comparing Demo Mode vs AI Mode

| Feature | Demo Mode (No AWS) | AI Mode (With AWS) |
|---------|-------------------|-------------------|
| Real-time AQI data | ✅ Yes | ✅ Yes |
| Historical trends | ✅ Yes | ✅ Yes |
| Safety assessment | ✅ Rule-based | ✅ AI-powered |
| Recommendations | ✅ Template-based | ✅ Personalized |
| Precautions | ✅ Standard guidelines | ✅ Context-aware |
| Time windows | ❌ No | ✅ Yes (predicted) |
| Reasoning | ✅ Basic | ✅ Detailed |
| Cost | 🆓 Free | 💰 ~$0.004/request |

---

## When to Upgrade to AI Mode

Consider enabling AWS Bedrock if you want:

1. **Personalized Recommendations**
   - Context-aware advice based on your specific situation
   - Nuanced guidance considering multiple factors

2. **Time Window Predictions**
   - "Best time to go outside: 2-5 PM (AQI 50-75)"
   - Confidence levels for predictions

3. **Advanced Reasoning**
   - Detailed explanations of recommendations
   - Historical trend analysis
   - Pollutant-specific advice

4. **Production Use**
   - Professional applications
   - Research projects
   - Public-facing services

---

## Upgrading to AI Mode Later

When you're ready to enable AI recommendations:

1. Follow `AWS_SETUP_GUIDE.md` (10 minutes)
2. Add credentials to `.env` file
3. Restart the application
4. AI mode activates automatically!

No code changes needed - the app detects AWS credentials automatically.

---

## Troubleshooting Demo Mode

### "Location not found"
- Try a major city name
- Use coordinates format: `latitude,longitude`
- Check internet connection

### "No recent air quality data"
- Location may not have monitoring stations
- Try a nearby major city
- Check [OpenAQ website](https://openaq.org/) for coverage

### App won't start
```bash
pip install -r requirements.txt
```

### Import errors
Make sure you're in the project directory:
```bash
cd O-Zone
streamlit run src/app.py
```

---

## Example Test Session

```bash
# 1. Start the app
streamlit run src/app.py

# 2. In the browser:
#    - Enter: "San Francisco"
#    - Click: Search
#    - Select Activity: "Jogging/Running"
#    - Select Sensitivity: "None"
#    - View: Rule-based recommendation

# 3. Try different scenarios:
#    - Change activity to "Walking"
#    - Change sensitivity to "Asthma/Respiratory"
#    - See how recommendations adapt

# 4. Try different locations:
#    - "Beijing" (often higher AQI)
#    - "Delhi" (often very high AQI)
#    - Compare recommendations
```

---

## Demo Mode is Perfect For:

✅ **Testing the application**
✅ **Learning about air quality**
✅ **Evaluating the interface**
✅ **Development and debugging**
✅ **Personal use without AWS costs**
✅ **Educational purposes**
✅ **Proof of concept demonstrations**

---

## Next Steps

1. ✅ Test the app in demo mode
2. ✅ Try different locations and scenarios
3. ✅ Evaluate if you need AI features
4. 📚 Read `AWS_SETUP_GUIDE.md` when ready
5. 🚀 Enable AI mode for production use

---

**Ready to test?** Run `streamlit run src/app.py` or `run.bat` (Windows)

**No AWS account needed!** 🎉
