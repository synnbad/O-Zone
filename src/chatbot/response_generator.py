"""
Response Generator Module

Generates and formats chatbot responses with adaptive communication.
"""

import logging
from typing import Any

from src.models import OverallAQI, RecommendationResponse
from .session_manager import UserProfile
from .user_profiler import get_communication_style
from .chatbot_config import ChatbotConfig

logger = logging.getLogger(__name__)


def generate_response(message_type: str, data: dict, user_profile: UserProfile) -> str:
    """
    Main entry point for response generation.
    
    Args:
        message_type: Type of message to generate
        data: Data to include in response
        user_profile: User profile for adaptation
        
    Returns:
        Formatted response string
    """
    if message_type == "aqi_explanation":
        return format_aqi_explanation(data.get("aqi"), user_profile)
    elif message_type == "recommendation":
        return format_recommendation(data.get("recommendation"), user_profile)
    elif message_type == "time_windows":
        return format_time_windows(data.get("time_windows", []), user_profile)
    elif message_type == "error":
        return format_error_message(
            data.get("error_type", ""),
            data.get("details", ""),
            data.get("suggestions", [])
        )
    else:
        logger.warning(f"Unknown message type: {message_type}")
        return "I'm not sure how to respond to that."


def format_aqi_explanation(aqi: OverallAQI, user_profile: UserProfile) -> str:
    """
    Formats AQI data for conversational presentation.
    
    Adapts technical detail based on user profile. For users who would benefit
    from AI-powered adaptation (children, non-technical users, or users requesting
    detailed explanations), uses bedrock_adapter.generate_adaptive_response() to
    leverage Claude Opus 4.6. Falls back to rule-based formatting if Bedrock is
    unavailable.
    
    Args:
        aqi: Overall AQI data
        user_profile: User profile for adaptation
        
    Returns:
        Formatted AQI explanation adapted to user's understanding level
    """
    if aqi is None:
        return "I don't have air quality data available right now."
    
    style = get_communication_style(user_profile)
    
    # Determine if AI-powered adaptation would be beneficial
    use_ai_adaptation = (
        user_profile.age_group == "child" or
        user_profile.education_level == "basic" or
        user_profile.technical_expertise == "expert" or
        user_profile.communication_preference == "detailed" or
        user_profile.occupation_category in ["environmental_scientist", "health_professional"]
    )
    
    # Try AI-powered adaptation for users who would benefit
    if use_ai_adaptation:
        try:
            from .bedrock_adapter import generate_adaptive_response
            
            # Build context with AQI data
            context = {
                "aqi_value": aqi.aqi,
                "category": aqi.category,
                "dominant_pollutant": aqi.dominant_pollutant,
                "task": "aqi_explanation"
            }
            
            # Add individual pollutant data for technical users
            if style["include_technical_details"] and aqi.individual_results:
                context["pollutant_details"] = [
                    {
                        "pollutant": result.pollutant,
                        "concentration": result.concentration,
                        "aqi": result.aqi
                    }
                    for result in aqi.individual_results
                ]
            
            # Construct prompt based on user profile
            if user_profile.age_group == "child" or user_profile.education_level == "basic":
                prompt = f"Explain this air quality information in simple terms suitable for a child or someone with basic education. The air quality index is {aqi.aqi}, which is {aqi.category}. The main pollutant is {aqi.dominant_pollutant}. Use simple words and short sentences."
            elif user_profile.technical_expertise == "expert" or user_profile.occupation_category in ["environmental_scientist", "health_professional"]:
                prompt = f"Provide a technical explanation of this air quality data for an expert. AQI: {aqi.aqi} ({aqi.category}), dominant pollutant: {aqi.dominant_pollutant}. Include scientific details and pollutant concentrations."
            else:
                prompt = f"Explain this air quality information clearly. The AQI is {aqi.aqi}, which is {aqi.category}. The dominant pollutant is {aqi.dominant_pollutant}."
            
            adapted_explanation = generate_adaptive_response(prompt, user_profile, context)
            logger.info("Successfully generated adaptive AQI explanation using Claude Opus 4.6")
            return adapted_explanation
            
        except Exception as e:
            logger.warning(f"Claude Opus adaptation failed for AQI explanation, using rule-based: {e}")
            # Fall through to rule-based formatting
    
    # Fallback: Rule-based formatting
    # Basic explanation with correct field name
    if style["vocabulary_level"] == "basic":
        explanation = f"The air quality number is {aqi.aqi}, which is {aqi.category}."
    else:
        explanation = f"The air quality index is {aqi.aqi}, which is {aqi.category}."
    
    # Add technical details for advanced users
    if style["include_technical_details"] and aqi.dominant_pollutant:
        pollutant_name = aqi.dominant_pollutant
        if style["vocabulary_level"] == "basic":
            explanation += f" The main air pollution is {pollutant_name}."
        else:
            explanation += f" The dominant pollutant is {pollutant_name}."
            
            # Include individual pollutant concentrations for technical users
            if aqi.individual_results:
                explanation += "\n\nPollutant details:"
                for result in aqi.individual_results:
                    explanation += f"\n- {result.pollutant}: {result.concentration:.1f} (AQI: {result.aqi})"
    
    return explanation


