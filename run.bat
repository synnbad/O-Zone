@echo off
echo Starting O-Zone Air Quality Advisor...
echo.
echo The app will open in your browser at http://localhost:8501
echo.
echo Running in Demo Mode (no AWS required)
echo To enable AI recommendations, see AWS_SETUP_GUIDE.md
echo.
streamlit run src/app.py
