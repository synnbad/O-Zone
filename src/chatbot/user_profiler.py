"""
User Profiler Module

Collects and infers user demographic information and communication preferences.
Adapts communication style based on user profile.
"""

import logging
from typing import Optional

from .session_manager import UserProfile

logger = logging.getLogger(__name__)


def collect_user_profile_interactive(session_id: str) -> UserProfile:
    """
    Prompts user for demographic information interactively.
    
    This function is designed to be called by the conversation manager
    to collect user profile information during onboarding. In a CLI or
    chat interface, this would prompt the user with questions.
    
    For now, this returns a default profile. The actual interactive
    prompting will be implemented in the conversation manager when
    the user enters the USER_PROFILE_COLLECTION state.
    
    Args:
        session_id: Session identifier for context
        
    Returns:
        UserProfile with collected information (currently default values)
    """
    logger.info(f"Interactive profile collection initiated for session {session_id}")
    
    # Default profile - actual collection happens through conversation flow
    return UserProfile(
        age_group="adult",
        education_level="high_school",
        technical_expertise="basic",
        communication_preference="balanced",
        occupation_category="general",
        inferred=False
    )


def infer_user_profile(conversation_history: list[tuple[str, str]]) -> UserProfile:
    """
    Infers user profile from conversation patterns and vocabulary.
    
    Analyzes user messages to determine:
    - Technical expertise based on vocabulary (technical terms usage)
    - Communication preference based on message length and complexity
    - Education level based on sentence structure and vocabulary
    
    Args:
        conversation_history: List of (user_message, bot_response) tuples
        
    Returns:
        UserProfile with inferred information
    """
    if not conversation_history:
        logger.debug("No conversation history, returning default inferred profile")
        return UserProfile(inferred=True)
    
    # Extract user messages
    user_messages = [msg for msg, _ in conversation_history]
    all_text = " ".join(user_messages).lower()
    
    # Infer technical expertise from vocabulary
    technical_terms = [
        "aqi", "pollutant", "concentration", "particulate", "pm2.5", "pm10",
        "ozone", "nitrogen dioxide", "sulfur dioxide", "carbon monoxide",
        "μg/m³", "ppm", "air quality index", "emissions"
    ]
    technical_count = sum(1 for term in technical_terms if term in all_text)
    
    if technical_count >= 5:
        technical_expertise = "expert"
        education_level = "advanced"
    elif technical_count >= 2:
        technical_expertise = "intermediate"
        education_level = "college"
    elif technical_count >= 1:
        technical_expertise = "basic"
        education_level = "high_school"
    else:
        technical_expertise = "none"
        education_level = "high_school"
    
    # Infer communication preference from message length
    avg_length = sum(len(msg) for msg in user_messages) / len(user_messages)
    
    if avg_length < 20:
        communication_preference = "concise"
    elif avg_length > 50:
        communication_preference = "detailed"
    else:
        communication_preference = "balanced"
    
    # Infer age group from language patterns (basic heuristic)
    simple_words = ["cool", "awesome", "yeah", "ok", "yep", "nope"]
    simple_count = sum(1 for word in simple_words if word in all_text)
    
    if simple_count >= 3 and avg_length < 30:
        age_group = "teen"
    else:
        age_group = "adult"  # Default assumption
    
    # Check for professional occupation indicators
    professional_terms = [
        "research", "study", "analysis", "data", "scientist", "doctor",
        "environmental", "health professional", "epidemiology"
    ]
    professional_count = sum(1 for term in professional_terms if term in all_text)
    
    if professional_count >= 2:
        occupation_category = "environmental_scientist"
    else:
        occupation_category = "general"
    
    profile = UserProfile(
        age_group=age_group,
        education_level=education_level,
        technical_expertise=technical_expertise,
        communication_preference=communication_preference,
        occupation_category=occupation_category,
        inferred=True
    )
    
    logger.info(
        f"Inferred user profile: age={age_group}, education={education_level}, "
        f"expertise={technical_expertise}, preference={communication_preference}, "
        f"occupation={occupation_category}"
    )
    return profile