def format_recommendation(recommendation: RecommendationResponse, user_profile: UserProfile) -> str:
    """
    Formats AI recommendation for user's understanding level.
    
    Adjusts explanation depth based on user profile. For users who would benefit
    from AI-powered adaptation (children, non-technical users, or users requesting
    detailed explanations), uses bedrock_adapter.generate_adaptive_response() to
    leverage Claude Opus 4.6. Falls back to rule-based formatting if Bedrock is
    unavailable.
    
    Args:
        recommendation: Recommendation data
        user_profile: User profile for adaptation
        
    Returns:
        Formatted recommendation adapted to user's understanding level and preferences
    """
    if recommendation is None:
        return "I couldn't generate a recommendation right now."
    
    style = get_communication_style(user_profile)
    
    # Determine if AI-powered adaptation would be beneficial
    use_ai_adaptation = (
        user_profile.age_group == "child" or
        user_profile.education_level == "basic" or
        user_profile.technical_expertise == "expert" or
        user_profile.communication_preference in ["concise", "detailed"] or
        user_profile.occupation_category in ["environmental_scientist", "health_professional"]
    )
    
    # Try AI-powered adaptation for users who would benefit
    if use_ai_adaptation:
        try:
            from .bedrock_adapter import generate_adaptive_response
            
            # Build context with recommendation data
            context = {
                "safety_assessment": recommendation.safety_assessment,
                "recommendation_text": recommendation.recommendation_text,
                "task": "recommendation_formatting"
            }
            
            if recommendation.precautions:
                context["precautions"] = recommendation.precautions
            
            if recommendation.reasoning:
                context["reasoning"] = recommendation.reasoning
            
            if recommendation.time_windows:
                context["time_windows_count"] = len(recommendation.time_windows)
            
            # Construct prompt based on user profile
            if user_profile.age_group == "child" or user_profile.education_level == "basic":
                prompt = f"Rewrite this air quality recommendation in simple terms suitable for a child or someone with basic education. Use simple words and short sentences.\n\nSafety: {recommendation.safety_assessment}\nRecommendation: {recommendation.recommendation_text}"
                if recommendation.precautions:
                    prompt += f"\nThings to watch out for: {', '.join(recommendation.precautions)}"
            elif user_profile.communication_preference == "concise":
                prompt = f"Provide a brief, concise summary of this air quality recommendation. Be direct and to the point.\n\nSafety: {recommendation.safety_assessment}\nRecommendation: {recommendation.recommendation_text}"
            elif user_profile.communication_preference == "detailed":
                prompt = f"Provide a comprehensive, detailed explanation of this air quality recommendation. Include context, reasoning, and background information.\n\nSafety: {recommendation.safety_assessment}\nRecommendation: {recommendation.recommendation_text}"
                if recommendation.reasoning:
                    prompt += f"\nReasoning: {recommendation.reasoning}"
                if recommendation.precautions:
                    prompt += f"\nPrecautions: {', '.join(recommendation.precautions)}"
            elif user_profile.technical_expertise == "expert" or user_profile.occupation_category in ["environmental_scientist", "health_professional"]:
                prompt = f"Provide a technical explanation of this air quality recommendation for an expert. Include scientific details and professional insights.\n\nSafety: {recommendation.safety_assessment}\nRecommendation: {recommendation.recommendation_text}"
                if recommendation.reasoning:
                    prompt += f"\nReasoning: {recommendation.reasoning}"
            else:
                prompt = f"Format this air quality recommendation clearly.\n\nSafety: {recommendation.safety_assessment}\nRecommendation: {recommendation.recommendation_text}"
            
            adapted_recommendation = generate_adaptive_response(prompt, user_profile, context)
            
            # Add time windows if available (append to adapted text)
            if recommendation.time_windows:
                if style["vocabulary_level"] == "basic":
                    adapted_recommendation += "\n\nBest times for your activity:\n"
                else:
                    adapted_recommendation += "\n\nRecommended time windows:\n"
                
                for i, window in enumerate(recommendation.time_windows, 1):
                    start_str = window.start_time.strftime('%I:%M %p')
                    end_str = window.end_time.strftime('%I:%M %p')
                    aqi_min, aqi_max = window.expected_aqi_range
                    
                    adapted_recommendation += f"{i}. {start_str} - {end_str} (AQI: {aqi_min}-{aqi_max})"
                    
                    if style["include_technical_details"]:
                        adapted_recommendation += f" [Confidence: {window.confidence}]"
                    
                    adapted_recommendation += "\n"
            
            logger.info("Successfully generated adaptive recommendation using Claude Opus 4.6")
            return adapted_recommendation.strip()
            
        except Exception as e:
            logger.warning(f"Claude Opus adaptation failed for recommendation, using rule-based: {e}")
            # Fall through to rule-based formatting
    
    # Fallback: Rule-based formatting
    # Start with safety assessment
    response = f"Safety Assessment: {recommendation.safety_assessment}\n\n"
    
    # Add recommendation text
    response += f"{recommendation.recommendation_text}\n\n"
    
    # Add precautions if available and user wants detail
    if recommendation.precautions and style["explanation_depth"] != "brief":
        if style["vocabulary_level"] == "basic":
            response += "Things to watch out for:\n"
        else:
            response += "Precautions:\n"
        
        for precaution in recommendation.precautions:
            response += f"- {precaution}\n"
        response += "\n"
    
    # Add reasoning for detailed explanations
    if style["explanation_depth"] == "comprehensive" and recommendation.reasoning:
        response += f"Why: {recommendation.reasoning}\n\n"
    
    # Add time windows if available
    if recommendation.time_windows:
        if style["vocabulary_level"] == "basic":
            response += "Best times for your activity:\n"
        else:
            response += "Recommended time windows:\n"
        
        for i, window in enumerate(recommendation.time_windows, 1):
            start_str = window.start_time.strftime('%I:%M %p')
            end_str = window.end_time.strftime('%I:%M %p')
            aqi_min, aqi_max = window.expected_aqi_range
            
            response += f"{i}. {start_str} - {end_str} (AQI: {aqi_min}-{aqi_max})"
            
            if style["include_technical_details"]:
                response += f" [Confidence: {window.confidence}]"
            
            response += "\n"
    
    return response.strip()


