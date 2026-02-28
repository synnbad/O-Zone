"""
Property-Based Tests for Session Management

Tests universal properties that should hold for all session management operations.
Uses Hypothesis for property-based testing with 100+ iterations per property.

Validates: Requirements 13.1, 13.4, 13.5
"""

import pytest
from hypothesis import given, strategies as st, assume, settings
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
    _session_store
)
from src.models import Location, OverallAQI, AQIResult, RecommendationResponse


# ============================================================================
# Hypothesis Strategies
# ============================================================================

# Strategy for valid activity profiles
activity_strategy = st.sampled_from([
    "Walking",
    "Jogging/Running",
    "Cycling",
    "Outdoor Study/Work",
    "Sports Practice",
    "Child Outdoor Play"
])

# Strategy for valid health profiles
health_strategy = st.sampled_from([
    "None",
    "Allergies",
    "Asthma/Respiratory",
    "Child/Elderly",
    "Pregnant"
])

# Strategy for conversation states
state_strategy = st.sampled_from([
    "greeting",
    "location_collection",
    "activity_selection",
    "health_profile_selection",
    "user_profile_collection",
    "recommendation_generation",
    "recommendation_presentation",
    "follow_up",
    "error_recovery",
    "goodbye"
])

# Strategy for user profile
user_profile_strategy = st.builds(
    UserProfile,
    age_group=st.sampled_from(["child", "teen", "adult", "senior"]),
    education_level=st.sampled_from(["basic", "high_school", "college", "advanced"]),
    technical_expertise=st.sampled_from(["none", "basic", "intermediate", "expert"]),
    communication_preference=st.sampled_from(["concise", "detailed", "balanced"]),
    occupation_category=st.sampled_from(["environmental_scientist", "health_professional", "general"]),
    inferred=st.booleans()
)

# Strategy for location
location_strategy = st.builds(
    Location,
    name=st.text(min_size=1, max_size=50),
    coordinates=st.tuples(
        st.floats(min_value=-90, max_value=90),
        st.floats(min_value=-180, max_value=180)
    ),
    country=st.text(min_size=2, max_size=2, alphabet=st.characters(whitelist_categories=('Lu',))),
    providers=st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=3)
)

# Strategy for conversation history
conversation_history_strategy = st.lists(
    st.tuples(
        st.text(min_size=1, max_size=100),
        st.text(min_size=1, max_size=200)
    ),
    min_size=0,
    max_size=20
)


# ============================================================================
# Property 24: Session State Maintenance
# ============================================================================

@settings(deadline=10000, max_examples=100)
@given(
    location=location_strategy,
    activity=activity_strategy,
    health=health_strategy,
    user_profile=user_profile_strategy
)
def test_property_24_session_state_maintenance(location, activity, health, user_profile):
    """
    Feature: ozone-chatbot, Property 24: Session State Maintenance
    
    For any session, the chatbot must maintain session state including location,
    activity profile, health profile, and user profile.
    
    **Validates: Requirements 13.1**
    """
    # Clear session store before test
    _session_store.clear()
    
    try:
        # Create a new session
        session = create_session()
        session_id = session.session_id
        
        # Update session with all context information
        update_session(session_id, {
            "location": location,
            "activity_profile": activity,
            "health_profile": health,
            "user_profile": user_profile
        })
        
        # Retrieve the session
        retrieved_session = get_session(session_id)
        
        # Verify session maintains all state
        assert retrieved_session is not None, "Session should exist"
        assert retrieved_session.session_id == session_id, "Session ID should match"
        
        # Verify location is maintained
        assert retrieved_session.location == location, "Location should be maintained"
        assert retrieved_session.location.name == location.name
        assert retrieved_session.location.coordinates == location.coordinates
        assert retrieved_session.location.country == location.country
        
        # Verify activity profile is maintained
        assert retrieved_session.activity_profile == activity, "Activity profile should be maintained"
        
        # Verify health profile is maintained
        assert retrieved_session.health_profile == health, "Health profile should be maintained"
        
        # Verify user profile is maintained
        assert retrieved_session.user_profile == user_profile, "User profile should be maintained"
        assert retrieved_session.user_profile.age_group == user_profile.age_group
        assert retrieved_session.user_profile.education_level == user_profile.education_level
        assert retrieved_session.user_profile.technical_expertise == user_profile.technical_expertise
        assert retrieved_session.user_profile.communication_preference == user_profile.communication_preference
        assert retrieved_session.user_profile.occupation_category == user_profile.occupation_category
        
    finally:
        # Cleanup
        _session_store.clear()