def update_profile_from_feedback(profile: UserProfile, feedback: str) -> UserProfile:
    """
    Adjusts profile based on user feedback.
    
    Detects user requests for:
    - Simpler explanations (reduces technical expertise, increases detail)
    - More detailed information (increases explanation depth)
    - More concise responses (reduces explanation depth)
    - More technical information (increases technical expertise)
    
    Args:
        profile: Current user profile
        feedback: User feedback message
        
    Returns:
        Updated UserProfile (creates a new instance with updated values)
    """
    feedback_lower = feedback.lower()
    
    # Create a copy of the profile to modify
    updated_profile = UserProfile(
        age_group=profile.age_group,
        education_level=profile.education_level,
        technical_expertise=profile.technical_expertise,
        communication_preference=profile.communication_preference,
        occupation_category=profile.occupation_category,
        inferred=profile.inferred
    )
    
    # Check for requests for simpler explanation
    if any(phrase in feedback_lower for phrase in [
        "simpler", "don't understand", "explain more simply", "too complex",
        "easier", "basic", "confused", "what does that mean", "more simply"
    ]):
        updated_profile.technical_expertise = "basic"
        updated_profile.communication_preference = "detailed"
        updated_profile.education_level = "high_school"
        logger.info("Updated profile: simplified communication requested")
    
    # Check for requests for more technical detail
    elif any(phrase in feedback_lower for phrase in [
        "more technical", "technical details", "scientific", "specific data",
        "exact numbers", "measurements", "concentrations"
    ]):
        updated_profile.technical_expertise = "expert"
        updated_profile.communication_preference = "detailed"
        logger.info("Updated profile: technical communication requested")
    
    # Check for requests for more detail (but not simpler)
    elif any(phrase in feedback_lower for phrase in [
        "more detail", "elaborate", "tell me more", "explain further",
        "why", "how does"
    ]) and "simpl" not in feedback_lower:
        updated_profile.communication_preference = "detailed"
        logger.info("Updated profile: detailed communication requested")
    
    # Check for requests for brevity
    elif any(phrase in feedback_lower for phrase in [
        "shorter", "brief", "quick", "summarize", "tldr", "bottom line",
        "just tell me", "in short"
    ]):
        updated_profile.communication_preference = "concise"
        logger.info("Updated profile: concise communication requested")
    
    return updated_profile


def get_communication_style(profile: UserProfile) -> dict:
    """
    Returns communication parameters based on user profile.
    
    Args:
        profile: User profile
        
    Returns:
        Dictionary with communication style parameters
    """
    # Determine vocabulary level
    if profile.age_group == "child" or profile.education_level == "basic":
        vocabulary_level = "basic"
    elif profile.technical_expertise in ["expert", "intermediate"]:
        vocabulary_level = "technical"
    else:
        vocabulary_level = "standard"
    
    # Determine sentence complexity
    if profile.age_group == "child" or profile.education_level == "basic":
        sentence_complexity = "simple"
    elif profile.education_level == "advanced":
        sentence_complexity = "complex"
    else:
        sentence_complexity = "moderate"
    
    # Determine explanation depth
    if profile.communication_preference == "concise":
        explanation_depth = "brief"
    elif profile.communication_preference == "detailed":
        explanation_depth = "comprehensive"
    else:
        explanation_depth = "moderate"
    
    # Determine whether to include technical details
    include_technical_details = (
        profile.technical_expertise in ["expert", "intermediate"] or
        profile.occupation_category in ["environmental_scientist", "health_professional"]
    )
    
    return {
        "vocabulary_level": vocabulary_level,
        "sentence_complexity": sentence_complexity,
        "explanation_depth": explanation_depth,
        "include_technical_details": include_technical_details
    }
