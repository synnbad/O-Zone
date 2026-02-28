"""
Session Manager for API

In-memory session storage with TTL for demo purposes.
"""

from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages in-memory sessions with TTL"""
    
    def __init__(self, ttl_minutes: int = 30):
        """
        Initialize session manager.
        
        Args:
            ttl_minutes: Time-to-live for sessions in minutes
        """
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
    
    def create_session(self) -> str:
        """
        Create a new session.
        
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {
            'created_at': datetime.now(UTC),
            'last_accessed': datetime.now(UTC),
            'data': {}
        }
        logger.info(f"Created session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if expired/not found
        """
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        
        # Check TTL
        if datetime.now(UTC) - session['last_accessed'] > self._ttl:
            logger.info(f"Session expired: {session_id}")
            del self._sessions[session_id]
            return None
        
        # Update last accessed
        session['last_accessed'] = datetime.now(UTC)
        return session['data']
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session identifier
            data: Data to update
            
        Returns:
            True if successful, False if session not found
        """
        if session_id not in self._sessions:
            return False
        
        self._sessions[session_id]['data'].update(data)
        self._sessions[session_id]['last_accessed'] = datetime.now(UTC)
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def cleanup_expired(self) -> int:
        """
        Remove expired sessions.
        
        Returns:
            Number of sessions deleted
        """
        now = datetime.now(UTC)
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session['last_accessed'] > self._ttl
        ]
        
        for sid in expired:
            del self._sessions[sid]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")
        
        return len(expired)


# Global session manager instance
session_manager = SessionManager(ttl_minutes=30)
