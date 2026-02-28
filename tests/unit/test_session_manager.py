"""
Unit tests for session_manager.py

Tests session creation, retrieval, updates, deletion, and cleanup.
Validates: Requirements 13.1, 13.2, 13.4, 13.5
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from src.chatbot.session_manager import (
    create_session,
    get_session,
    update_session,
    delete_session,
    cleanup_expired_sessions,
    SessionContext,
    UserProfile,
    SessionNotFoundError,
    _session_store
)
from src.models import Location, OverallAQI, AQIResult, RecommendationResponse


@pytest.fixture(autouse=True)
def clear_session_store():
    """Clear session store before and after each test"""
    _session_store.clear()
    yield
    _session_store.clear()


@pytest.fixture
def mock_location():
    """Create a mock location"""
    return Location(
        name="Seattle",
        coordinates=(47.6062, -122.3321),
        country="US",
        providers=["openaq"]
    )


@pytest.fixture
def mock_aqi(mock_location):
    """Create a mock AQI"""
    return OverallAQI(
        aqi=75,
        category="Moderate",
        color="#FFFF00",
        dominant_pollutant="PM2.5",
        individual_results=[
            AQIResult(
                pollutant="PM2.5",
                concentration=25.0,
                aqi=75,
                category="Moderate",
                color="#FFFF00"
            )
        ],
        timestamp=datetime.now(timezone.utc),
        location=mock_location
    )


@pytest.fixture
def mock_recommendation():
    """Create a mock recommendation"""
    return RecommendationResponse(
        safety_assessment="Safe",
        recommendation_text="Good conditions for outdoor activities",
        precautions=["Stay hydrated"],
        time_windows=[],
        reasoning="AQI is in acceptable range"
    )


# Test session creation generates unique IDs
class TestSessionCreation:
    """Tests for session creation and unique ID generation"""
    
    def test_create_session_generates_unique_id(self):
        """Test that create_session generates a unique session ID"""
        session = create_session()
        
        assert session.session_id is not None
        assert isinstance(session.session_id, str)
        assert len(session.session_id) > 0
    
    def test_create_session_multiple_unique_ids(self):
        """Test that multiple sessions have different IDs"""
        session1 = create_session()
        session2 = create_session()
        session3 = create_session()
        
        assert session1.session_id != session2.session_id
        assert session1.session_id != session3.session_id
        assert session2.session_id != session3.session_id
    
    def test_create_session_initializes_fields(self):
        """Test that create_session initializes all fields correctly"""
        session = create_session()
        
        # Check required fields
        assert session.session_id is not None
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_updated, datetime)
        assert session.current_state == "greeting"
        
        # Check optional fields are None
        assert session.location is None
        assert session.activity_profile is None
        assert session.health_profile is None
        assert session.current_aqi is None
        assert session.recommendation is None
        
        # Check default values
        assert isinstance(session.user_profile, UserProfile)
        assert session.conversation_history == []
    
    def test_create_session_stores_in_session_store(self):
        """Test that create_session adds session to the store"""
        session = create_session()
        
        assert session.session_id in _session_store
        assert _session_store[session.session_id] == session
    
    def test_create_session_timestamps_are_utc(self):
        """Test that timestamps are in UTC timezone"""
        session = create_session()
        
        assert session.created_at.tzinfo == timezone.utc
        assert session.last_updated.tzinfo == timezone.utc


# Test session retrieval and expiration
class TestSessionRetrieval:
    """Tests for session retrieval and expiration checking"""
    
    def test_get_session_returns_existing_session(self):
        """Test that get_session returns an existing session"""
        session = create_session()
        session_id = session.session_id
        
        retrieved = get_session(session_id)
        
        assert retrieved is not None
        assert retrieved.session_id == session_id
    
    def test_get_session_returns_none_for_nonexistent(self):
        """Test that get_session returns None for non-existent session"""
        retrieved = get_session("nonexistent-id")
        
        assert retrieved is None
    
    def test_get_session_updates_last_updated_timestamp(self):
        """Test that get_session updates the last_updated timestamp"""
        session = create_session()
        original_timestamp = session.last_updated
        
        # Wait a tiny bit to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        retrieved = get_session(session.session_id)
        
        assert retrieved.last_updated > original_timestamp
    
    def test_get_session_expired_returns_none(self):
        """Test that get_session returns None for expired sessions"""
        session = create_session()
        session_id = session.session_id
        
        # Mock the session to be expired
        with patch('src.chatbot.chatbot_config.ChatbotConfig') as mock_config:
            mock_config.SESSION_TTL_MINUTES = 30
            
            # Set last_updated to 31 minutes ago
            expired_time = datetime.now(timezone.utc) - timedelta(minutes=31)
            session.last_updated = expired_time
            
            retrieved = get_session(session_id)
            
            assert retrieved is None
    
    def test_get_session_expired_removes_from_store(self):
        """Test that expired sessions are removed from the store"""
        session = create_session()
        session_id = session.session_id
        
        with patch('src.chatbot.chatbot_config.ChatbotConfig') as mock_config:
            mock_config.SESSION_TTL_MINUTES = 30
            
            # Set last_updated to 31 minutes ago
            expired_time = datetime.now(timezone.utc) - timedelta(minutes=31)
            session.last_updated = expired_time
            
            get_session(session_id)
            
            # Session should be removed from store
            assert session_id not in _session_store
    
    def test_get_session_not_expired_returns_session(self):
        """Test that non-expired sessions are returned"""
        session = create_session()
        session_id = session.session_id
        
        with patch('src.chatbot.chatbot_config.ChatbotConfig') as mock_config:
            mock_config.SESSION_TTL_MINUTES = 30
            
            # Set last_updated to 29 minutes ago (not expired)
            recent_time = datetime.now(timezone.utc) - timedelta(minutes=29)
            session.last_updated = recent_time
            
            retrieved = get_session(session_id)
            
            assert retrieved is not None
            assert retrieved.session_id == session_id


# Test session updates and deletion
class TestSessionUpdates:
    """Tests for session updates and deletion"""
    
    def test_update_session_updates_location(self, mock_location):
        """Test that update_session can update location"""
        session = create_session()
        
        update_session(session.session_id, {"location": mock_location})
        
        updated = _session_store[session.session_id]
        assert updated.location == mock_location
    
    def test_update_session_updates_activity_profile(self):
        """Test that update_session can update activity profile"""
        session = create_session()
        
        update_session(session.session_id, {"activity_profile": "Walking"})
        
        updated = _session_store[session.session_id]
        assert updated.activity_profile == "Walking"
    
    def test_update_session_updates_health_profile(self):
        """Test that update_session can update health profile"""
        session = create_session()
        
        update_session(session.session_id, {"health_profile": "Asthma/Respiratory"})
        
        updated = _session_store[session.session_id]
        assert updated.health_profile == "Asthma/Respiratory"
    
    def test_update_session_updates_user_profile(self):
        """Test that update_session can update user profile"""
        session = create_session()
        new_profile = UserProfile(
            age_group="adult",
            education_level="college",
            technical_expertise="intermediate"
        )
        
        update_session(session.session_id, {"user_profile": new_profile})
        
        updated = _session_store[session.session_id]
        assert updated.user_profile == new_profile
    
    def test_update_session_updates_current_aqi(self, mock_aqi):
        """Test that update_session can update current AQI"""
        session = create_session()
        
        update_session(session.session_id, {"current_aqi": mock_aqi})
        
        updated = _session_store[session.session_id]
        assert updated.current_aqi == mock_aqi
    
    def test_update_session_updates_recommendation(self, mock_recommendation):
        """Test that update_session can update recommendation"""
        session = create_session()
        
        update_session(session.session_id, {"recommendation": mock_recommendation})
        
        updated = _session_store[session.session_id]
        assert updated.recommendation == mock_recommendation
    
    def test_update_session_updates_conversation_history(self):
        """Test that update_session can update conversation history"""
        session = create_session()
        history = [("Hello", "Hi there!"), ("What's the AQI?", "The AQI is 75")]
        
        update_session(session.session_id, {"conversation_history": history})
        
        updated = _session_store[session.session_id]
        assert updated.conversation_history == history
    
    def test_update_session_updates_current_state(self):
        """Test that update_session can update current state"""
        session = create_session()
        
        update_session(session.session_id, {"current_state": "location_collection"})
        
        updated = _session_store[session.session_id]
        assert updated.current_state == "location_collection"
    
    def test_update_session_updates_multiple_fields(self, mock_location):
        """Test that update_session can update multiple fields at once"""
        session = create_session()
        
        updates = {
            "location": mock_location,
            "activity_profile": "Cycling",
            "health_profile": "None",
            "current_state": "recommendation_generation"
        }
        
        update_session(session.session_id, updates)
        
        updated = _session_store[session.session_id]
        assert updated.location == mock_location
        assert updated.activity_profile == "Cycling"
        assert updated.health_profile == "None"
        assert updated.current_state == "recommendation_generation"
    
    def test_update_session_updates_last_updated_timestamp(self):
        """Test that update_session updates the last_updated timestamp"""
        session = create_session()
        original_timestamp = session.last_updated
        
        import time
        time.sleep(0.01)
        
        update_session(session.session_id, {"activity_profile": "Walking"})
        
        updated = _session_store[session.session_id]
        assert updated.last_updated > original_timestamp
    
    def test_update_session_raises_error_for_nonexistent_session(self):
        """Test that update_session raises error for non-existent session"""
        with pytest.raises(SessionNotFoundError):
            update_session("nonexistent-id", {"activity_profile": "Walking"})
    
    def test_update_session_ignores_invalid_fields(self):
        """Test that update_session ignores invalid field names"""
        session = create_session()
        
        # Should not raise error, just ignore invalid fields
        update_session(session.session_id, {
            "activity_profile": "Walking",
            "invalid_field": "should be ignored",
            "another_invalid": 123
        })
        
        updated = _session_store[session.session_id]
        assert updated.activity_profile == "Walking"
        assert not hasattr(updated, "invalid_field")
    
    def test_delete_session_removes_session(self):
        """Test that delete_session removes session from store"""
        session = create_session()
        session_id = session.session_id
        
        assert session_id in _session_store
        
        delete_session(session_id)
        
        assert session_id not in _session_store
    
    def test_delete_session_nonexistent_is_noop(self):
        """Test that deleting non-existent session doesn't raise error"""
        # Should not raise error
        delete_session("nonexistent-id")
    
    def test_delete_session_multiple_times(self):
        """Test that deleting same session multiple times is safe"""
        session = create_session()
        session_id = session.session_id
        
        delete_session(session_id)
        delete_session(session_id)  # Should not raise error
        
        assert session_id not in _session_store


