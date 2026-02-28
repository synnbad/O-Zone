"""
O-Zone MVP - Streamlit Application

Air quality decision platform with AI-powered recommendations.
"""

import streamlit as st
from datetime import datetime, UTC
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config import Config
from src.data_fetcher import get_location, get_current_measurements, get_historical_measurements
from src.aqi_calculator import calculate_overall_aqi, get_aqi_category
from src.bedrock_client import get_recommendation
from src.responsive_styles import inject_responsive_styles
from src.pwa_config import setup_pwa_files


# Page configuration
st.set_page_config(
    page_title="O-Zone - Air Quality Advisor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'location' not in st.session_state:
    st.session_state.location = None
if 'current_aqi' not in st.session_state:
    st.session_state.current_aqi = None
if 'activity' not in st.session_state:
    st.session_state.activity = "Walking"
if 'health_sensitivity' not in st.session_state:
    st.session_state.health_sensitivity = "None"
if 'recommendation' not in st.session_state:
    st.session_state.recommendation = None
if 'historical_data' not in st.session_state:
    st.session_state.historical_data = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "text_input"  # "text_input" or "globe_view"
if 'globe_state' not in st.session_state:
    from src.models import GlobeState
    st.session_state.globe_state = GlobeState(
        center_lat=0.0, 
        center_lon=0.0, 
        zoom_level=2, 
        rotation=0.0, 
        selected_station=None
    )
if 'visible_stations' not in st.session_state:
    st.session_state.visible_stations = []


def main():
    """Main application entry point."""
    # Inject responsive CSS styles for mobile, tablet, and desktop
    try:
        inject_responsive_styles()
    except Exception as e:
        st.warning("⚠️ Responsive styles could not be loaded. Some features may not work on mobile.")
        import logging
        logging.error(f"CSS injection failed: {e}")
    
    # Setup PWA files (manifest.json and service worker)
    try:
        setup_pwa_files()
    except Exception as e:
        st.info("ℹ️ App installation feature is currently unavailable.")
        import logging
        logging.error(f"PWA setup failed: {e}")
    
    # Header
    st.title("🌍 O-Zone Air Quality Advisor")
    st.markdown("*AI-powered outdoor activity recommendations based on real-time air quality*")
    
    # Check AWS configuration
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
        st.info(
            "ℹ️ **Running in Demo Mode** - AWS Bedrock not configured. "
            "Using rule-based recommendations instead of AI. "
            "See `AWS_SETUP_GUIDE.md` to enable AI recommendations."
        )
    
    # Check if using demo data
    if hasattr(st.session_state, 'location') and st.session_state.location:
        if 'Demo Data' in st.session_state.location.providers:
            st.warning(
                "📊 **Using Demo Data** - OpenAQ API is unavailable. "
                "Showing sample air quality data for demonstration. "
                "Try: San Francisco, Los Angeles, New York, Beijing, Delhi, London, Tokyo, Seattle"
            )
    
    # Location Input Section - show either text input or globe view
    if st.session_state.view_mode == "text_input":
        render_location_input()
    else:
        render_globe_view()
    
    # Show data sections if location is selected
    if st.session_state.location and st.session_state.current_aqi:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            render_current_conditions()
            render_historical_context()
        
        with col2:
            render_activity_input()
            render_recommendation()


def render_location_input():
    """Render location search interface."""
    st.header("📍 Location")
    
    # Wrap location input and map toggle in mobile-header for compact mobile layout
    st.markdown('<div class="mobile-header">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        location_query = st.text_input(
            "Enter city name or coordinates (lat,lon)",
            placeholder="e.g., San Francisco or 37.7749,-122.4194",
            help="Search for any city worldwide or enter coordinates"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)
    
    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🗺️ Explore Map", use_container_width=True):
            st.session_state.view_mode = "globe_view"
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if search_button and location_query:
        with st.spinner("Searching for location..."):
            location = get_location(location_query)
            
            if location:
                st.session_state.location = location
                provider_info = f" (via {', '.join(location.providers)})" if location.providers else ""
                st.success(f"✓ Found: {location.name}, {location.country}{provider_info}")
                
                # Fetch data
                fetch_and_update_data()
            else:
                st.error(
                    f"❌ Location '{location_query}' not found. "
                    f"Try a major city name or check coordinates format."
                )
    
    # Display current location
    if st.session_state.location:
        st.info(f"📍 Current location: **{st.session_state.location.name}, {st.session_state.location.country}**")


def render_globe_view():
    """Render interactive globe/map visualization using Folium (OpenStreetMap)."""
    import folium
    from streamlit_folium import st_folium
    from src import demo_data
    
    st.header("🌍 Explore Air Quality Map")
    
    # Return to Search button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Return to Search", use_container_width=True):
            st.session_state.view_mode = "text_input"
            st.rerun()
    
    # Display loading indicator during station data fetch
    with st.spinner("Loading air quality stations..."):
        try:
            # Get demo stations (since OpenAQ API is unavailable)
            stations = demo_data.get_demo_global_stations(bounds=None)
            
            # Create Folium map centered on world view
            m = folium.Map(
                location=[20, 0],  # Center on world
                zoom_start=2,
                tiles="OpenStreetMap",
                width="100%",
                height=600
            )
            
            # Add markers for each station
            for station in stations:
                lat, lon = station.coordinates
                
                # Determine marker color based on AQI
                if station.current_aqi is None:
                    color = 'gray'
                    icon = 'question'
                elif station.current_aqi <= 50:
                    color = 'green'
                    icon = 'ok'
                elif station.current_aqi <= 100:
                    color = 'lightgreen'
                    icon = 'info-sign'
                elif station.current_aqi <= 150:
                    color = 'orange'
                    icon = 'warning-sign'
                elif station.current_aqi <= 200:
                    color = 'red'
                    icon = 'exclamation-sign'
                elif station.current_aqi <= 300:
                    color = 'purple'
                    icon = 'remove'
                else:
                    color = 'darkred'
                    icon = 'fire'
                
                # Create popup with station info
                popup_html = f"""
                <div style="font-family: Arial; width: 200px;">
                    <h4 style="margin: 0 0 10px 0;">{station.name}</h4>
                    <p style="margin: 5px 0;"><b>Country:</b> {station.country}</p>
                    <p style="margin: 5px 0;"><b>AQI:</b> {station.current_aqi if station.current_aqi else 'N/A'}</p>
                    <p style="margin: 5px 0;"><b>Category:</b> {station.aqi_category if station.aqi_category else 'N/A'}</p>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=f"{station.name}: AQI {station.current_aqi if station.current_aqi else 'N/A'}",
                    icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
                ).add_to(m)
            
            # Display the map
            st_folium(m, width=None, height=600, returned_objects=[])
            
            # Display information about the map view
            st.info(
                "🗺️ **Air Quality Map**: Explore monitoring stations worldwide using OpenStreetMap. "
                "Click markers to see details. Color coding: "
                "🟢 Good (0-50), 🟡 Moderate (51-100), 🟠 Unhealthy for Sensitive (101-150), "
                "🔴 Unhealthy (151-200), 🟣 Very Unhealthy (201-300), 🟤 Hazardous (301+)"
            )
            
            # Show station count
            st.caption(f"Showing {len(stations)} monitoring stations")
            
            # Location selector
            st.markdown("---")
            st.subheader("Select a Location")
            st.write("Enter a city name to view detailed air quality data:")
            
            # Provide a quick location selector
            col1, col2 = st.columns([3, 1])
            with col1:
                location_query = st.text_input(
                    "Enter location",
                    placeholder="e.g., San Francisco, Los Angeles, New York, Beijing, Delhi, London, Tokyo, Seattle",
                    key="globe_location_input"
                )
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("Select", type="primary", use_container_width=True, key="globe_select_button"):
                    if location_query:
                        with st.spinner("Loading location data..."):
                            location = get_location(location_query)
                            
                            if location:
                                st.session_state.location = location
                                st.session_state.view_mode = "text_input"
                                
                                # Fetch data
                                fetch_and_update_data()
                                st.rerun()
                            else:
                                st.error(f"Location '{location_query}' not found. Try: San Francisco, Los Angeles, New York, Beijing, Delhi, London, Tokyo, or Seattle")
        
        except Exception as e:
            st.error(f"Error loading map view: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            st.write("Please try returning to search and selecting a location manually.")


def render_current_conditions():
    """Display current air quality conditions."""
    st.header("🌡️ Current Air Quality")
    
    aqi = st.session_state.current_aqi
    
    if not aqi:
        st.info("Select a location to view air quality data")
        return
    
    # Large AQI display
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color: {aqi.color}; padding: 30px; border-radius: 10px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 72px;">{aqi.aqi}</h1>
                <p style="color: white; margin: 0; font-size: 24px;">{aqi.category}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.metric("Dominant Pollutant", aqi.dominant_pollutant)
        st.caption(f"Last updated: {aqi.timestamp.strftime('%Y-%m-%d %H:%M UTC')}")
    
    with col3:
        st.subheader("Individual Pollutants")
        for result in aqi.individual_results:
            st.markdown(
                f"""
                <div style="background-color: {result.color}; padding: 5px 10px; border-radius: 5px; margin: 5px 0;">
                    <span style="color: white;"><b>{result.pollutant}:</b> {result.aqi} ({result.category})</span>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_activity_input():
    """Render activity and health sensitivity selectors."""
    st.header("🏃 Your Activity")
    
    activity = st.selectbox(
        "Planned Activity",
        Config.ACTIVITY_OPTIONS,
        index=Config.ACTIVITY_OPTIONS.index(st.session_state.activity)
    )
    
    health_sensitivity = st.selectbox(
        "Health Sensitivity",
        Config.HEALTH_SENSITIVITY_OPTIONS,
        index=Config.HEALTH_SENSITIVITY_OPTIONS.index(st.session_state.health_sensitivity)
    )
    
    # Update session state and regenerate recommendation if changed
    if activity != st.session_state.activity or health_sensitivity != st.session_state.health_sensitivity:
        st.session_state.activity = activity
        st.session_state.health_sensitivity = health_sensitivity
        
        if st.session_state.current_aqi:
            with st.spinner("Generating recommendation..."):
                generate_recommendation()


def render_recommendation():
    """Display AI-generated recommendation."""
    st.header("🤖 Recommendations")
    
    # Show mode indicator
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
        st.caption("📋 Rule-based recommendations (AWS not configured)")
    else:
        st.caption("🤖 AI-powered recommendations via Claude 3.5 Sonnet")
    
    if not st.session_state.recommendation:
        if st.session_state.current_aqi:
            with st.spinner("Generating recommendation..."):
                generate_recommendation()
        else:
            st.info("Select a location and activity to get personalized recommendations")
            return
    
    rec = st.session_state.recommendation
    
    # Safety assessment badge
    badge_colors = {
        "Safe": "#00E400",
        "Moderate Risk": "#FFFF00",
        "Unsafe": "#FF0000"
    }
    
    st.markdown(
        f"""
        <div style="background-color: {badge_colors.get(rec.safety_assessment, '#808080')}; 
                    padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
            <h3 style="color: white; margin: 0;">{rec.safety_assessment}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Recommendation text
    st.write(rec.recommendation_text)
    
    # Precautions
    if rec.precautions:
        with st.expander("⚠️ Precautions", expanded=True):
            for precaution in rec.precautions:
                st.write(f"• {precaution}")
    
    # Time windows
    if rec.time_windows:
        with st.expander("⏰ Optimal Time Windows", expanded=False):
            for tw in rec.time_windows:
                st.write(
                    f"**{tw.start_time.strftime('%H:%M')} - {tw.end_time.strftime('%H:%M')}** "
                    f"(AQI: {tw.expected_aqi_range[0]}-{tw.expected_aqi_range[1]}, "
                    f"Confidence: {tw.confidence})"
                )


def render_historical_context():
    """Display historical air quality trends."""
    st.header("📊 Historical Trends")
    
    if not st.session_state.historical_data:
        st.info("No historical data available for this location")
        return
    
    historical_data = st.session_state.historical_data
    
    if not any(historical_data.values()):
        st.info("No historical data available for this location")
        return
    
    # Create tabs for different time ranges
    tab1, tab2 = st.tabs(["24 Hours", "Summary"])
    
    with tab1:
        render_24h_chart(historical_data)
    
    with tab2:
        render_summary_stats(historical_data)


def render_24h_chart(historical_data):
    """Render 24-hour trend chart."""
    fig = go.Figure()
    
    # Add trace for each pollutant
    for pollutant, measurements in historical_data.items():
        if not measurements:
            continue
        
        timestamps = [m.timestamp for m in measurements]
        values = [m.value for m in measurements]
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=values,
            mode='lines+markers',
            name=pollutant,
            hovertemplate=f'{pollutant}: %{{y:.1f}}<br>%{{x}}<extra></extra>'
        ))
    
    fig.update_layout(
        title="Pollutant Concentrations (24 Hours)",
        xaxis_title="Time",
        yaxis_title="Concentration",
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_summary_stats(historical_data):
    """Render summary statistics."""
    for pollutant, measurements in historical_data.items():
        if not measurements:
            continue
        
        values = [m.value for m in measurements]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(f"{pollutant} Min", f"{min(values):.1f}")
        
        with col2:
            st.metric(f"{pollutant} Avg", f"{sum(values)/len(values):.1f}")
        
        with col3:
            st.metric(f"{pollutant} Max", f"{max(values):.1f}")


def fetch_and_update_data():
    """Fetch all data and update session state."""
    location = st.session_state.location
    
    if not location:
        return
    
    try:
        # Fetch current measurements
        measurements = get_current_measurements(location)
        
        if not measurements:
            st.warning("No recent air quality data available for this location")
            return
        
        # Calculate AQI
        overall_aqi = calculate_overall_aqi(measurements)
        st.session_state.current_aqi = overall_aqi
        
        # Fetch historical data
        historical_data = get_historical_measurements(location, hours=24)
        st.session_state.historical_data = historical_data
        
        # Generate recommendation
        generate_recommendation()
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")


def generate_recommendation():
    """Generate AI recommendation."""
    try:
        recommendation = get_recommendation(
            st.session_state.current_aqi,
            st.session_state.activity,
            st.session_state.health_sensitivity,
            st.session_state.historical_data
        )
        st.session_state.recommendation = recommendation
    
    except Exception as e:
        st.error(f"Error generating recommendation: {str(e)}")


if __name__ == "__main__":
    main()