def format_time_windows(time_windows: list, user_profile: UserProfile) -> str:
    """
    Formats predicted time windows conversationally.
    
    Args:
        time_windows: List of time window predictions
        user_profile: User profile for adaptation
        
    Returns:
        Formatted time windows
    """
    if not time_windows:
        return "I don't see any suitable time windows in the forecast."
    
    style = get_communication_style(user_profile)
    
    response = "Here are the best time windows for your activity:\n\n"
    
    for i, window in enumerate(time_windows, 1):
        response += f"{i}. {window.start_time.strftime('%I:%M %p')} - {window.end_time.strftime('%I:%M %p')}"
        response += f" (Expected AQI: {window.expected_aqi_range[0]}-{window.expected_aqi_range[1]})"
        
        if style["include_technical_details"]:
            response += f" [Confidence: {window.confidence}]"
        
        response += "\n"
    
    return response


def format_trend_data(historical_data: dict, user_profile: UserProfile, period_name: str) -> str:
    """
    Formats historical air quality data as trends.
    
    Args:
        historical_data: Dictionary mapping pollutant names to lists of Measurement objects
        user_profile: User profile for adaptation
        period_name: Name of the period (e.g., "24-hour", "7-day")
        
    Returns:
        Formatted trend data
    """
    from src.aqi_calculator import calculate_aqi
    
    if not historical_data:
        return f"No {period_name} trend data available."
    
    style = get_communication_style(user_profile)
    
    # Build response
    if style["vocabulary_level"] == "basic":
        response = f"Here's how the air quality has changed over the past {period_name.replace('-', ' ')}:\n\n"
    else:
        response = f"Air quality trends for the past {period_name}:\n\n"
    
    # Get all measurements sorted by time
    all_measurements = []
    for pollutant, measurements in historical_data.items():
        all_measurements.extend(measurements)
    
    if not all_measurements:
        return f"No {period_name} trend data available."
    
    # Sort by timestamp
    all_measurements.sort(key=lambda m: m.timestamp)
    
    # Group measurements by time period (hourly for 24h, daily for 7-day)
    if period_name == "24-hour":
        # Show hourly trends
        from collections import defaultdict
        hourly_data = defaultdict(list)
        
        for measurement in all_measurements:
            hour_key = measurement.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_data[hour_key].append(measurement)
        
        # Calculate AQI for each hour and show trends
        response += "Time | AQI | Category\n"
        response += "---- | --- | --------\n"
        
        for hour_key in sorted(hourly_data.keys())[-24:]:  # Last 24 hours
            measurements = hourly_data[hour_key]
            # Calculate average AQI for the hour
            aqi_values = []
            for m in measurements:
                try:
                    aqi_result = calculate_aqi(m.pollutant, m.value)
                    aqi_values.append(aqi_result.aqi)
                except:
                    pass
            
            if aqi_values:
                avg_aqi = int(sum(aqi_values) / len(aqi_values))
                # Determine category
                if avg_aqi <= 50:
                    category = "Good"
                elif avg_aqi <= 100:
                    category = "Moderate"
                elif avg_aqi <= 150:
                    category = "Unhealthy for Sensitive"
                elif avg_aqi <= 200:
                    category = "Unhealthy"
                elif avg_aqi <= 300:
                    category = "Very Unhealthy"
                else:
                    category = "Hazardous"
                
                time_str = hour_key.split()[1][:5]  # HH:MM format
                response += f"{time_str} | {avg_aqi} | {category}\n"
    
    else:  # 7-day
        # Show daily trends
        from collections import defaultdict
        daily_data = defaultdict(list)
        
        for measurement in all_measurements:
            day_key = measurement.timestamp.strftime('%Y-%m-%d')
            daily_data[day_key].append(measurement)
        
        response += "Date | Avg AQI | Category\n"
        response += "---- | ------- | --------\n"
        
        for day_key in sorted(daily_data.keys())[-7:]:  # Last 7 days
            measurements = daily_data[day_key]
            # Calculate average AQI for the day
            aqi_values = []
            for m in measurements:
                try:
                    aqi_result = calculate_aqi(m.pollutant, m.value)
                    aqi_values.append(aqi_result.aqi)
                except:
                    pass
            
            if aqi_values:
                avg_aqi = int(sum(aqi_values) / len(aqi_values))
                # Determine category
                if avg_aqi <= 50:
                    category = "Good"
                elif avg_aqi <= 100:
                    category = "Moderate"
                elif avg_aqi <= 150:
                    category = "Unhealthy for Sensitive"
                elif avg_aqi <= 200:
                    category = "Unhealthy"
                elif avg_aqi <= 300:
                    category = "Very Unhealthy"
                else:
                    category = "Hazardous"
                
                date_str = day_key.split('-')[1] + '/' + day_key.split('-')[2]  # MM/DD format
                response += f"{date_str} | {avg_aqi} | {category}\n"
    
    # Add interpretation for detailed users
    if style["explanation_depth"] == "comprehensive":
        response += "\n"
        if style["vocabulary_level"] == "basic":
            response += "This shows how the air quality number has changed over time."
        else:
            response += "This trend analysis shows how air quality has varied over the selected period."
    
    return response