@settings(deadline=10000, max_examples=100)
@given(
    activity=activity_strategy,
    health=health_strategy,
    state=state_strategy
)
def test_property_24_partial_state_maintenance(activity, health, state):
    """
    Feature: ozone-chatbot, Property 24: Session State Maintenance (Partial State)
    
    For any session with partial context, the chatbot must maintain the provided
    state while keeping unprovided fields as None.
    
    **Validates: Requirements 13.1**
    """
    _session_store.clear()
    
    try:
        # Create session with partial context
        session = create_session()
        session_id = session.session_id
        
        # Update only some fields
        update_session(session_id, {
            "activity_profile": activity,
            "health_profile": health,
            "current_state": state
        })
        
        # Retrieve and verify
        retrieved = get_session(session_id)
        
        assert retrieved is not None
        assert retrieved.activity_profile == activity
        assert retrieved.health_profile == health
        assert retrieved.current_state == state
        
        # Verify unprovided fields remain None
        assert retrieved.location is None
        assert retrieved.current_aqi is None
        assert retrieved.recommendation is None
        
    finally:
        _session_store.clear()


# ============================================================================
# Property 26: Session Context Persistence
# ============================================================================

@settings(deadline=10000, max_examples=100)
@given(
    location=location_strategy,
    activity=activity_strategy,
    health=health_strategy,
    conversation_history=conversation_history_strategy,
    num_requests=st.integers(min_value=2, max_value=10)
)
def test_property_26_session_context_persistence(location, activity, health, conversation_history, num_requests):
    """
    Feature: ozone-chatbot, Property 26: Session Context Persistence
    
    For any session, context must persist across multiple requests within the same session.
    
    **Validates: Requirements 13.4**
    """
    _session_store.clear()
    
    try:
        # Create session with initial context
        session = create_session()
        session_id = session.session_id
        
        # Set initial context
        update_session(session_id, {
            "location": location,
            "activity_profile": activity,
            "health_profile": health,
            "conversation_history": conversation_history
        })
        
        # Simulate multiple requests by retrieving session multiple times
        for i in range(num_requests):
            retrieved = get_session(session_id)
            
            # Verify context persists across all requests
            assert retrieved is not None, f"Session should exist on request {i+1}"
            assert retrieved.session_id == session_id
            assert retrieved.location == location, f"Location should persist on request {i+1}"
            assert retrieved.activity_profile == activity, f"Activity should persist on request {i+1}"
            assert retrieved.health_profile == health, f"Health profile should persist on request {i+1}"
            assert retrieved.conversation_history == conversation_history, f"History should persist on request {i+1}"
            
            # Add to conversation history to simulate interaction
            new_entry = (f"User message {i}", f"Bot response {i}")
            conversation_history.append(new_entry)
            update_session(session_id, {"conversation_history": conversation_history})
        
        # Final verification that all accumulated history is present
        final_session = get_session(session_id)
        assert len(final_session.conversation_history) >= num_requests
        
    finally:
        _session_store.clear()


