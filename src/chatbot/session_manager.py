"""
Session Manager Module

Manages user sessions including creation, retrieval, updates, and cleanup.
Stores session context with location, activity, health profile, and user profile.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

from src.models import Location, OverallAQI, RecommendationResponse

logger = logging.getLogger(__name__)


@dataclass
class UserProfile:
    """User demographic and communication preference information"""
    age_group: Optional[str] = None  # child, teen, adult, senior
    education_level: Optional[str] = None  # basic, high_school, college, advanced
    technical_expertise: Optional[str] = None  # none, basic, intermediate, expert
    communication_preference: Optional[str] = None  # concise, detailed, balanced
    occupation_category: Optional[str] = None  # environmental_scientist, health_professional, general
    inferred: bool = False  # True if profile inferred from conversation


@dataclass
class SessionContext:
    """Complete state of a user session"""
    session_id: str
    location: Optional[Location] = None
    activity_profile: Optional[str] = None
    health_profile: Optional[str] = None
    user_profile: UserProfile = field(default_factory=UserProfile)
    current_aqi: Optional[OverallAQI] = None
    recommendation: Optional[RecommendationResponse] = None
    conversation_history: list[tuple[str, str]] = field(default_factory=list)  # (user_message, bot_response)
    current_state: str = "greeting"  # Conversation state
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# In-memory session store
_session_store: dict[str, SessionContext] = {}


class SessionNotFoundError(Exception):
    """Raised when a session is not found"""
    pass


def create_session() -> SessionContext:
    """
    Creates a new session with a unique ID.
    
    Returns:
        SessionContext: New session object
    """
    session_id = str(uuid.uuid4())
    session = SessionContext(session_id=session_id)
    _session_store[session_id] = session
    
    logger.info(f"Created new session: {session_id}")
    return session


def get_session(session_id: str) -> Optional[SessionContext]:
    """
    Retrieves a session from the store.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        SessionContext if found and not expired, None otherwise
    """
    session = _session_store.get(session_id)
    
    if session is None:
        logger.debug(f"Session not found: {session_id}")
        return None
    
    # Check if session is expired
    from .chatbot_config import ChatbotConfig
    ttl = timedelta(minutes=ChatbotConfig.SESSION_TTL_MINUTES)
    if datetime.now(timezone.utc) - session.last_updated > ttl:
        logger.info(f"Session expired: {session_id}")
        delete_session(session_id)
        return None
    
    # Update last_updated timestamp
    session.last_updated = datetime.now(timezone.utc)
    logger.debug(f"Retrieved session: {session_id}")
    return session


def update_session(session_id: str, updates: dict) -> None:
    """
    Updates specified fields in a session.
    
    Args:
        session_id: Unique session identifier
        updates: Dictionary of field names and values to update
        
    Raises:
        SessionNotFoundError: If session doesn't exist
    """
    session = _session_store.get(session_id)
    
    if session is None:
        raise SessionNotFoundError(f"Session not found: {session_id}")
    
    # Validate update keys
    valid_fields = {
        'location', 'activity_profile', 'health_profile', 'user_profile',
        'current_aqi', 'recommendation', 'conversation_history', 'current_state'
    }
    
    invalid_keys = set(updates.keys()) - valid_fields
    if invalid_keys:
        logger.warning(f"Ignoring invalid update keys: {invalid_keys}")
    
    # Apply updates
    for key, value in updates.items():
        if key in valid_fields:
            setattr(session, key, value)
    
    session.last_updated = datetime.now(timezone.utc)
    logger.debug(f"Updated session {session_id}: {list(updates.keys())}")


def delete_session(session_id: str) -> None:
    """
    Removes a session from the store.
    
    Args:
        session_id: Unique session identifier
    """
    if session_id in _session_store:
        del _session_store[session_id]
        logger.info(f"Deleted session: {session_id}")


def cleanup_expired_sessions() -> int:
    """
    Removes sessions older than TTL.
    
    Returns:
        Number of sessions deleted
    """
    from .chatbot_config import ChatbotConfig
    
    ttl = timedelta(minutes=ChatbotConfig.SESSION_TTL_MINUTES)
    now = datetime.now(timezone.utc)
    
    expired_sessions = [
        session_id for session_id, session in _session_store.items()
        if now - session.last_updated > ttl
    ]
    
    for session_id in expired_sessions:
        delete_session(session_id)
    
    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    return len(expired_sessions)