def format_error_message(error_type: str, details: str, suggestions: list[str]) -> str:
    """
    Creates user-friendly error message.
    
    Args:
        error_type: Type of error
        details: Error details
        suggestions: List of suggested actions
        
    Returns:
        Formatted error message
    """
    message = "I encountered an issue"
    
    if details:
        message += f": {details}"
    
    message += ".\n\n"
    
    if suggestions:
        message += "You could try:\n"
        for suggestion in suggestions:
            message += f"- {suggestion}\n"
    
    return message


def adapt_vocabulary(text: str, vocabulary_level: str, user_profile: UserProfile | None = None) -> str:
    """
    Adapts vocabulary based on level using Claude Opus 4.6.
    
    Uses bedrock_adapter.generate_adaptive_response() to leverage Claude Opus 4.6
    for truly adaptive, demographic-aware vocabulary adjustment. Falls back to
    rule-based replacements if Bedrock is unavailable.
    
    Args:
        text: Original text
        vocabulary_level: Target vocabulary level (basic, standard, technical)
        user_profile: Optional user profile for AI-powered adaptation
        
    Returns:
        Adapted text with vocabulary adjusted to target level
    """
    # Try AI-powered adaptation if user profile is available
    if user_profile is not None:
        try:
            from .bedrock_adapter import generate_adaptive_response
            
            # Construct prompt for vocabulary adaptation
            if vocabulary_level == "basic":
                prompt = f"Rewrite the following text using simple, everyday vocabulary suitable for children or users with basic education. Avoid technical jargon and use short, clear words:\n\n{text}"
            elif vocabulary_level == "technical":
                prompt = f"Rewrite the following text to include technical details and scientific terminology suitable for experts or professionals:\n\n{text}"
            else:
                # Standard level - minimal changes
                return text
            
            context = {
                "task": "vocabulary_adaptation",
                "target_level": vocabulary_level,
                "original_text_length": len(text)
            }
            
            adapted_text = generate_adaptive_response(prompt, user_profile, context)
            logger.info(f"Successfully adapted vocabulary using Claude Opus 4.6 (level: {vocabulary_level})")
            return adapted_text
            
        except Exception as e:
            logger.warning(f"Claude Opus adaptation failed, falling back to rule-based: {e}")
            # Fall through to rule-based approach
    
    # Fallback: Rule-based vocabulary replacement
    if vocabulary_level == "basic":
        replacements = ChatbotConfig.VOCABULARY_LEVELS["basic"]
        for technical, simple in replacements.items():
            text = text.replace(technical, simple)
    
    return text