# Test cleanup of expired sessions
class TestSessionCleanup:
    """Tests for cleanup of expired sessions"""
    
    def test_cleanup_expired_sessions_removes_expired(self):
        """Test that cleanup removes expired sessions"""
        # Create multiple sessions
        session1 = create_session()
        session2 = create_session()
        session3 = create_session()
        
        with patch('src.chatbot.chatbot_config.ChatbotConfig') as mock_config:
            mock_config.SESSION_TTL_MINUTES = 30
            
            # Make session1 and session3 expired
            expired_time = datetime.now(timezone.utc) - timedelta(minutes=31)
            session1.last_updated = expired_time
            session3.last_updated = expired_time
            
            # session2 is not expired
            recent_time = datetime.now(timezone.utc) - timedelta(minutes=10)
            session2.last_updated = recent_time
            
            count = cleanup_expired_sessions()
            
            assert count == 2
            assert session1.session_id not in _session_store
            assert session2.session_id in _session_store
            assert session3.session_id not in _session_store
    
    def test_cleanup_expired_sessions_no_expired(self):
        """Test that cleanup returns 0 when no sessions are expired"""
        # Create sessions that are not expired
        session1 = create_session()
        session2 = create_session()
        
        with patch('src.chatbot.chatbot_config.ChatbotConfig') as mock_config:
            mock_config.SESSION_TTL_MINUTES = 30
            
            count = cleanup_expired_sessions()
            
            assert count == 0
            assert session1.session_id in _session_store
            assert session2.session_id in _session_store
    
    def test_cleanup_expired_sessions_empty_store(self):
        """Test that cleanup works with empty session store"""
        count = cleanup_expired_sessions()
        
        assert count == 0
    
    def test_cleanup_expired_sessions_all_expired(self):
        """Test that cleanup removes all sessions when all are expired"""
        # Create multiple sessions
        sessions = [create_session() for _ in range(5)]
        
        with patch('src.chatbot.chatbot_config.ChatbotConfig') as mock_config:
            mock_config.SESSION_TTL_MINUTES = 30
            
            # Make all sessions expired
            expired_time = datetime.now(timezone.utc) - timedelta(minutes=31)
            for session in sessions:
                session.last_updated = expired_time
            
            count = cleanup_expired_sessions()
            
            assert count == 5
            assert len(_session_store) == 0
    
    def test_cleanup_expired_sessions_boundary_case(self):
        """Test cleanup with session just before TTL boundary"""
        session = create_session()
        
        with patch('src.chatbot.chatbot_config.ChatbotConfig') as mock_config:
            mock_config.SESSION_TTL_MINUTES = 30
            
            # Set last_updated to 29 minutes 59 seconds ago (just before expiration)
            boundary_time = datetime.now(timezone.utc) - timedelta(minutes=29, seconds=59)
            session.last_updated = boundary_time
            
            count = cleanup_expired_sessions()
            
            # Session just before boundary should not be expired
            assert count == 0
            assert session.session_id in _session_store
