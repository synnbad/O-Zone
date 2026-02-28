# O-Zone Quick Start Guide

## Test Right Now (No Setup Required!)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run src/app.py
```

That's it! The app opens in your browser at `http://localhost:8501`

---

## What You Get Without AWS

✅ Real-time air quality data (global coverage)
✅ EPA-standard AQI calculations
✅ Current conditions display
✅ Historical trend charts
✅ **Rule-based recommendations** (smart, but not AI)

The app automatically uses demo mode when AWS is not configured.

---

## Try These Locations

**Good Air Quality:**
- San Francisco
- Seattle
- Portland

**Moderate Air Quality:**
- Los Angeles
- Phoenix

**Variable (Check Current Conditions):**
- Beijing
- Delhi
- London

**Or use coordinates:**
- `37.7749,-122.4194` (San Francisco)
- `39.9042,116.4074` (Beijing)

---

## Test Different Scenarios

1. **Low Intensity + No Sensitivity**
   - Activity: Walking
   - Sensitivity: None
   - See: Permissive recommendations

2. **High Intensity + Sensitive**
   - Activity: Jogging/Running
   - Sensitivity: Asthma/Respiratory
   - See: More cautious recommendations

3. **Poor Air Quality**
   - Try: Delhi or Beijing
   - Any activity
   - See: Protective recommendations

---

## Upgrade to AI Mode (Optional)

Want AI-powered recommendations with time predictions?

1. See [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md) (10 min setup)
2. Add credentials to `.env`
3. Restart app
4. AI mode activates automatically!

**Cost**: ~$0.004 per recommendation (less than half a cent)

---

## Documentation

- **This file**: Quick start (you are here)
- **TEST_WITHOUT_AWS.md**: Detailed demo mode guide
- **AWS_SETUP_GUIDE.md**: Enable AI recommendations
- **README.md**: Complete documentation
- **GETTING_STARTED.md**: Full setup guide

---

## Troubleshooting

**"Location not found"**
→ Try a major city or check coordinates format

**"No recent air quality data"**
→ Location may not have monitoring stations, try nearby city

**Import errors**
→ Run `pip install -r requirements.txt`

**App won't start**
→ Make sure you're in the project directory

---

## What's Next?

1. ✅ Test the app now (no setup needed!)
2. 📊 Try different locations and scenarios
3. 🤖 Enable AI mode when ready (optional)
4. 🌍 Enjoy air quality insights!

---

**Ready?** Run: `streamlit run src/app.py` or `run.bat` (Windows)