def adapt_sentence_complexity(text: str, complexity_level: str, user_profile: UserProfile | None = None) -> str:
    """
    Adapts sentence complexity based on level using Claude Opus 4.6.
    
    Uses bedrock_adapter.generate_adaptive_response() to leverage Claude Opus 4.6
    for truly adaptive sentence structure adjustment. Falls back to rule-based
    transformations if Bedrock is unavailable.
    
    Args:
        text: Original text
        complexity_level: Target complexity level (simple, moderate, complex)
        user_profile: Optional user profile for AI-powered adaptation
        
    Returns:
        Adapted text with sentence structure adjusted to target complexity
    """
    # Try AI-powered adaptation if user profile is available
    if user_profile is not None:
        try:
            from .bedrock_adapter import generate_adaptive_response
            
            # Construct prompt for sentence complexity adaptation
            if complexity_level == "simple":
                prompt = f"Rewrite the following text using short, simple sentences. Break long sentences into shorter ones. Use clear, direct language:\n\n{text}"
            elif complexity_level == "complex":
                prompt = f"Rewrite the following text using more sophisticated sentence structures. Combine related ideas where appropriate:\n\n{text}"
            else:
                # Moderate level - minimal changes
                return text
            
            context = {
                "task": "sentence_complexity_adaptation",
                "target_level": complexity_level,
                "original_text_length": len(text)
            }
            
            adapted_text = generate_adaptive_response(prompt, user_profile, context)
            logger.info(f"Successfully adapted sentence complexity using Claude Opus 4.6 (level: {complexity_level})")
            return adapted_text
            
        except Exception as e:
            logger.warning(f"Claude Opus adaptation failed, falling back to rule-based: {e}")
            # Fall through to rule-based approach
    
    # Fallback: Rule-based sentence transformation
    if complexity_level == "simple":
        # Break long sentences at conjunctions
        text = text.replace(", and ", ". ")
        text = text.replace(", but ", ". However, ")
    
    return text
