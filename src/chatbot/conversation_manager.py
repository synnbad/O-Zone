"""
Conversation Manager Module

Orchestrates conversation flow through states and manages user interactions.
"""

import logging
from enum import Enum

from .session_manager import SessionContext, get_session, update_session
from .chatbot_config import ChatbotConfig

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Conversation flow states"""
    GREETING = "greeting"
    LOCATION_COLLECTION = "location_collection"
    ACTIVITY_SELECTION = "activity_selection"
    HEALTH_PROFILE_SELECTION = "health_profile_selection"
    USER_PROFILE_COLLECTION = "user_profile_collection"
    RECOMMENDATION_GENERATION = "recommendation_generation"
    RECOMMENDATION_PRESENTATION = "recommendation_presentation"
    FOLLOW_UP = "follow_up"
    ERROR_RECOVERY = "error_recovery"
    GOODBYE = "goodbye"


def process_user_input(session_id: str, user_input: str) -> str:
    """
    Main entry point for handling user messages.
    
    Args:
        session_id: Session identifier
        user_input: User's message
        
    Returns:
        Bot response string
    """
    session = get_session(session_id)
    
    if session is None:
        return "Your session has expired. Please start a new conversation."
    
    # Route to appropriate handler based on current state
    try:
        if session.current_state == ConversationState.GREETING.value:
            response = handle_greeting(session)
        elif session.current_state == ConversationState.LOCATION_COLLECTION.value:
            response = handle_location_collection(session, user_input)
        elif session.current_state == ConversationState.ACTIVITY_SELECTION.value:
            response = handle_activity_selection(session, user_input)
        elif session.current_state == ConversationState.HEALTH_PROFILE_SELECTION.value:
            response = handle_health_profile_selection(session, user_input)
        elif session.current_state == ConversationState.RECOMMENDATION_GENERATION.value:
            response = handle_recommendation_generation(session)
        elif session.current_state == ConversationState.RECOMMENDATION_PRESENTATION.value:
            response = handle_recommendation_presentation(session)
        elif session.current_state == ConversationState.FOLLOW_UP.value:
            response = handle_follow_up(session, user_input)
        else:
            response = "I'm not sure how to help with that. Let's start over."
            update_session(session_id, {"current_state": ConversationState.GREETING.value})
        
        # Update conversation history
        history = session.conversation_history + [(user_input, response)]
        update_session(session_id, {"conversation_history": history})
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing user input: {e}", exc_info=True)
        return handle_error_recovery(session, e)


def handle_greeting(session: SessionContext) -> str:
    """Handles initial greeting state"""
    update_session(session.session_id, {
        "current_state": ConversationState.LOCATION_COLLECTION.value
    })
    return ChatbotConfig.GREETING_TEMPLATE


def handle_location_collection(session: SessionContext, user_input: str) -> str:
    """Handles location collection state"""
    from .backend_integration import resolve_location, LocationNotFoundError
    
    logger.info(f"Location input received: {user_input}")
    
    try:
        # Resolve location using backend integration
        location = resolve_location(user_input)
        
        # Update session with location
        update_session(session.session_id, {
            "location": location,
            "current_state": ConversationState.ACTIVITY_SELECTION.value
        })
        
        # Confirm location and move to activity selection
        activity_options = ChatbotConfig.get_activity_options_text()
        return f"Great! I found {location.name} in {location.country}.\n\nNow, what outdoor activity are you planning?\n\n{activity_options}\n\nPlease select one."
        
    except LocationNotFoundError as e:
        # Stay in location collection state and provide error message
        logger.warning(f"Location not found: {user_input}")
        return str(e)


def handle_activity_selection(session: SessionContext, user_input: str) -> str:
    """Handles activity selection state"""
    user_input_clean = user_input.strip()
    
    # Check if input matches an activity option
    selected_activity = None
    for activity in ChatbotConfig.ACTIVITY_OPTIONS:
        if activity.lower() in user_input_clean.lower():
            selected_activity = activity
            break
    
    # Also check for numeric selection
    if not selected_activity:
        try:
            index = int(user_input_clean) - 1
            if 0 <= index < len(ChatbotConfig.ACTIVITY_OPTIONS):
                selected_activity = ChatbotConfig.ACTIVITY_OPTIONS[index]
        except ValueError:
            pass
    
    if not selected_activity:
        activity_options = ChatbotConfig.get_activity_options_text()
        return f"I didn't recognize that activity. Please choose from:\n\n{activity_options}"
    
    # Update session with activity
    update_session(session.session_id, {
        "activity_profile": selected_activity,
        "current_state": ConversationState.HEALTH_PROFILE_SELECTION.value
    })
    
    health_options = ChatbotConfig.get_health_options_text()
    return f"Got it! You're planning {selected_activity}.\n\nDo you have any health sensitivities I should consider?\n\n{health_options}\n\nPlease select one."


def handle_health_profile_selection(session: SessionContext, user_input: str) -> str:
    """Handles health profile selection state"""
    user_input_clean = user_input.strip()
    
    # Check if input matches a health option
    selected_health = None
    for health in ChatbotConfig.HEALTH_SENSITIVITY_OPTIONS:
        if health.lower() in user_input_clean.lower():
            selected_health = health
            break
    
    # Also check for numeric selection
    if not selected_health:
        try:
            index = int(user_input_clean) - 1
            if 0 <= index < len(ChatbotConfig.HEALTH_SENSITIVITY_OPTIONS):
                selected_health = ChatbotConfig.HEALTH_SENSITIVITY_OPTIONS[index]
        except ValueError:
            pass
    
    if not selected_health:
        health_options = ChatbotConfig.get_health_options_text()
        return f"I didn't recognize that option. Please choose from:\n\n{health_options}"
    
    # Update session with health profile
    update_session(session.session_id, {
        "health_profile": selected_health,
        "current_state": ConversationState.RECOMMENDATION_GENERATION.value
    })
    
    return f"Thank you. Let me check the air quality and generate recommendations for you..."


def handle_recommendation_generation(session: SessionContext) -> str:
    """Handles recommendation generation state"""
    from .backend_integration import (
        fetch_current_aqi, 
        fetch_historical_data,
        generate_recommendation,
        NoDataAvailableError
    )
    
    logger.info(f"Generating recommendation for session {session.session_id}")
    
    # Check if we have all required context
    if not session.location or not session.activity_profile or not session.health_profile:
        logger.error("Missing required context for recommendation generation")
        return "I need more information before I can generate a recommendation. Let's start over."
    
    try:
        # Fetch current AQI
        overall_aqi = fetch_current_aqi(session.location)
        
        # Fetch historical data (optional, don't fail if unavailable)
        historical_data = fetch_historical_data(session.location, hours=24)
        
        # Generate recommendation
        recommendation = generate_recommendation(
            overall_aqi=overall_aqi,
            activity=session.activity_profile,
            health_sensitivity=session.health_profile,
            historical_data=historical_data if historical_data else None
        )
        
        # Update session with results
        update_session(session.session_id, {
            "current_aqi": overall_aqi,
            "recommendation": recommendation,
            "current_state": ConversationState.RECOMMENDATION_PRESENTATION.value
        })
        
        # Move directly to presentation
        return handle_recommendation_presentation(session)
        
    except NoDataAvailableError as e:
        logger.warning(f"No data available for {session.location.name}")
        update_session(session.session_id, {
            "current_state": ConversationState.ERROR_RECOVERY.value
        })
        return str(e)
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}", exc_info=True)
        return handle_error_recovery(session, e)


def handle_recommendation_presentation(session: SessionContext) -> str:
    """Handles recommendation presentation state"""
    from .response_generator import format_aqi_explanation, format_recommendation
    
    logger.info(f"Presenting recommendation for session {session.session_id}")
    
    # Check if we have recommendation data
    if not session.current_aqi or not session.recommendation:
        logger.error("Missing AQI or recommendation data for presentation")
        return "I don't have recommendation data available. Let's try again."
    
    # Update state to follow-up
    update_session(session.session_id, {
        "current_state": ConversationState.FOLLOW_UP.value
    })
    
    # Format AQI explanation
    aqi_text = format_aqi_explanation(session.current_aqi, session.user_profile)
    
    # Format recommendation
    rec_text = format_recommendation(session.recommendation, session.user_profile)
    
    # Combine and add follow-up options
    response = f"{aqi_text}\n\n{rec_text}\n\n"
    response += "Would you like to:\n"
    response += "- See time windows for your activity\n"
    response += "- View air quality trends\n"
    response += "- Change your location\n"
    response += "- Ask another question"
    
    return response


def handle_follow_up(session: SessionContext, user_input: str) -> str:
    """
    Handles follow-up questions and requests.
    
    Supports:
    - Location changes mid-session
    - Time window requests
    - Trend requests (24-hour or 7-day)
    - General questions
    
    Args:
        session: Current session context
        user_input: User's follow-up message
        
    Returns:
        Bot response string
    """
    user_input_lower = user_input.lower()
    
    # Detect intent and route to appropriate handler
    
    # Time window requests
    if any(word in user_input_lower for word in ["time", "window", "when", "best time"]):
        return _handle_time_window_request(session)
    
    # Trend requests
    elif any(word in user_input_lower for word in ["trend", "history", "pattern", "24", "7 day", "week"]):
        return _handle_trend_request(session, user_input_lower)
    
    # Location change requests
    elif any(word in user_input_lower for word in ["location", "change", "different", "another city"]):
        return _handle_location_change_request(session, user_input)
    
    # Goodbye
    elif any(word in user_input_lower for word in ["bye", "goodbye", "exit", "quit"]):
        update_session(session.session_id, {
            "current_state": ConversationState.GOODBYE.value
        })
        return "Thank you for using O-Zone! Stay safe and breathe easy!"
    
    # General help
    else:
        return "I can help you with:\n- Time windows for your activity\n- Air quality trends (24-hour or 7-day)\n- Changing your location\n\nWhat would you like to know?"


def _handle_time_window_request(session: SessionContext) -> str:
    """
    Handles time window prediction requests.
    
    Fetches time windows from existing recommendation or generates new ones.
    
    Args:
        session: Current session context
        
    Returns:
        Formatted time windows or error message
    """
    from .response_generator import format_time_windows
    
    logger.info(f"Time window request for session {session.session_id}")
    
    # Check if we have a recommendation with time windows
    if session.recommendation and session.recommendation.time_windows:
        time_windows = session.recommendation.time_windows
        logger.info(f"Using {len(time_windows)} time windows from existing recommendation")
        return format_time_windows(time_windows, session.user_profile)
    
    # If no time windows in recommendation, inform user
    # (In a full implementation, we could fetch forecast data and generate new windows)
    logger.info("No time windows available in current recommendation")
    return (
        "I don't have time window predictions available right now. "
        "Time windows are generated when air quality forecasts are available. "
        "You could try checking back later or asking for a new recommendation."
    )


def _handle_trend_request(session: SessionContext, user_input_lower: str) -> str:
    """
    Handles air quality trend requests.
    
    Fetches historical data and formats trends for display.
    
    Args:
        session: Current session context
        user_input_lower: Lowercase user input for period detection
        
    Returns:
        Formatted trend data or error message
    """
    from .backend_integration import fetch_historical_data
    from .response_generator import format_trend_data
    
    logger.info(f"Trend request for session {session.session_id}")
    
    # Check if we have location
    if not session.location:
        logger.warning("Trend request without location")
        return "I need a location to show air quality trends. Please provide a location first."
    
    # Determine trend period (24-hour or 7-day)
    if "7" in user_input_lower or "week" in user_input_lower:
        hours = 168  # 7 days
        period_name = "7-day"
    else:
        hours = 24
        period_name = "24-hour"
    
    logger.info(f"Fetching {period_name} trend data for {session.location.name}")
    
    try:
        # Fetch historical data
        historical_data = fetch_historical_data(session.location, hours=hours)
        
        if not historical_data:
            logger.info(f"No historical data available for {session.location.name}")
            return (
                f"I don't have {period_name} historical data available for {session.location.name}. "
                f"This sometimes happens with monitoring stations that have limited data. "
                f"You could try a nearby larger city."
            )
        
        # Format trend data for presentation
        return format_trend_data(historical_data, session.user_profile, period_name)
        
    except Exception as e:
        logger.error(f"Error fetching trend data: {e}", exc_info=True)
        return (
            f"I encountered an issue retrieving trend data for {session.location.name}. "
            f"Please try again in a moment."
        )


def _handle_location_change_request(session: SessionContext, user_input: str) -> str:
    """
    Handles mid-session location change requests.
    
    Validates new location, updates session, and regenerates recommendations.
    
    Args:
        session: Current session context
        user_input: User's input (may contain new location)
        
    Returns:
        Response with new location confirmation or prompt for location
    """
    from .backend_integration import resolve_location, LocationNotFoundError
    
    logger.info(f"Location change request for session {session.session_id}")
    
    # Check if user provided a new location in the same message
    # Look for location after keywords like "change to", "try", etc.
    user_input_lower = user_input.lower()
    
    # Try to extract location from input
    new_location_query = None
    for keyword in ["change to", "try", "check", "what about", "how about"]:
        if keyword in user_input_lower:
            # Extract text after keyword (use lowercase for matching, but split original for proper case)
            idx = user_input_lower.index(keyword)
            after_keyword = user_input[idx + len(keyword):].strip()
            if after_keyword:
                new_location_query = after_keyword
                break
    
    # If no location extracted, prompt for it
    if not new_location_query:
        update_session(session.session_id, {
            "current_state": ConversationState.LOCATION_COLLECTION.value
        })
        return "Sure! What's the new location you'd like to check?"
    
    # Try to resolve the new location
    try:
        new_location = resolve_location(new_location_query)
        
        # Update session with new location
        update_session(session.session_id, {
            "location": new_location,
            "current_aqi": None,  # Clear old AQI
            "recommendation": None,  # Clear old recommendation
            "current_state": ConversationState.RECOMMENDATION_GENERATION.value
        })
        
        logger.info(f"Location changed to {new_location.name} for session {session.session_id}")
        
        # Generate new recommendation for the new location
        # Note: We need to fetch the updated session since we just updated it
        updated_session = get_session(session.session_id)
        if updated_session:
            return handle_recommendation_generation(updated_session)
        else:
            return "I encountered an issue updating your location. Please try again."
        
    except LocationNotFoundError as e:
        # Keep previous location and prompt for correction
        logger.warning(f"Invalid location change attempt: {new_location_query}")
        return str(e)


def handle_error_recovery(session: SessionContext, error: Exception) -> str:
    """Handles errors and guides user to recovery"""
    from .response_generator import format_error_message
    from .backend_integration import LocationNotFoundError, NoDataAvailableError
    
    logger.error(f"Error in session {session.session_id}: {error}", exc_info=True)
    
    update_session(session.session_id, {
        "current_state": ConversationState.ERROR_RECOVERY.value
    })
    
    # Translate error to user-friendly message
    if isinstance(error, LocationNotFoundError):
        error_type = "LOCATION_ERROR"
        details = str(error)
        suggestions = [
            "Try a nearby larger city",
            "Check the spelling of the location",
            "Try a different location"
        ]
    elif isinstance(error, NoDataAvailableError):
        error_type = "DATA_ERROR"
        details = str(error)
        suggestions = [
            "Try a nearby larger city",
            "Check back in a few hours",
            "Try a different location"
        ]
    else:
        error_type = "GENERAL_ERROR"
        details = "I encountered an unexpected issue"
        suggestions = [
            "Try again in a moment",
            "Start over with a different location",
            "Contact support if the issue persists"
        ]
    
    return format_error_message(error_type, details, suggestions)


def determine_next_state(session: SessionContext) -> ConversationState:
    """Determines next required state based on session context"""
    if session.location is None:
        return ConversationState.LOCATION_COLLECTION
    elif session.activity_profile is None:
        return ConversationState.ACTIVITY_SELECTION
    elif session.health_profile is None:
        return ConversationState.HEALTH_PROFILE_SELECTION
    elif session.recommendation is None:
        return ConversationState.RECOMMENDATION_GENERATION
    else:
        return ConversationState.FOLLOW_UP