@settings(deadline=10000, max_examples=100)
@given(
    initial_state=state_strategy,
    updates=st.lists(
        st.dictionaries(
            keys=st.sampled_from(["activity_profile", "health_profile", "current_state"]),
            values=st.one_of(activity_strategy, health_strategy, state_strategy),
            min_size=1,
            max_size=2
        ),
        min_size=2,
        max_size=5
    )
)
def test_property_26_context_persistence_through_updates(initial_state, updates):
    """
    Feature: ozone-chatbot, Property 26: Session Context Persistence (Through Updates)
    
    For any session, context must persist even when other fields are updated.
    
    **Validates: Requirements 13.4**
    """
    _session_store.clear()
    
    try:
        # Create session with initial state
        session = create_session()
        session_id = session.session_id
        
        # Set initial activity and health
        initial_activity = "Walking"
        initial_health = "None"
        update_session(session_id, {
            "activity_profile": initial_activity,
            "health_profile": initial_health,
            "current_state": initial_state
        })
        
        # Track what should be the current values
        expected_activity = initial_activity
        expected_health = initial_health
        expected_state = initial_state
        
        # Apply multiple updates
        for update_dict in updates:
            # Apply the update
            update_session(session_id, update_dict)
            
            # Update expectations
            if "activity_profile" in update_dict:
                expected_activity = update_dict["activity_profile"]
            if "health_profile" in update_dict:
                expected_health = update_dict["health_profile"]
            if "current_state" in update_dict:
                expected_state = update_dict["current_state"]
            
            # Verify persistence
            retrieved = get_session(session_id)
            assert retrieved is not None
            assert retrieved.activity_profile == expected_activity
            assert retrieved.health_profile == expected_health
            assert retrieved.current_state == expected_state
        
    finally:
        _session_store.clear()


# ============================================================================
# Property 27: Session Cleanup
# ============================================================================

@settings(deadline=10000, max_examples=100)
@given(
    num_sessions=st.integers(min_value=1, max_value=10)
)
def test_property_27_session_cleanup_on_termination(num_sessions):
    """
    Feature: ozone-chatbot, Property 27: Session Cleanup
    
    For any session termination, the chatbot must clear the session context.
    
    **Validates: Requirements 13.5**
    """
    _session_store.clear()
    
    try:
        # Create multiple sessions
        session_ids = []
        for _ in range(num_sessions):
            session = create_session()
            session_ids.append(session.session_id)
        
        # Verify all sessions exist
        assert len(_session_store) == num_sessions
        for session_id in session_ids:
            assert session_id in _session_store
        
        # Delete each session (termination)
        for session_id in session_ids:
            delete_session(session_id)
            
            # Verify session is cleared
            assert session_id not in _session_store, f"Session {session_id} should be cleared"
            assert get_session(session_id) is None, f"Session {session_id} should not be retrievable"
        
        # Verify store is empty
        assert len(_session_store) == 0, "All sessions should be cleared"
        
    finally:
        _session_store.clear()


@settings(deadline=10000, max_examples=100)
@given(
    num_expired=st.integers(min_value=1, max_value=5),
    num_active=st.integers(min_value=1, max_value=5)
)
def test_property_27_session_cleanup_expired_sessions(num_expired, num_active):
    """
    Feature: ozone-chatbot, Property 27: Session Cleanup (Expired Sessions)
    
    For any expired sessions, the cleanup process must clear their context
    while preserving active sessions.
    
    **Validates: Requirements 13.5**
    """
    _session_store.clear()
    
    try:
        with patch('src.chatbot.chatbot_config.ChatbotConfig') as mock_config:
            mock_config.SESSION_TTL_MINUTES = 30
            
            # Create expired sessions
            expired_ids = []
            for _ in range(num_expired):
                session = create_session()
                expired_ids.append(session.session_id)
                # Make session expired (31 minutes old)
                expired_time = datetime.now(timezone.utc) - timedelta(minutes=31)
                session.last_updated = expired_time
            
            # Create active sessions
            active_ids = []
            for _ in range(num_active):
                session = create_session()
                active_ids.append(session.session_id)
                # Make session recent (10 minutes old)
                recent_time = datetime.now(timezone.utc) - timedelta(minutes=10)
                session.last_updated = recent_time
            
            # Verify all sessions exist before cleanup
            assert len(_session_store) == num_expired + num_active
            
            # Run cleanup
            cleaned_count = cleanup_expired_sessions()
            
            # Verify correct number of sessions cleaned
            assert cleaned_count == num_expired, f"Should clean {num_expired} expired sessions"
            
            # Verify expired sessions are cleared
            for session_id in expired_ids:
                assert session_id not in _session_store, f"Expired session {session_id} should be cleared"
                assert get_session(session_id) is None
            
            # Verify active sessions are preserved
            for session_id in active_ids:
                assert session_id in _session_store, f"Active session {session_id} should be preserved"
                assert get_session(session_id) is not None
            
            # Verify final count
            assert len(_session_store) == num_active, "Only active sessions should remain"
            
    finally:
        _session_store.clear()


@settings(deadline=10000, max_examples=100)
@given(
    location=location_strategy,
    activity=activity_strategy,
    conversation_history=conversation_history_strategy
)
def test_property_27_session_cleanup_clears_all_context(location, activity, conversation_history):
    """
    Feature: ozone-chatbot, Property 27: Session Cleanup (Complete Context Clearing)
    
    For any session termination, all context fields must be cleared from the store.
    
    **Validates: Requirements 13.5**
    """
    _session_store.clear()
    
    try:
        # Create session with full context
        session = create_session()
        session_id = session.session_id
        
        # Populate with rich context
        update_session(session_id, {
            "location": location,
            "activity_profile": activity,
            "conversation_history": conversation_history,
            "current_state": "recommendation_presentation"
        })
        
        # Verify context exists
        retrieved = get_session(session_id)
        assert retrieved.location is not None
        assert retrieved.activity_profile is not None
        assert len(retrieved.conversation_history) > 0 or len(conversation_history) == 0
        
        # Delete session
        delete_session(session_id)
        
        # Verify complete cleanup - session should not exist at all
        assert session_id not in _session_store
        assert get_session(session_id) is None
        
        # Verify we can't access any of the old context
        # (since the session doesn't exist, we can't retrieve it)
        
    finally:
        _session_store.clear()


# ============================================================================
# Additional Property: Session Isolation
# ============================================================================

@settings(deadline=10000, max_examples=100)
@given(
    num_sessions=st.integers(min_value=2, max_value=5),
    activities=st.lists(activity_strategy, min_size=2, max_size=5),
    healths=st.lists(health_strategy, min_size=2, max_size=5)
)
def test_property_session_isolation(num_sessions, activities, healths):
    """
    Feature: ozone-chatbot, Property: Session Isolation
    
    For any multiple concurrent sessions, updates to one session must not affect others.
    
    **Validates: Requirements 13.1, 13.4**
    """
    _session_store.clear()
    
    # Ensure we have enough activities and healths
    assume(len(activities) >= num_sessions)
    assume(len(healths) >= num_sessions)
    
    try:
        # Create multiple sessions with different contexts
        sessions = []
        for i in range(num_sessions):
            session = create_session()
            update_session(session.session_id, {
                "activity_profile": activities[i],
                "health_profile": healths[i]
            })
            sessions.append(session)
        
        # Verify each session has its own context
        for i, session in enumerate(sessions):
            retrieved = get_session(session.session_id)
            assert retrieved is not None
            assert retrieved.activity_profile == activities[i]
            assert retrieved.health_profile == healths[i]
        
        # Update one session
        update_session(sessions[0].session_id, {
            "activity_profile": "Cycling",
            "current_state": "follow_up"
        })
        
        # Verify other sessions are unaffected
        for i in range(1, num_sessions):
            retrieved = get_session(sessions[i].session_id)
            assert retrieved.activity_profile == activities[i], f"Session {i} should be unaffected"
            assert retrieved.health_profile == healths[i], f"Session {i} should be unaffected"
            assert retrieved.current_state != "follow_up", f"Session {i} should have different state"
        
    finally:
        _session_store.clear()
