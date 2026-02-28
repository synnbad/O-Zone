"""
Unit tests for chatbot_interface module
"""

import pytest
from unittest.mock import patch, MagicMock
from src.chatbot.chatbot_interface import ChatbotInterface
from src.chatbot.session_manager import SessionContext, UserProfile
from datetime import datetime


@pytest.fixture
def interface():
    """Create a ChatbotInterface instance"""
    return ChatbotInterface()


@pytest.fixture
def mock_session():
    """Create a mock session"""
    return SessionContext(
        session_id="test-session-123",
        location=None,
        activity_profile=None,
        health_profile=None,
        user_profile=UserProfile(),
        current_aqi=None,
        recommendation=None,
        conversation_history=[],
        current_state="greeting",
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow()
    )


class TestChatbotInterface:
    """Test suite for ChatbotInterface"""
    
    def test_initialization(self, interface):
        """Test interface initialization"""
        assert interface.current_session_id is None
    
    @patch('src.chatbot.chatbot_interface.create_session')
    def test_start_session(self, mock_create_session, interface, mock_session):
        """Test starting a new session"""
        mock_create_session.return_value = mock_session
        
        session_id = interface.start_session()
        
        assert session_id == "test-session-123"
        assert interface.current_session_id == "test-session-123"
        mock_create_session.assert_called_once()
    
    @patch('src.chatbot.chatbot_interface.process_user_input')
    @patch('src.chatbot.chatbot_interface.create_session')
    def test_send_message_creates_session_if_none(self, mock_create_session, mock_process, interface, mock_session):
        """Test that send_message creates a session if none exists"""
        mock_create_session.return_value = mock_session
        mock_process.return_value = "Hello! I'm the O-Zone chatbot."
        
        response = interface.send_message("Hello")
        
        assert interface.current_session_id == "test-session-123"
        mock_create_session.assert_called_once()
        mock_process.assert_called_once_with("test-session-123", "Hello")
    
    @patch('src.chatbot.chatbot_interface.process_user_input')
    def test_send_message_with_existing_session(self, mock_process, interface):
        """Test sending a message with an existing session"""
        interface.current_session_id = "existing-session"
        mock_process.return_value = "I can help you with air quality information."
        
        response = interface.send_message("What can you do?")
        
        assert response == "I can help you with air quality information."
        mock_process.assert_called_once_with("existing-session", "What can you do?")
    
    def test_input_sanitization_strips_whitespace(self, interface):
        """Test that input is sanitized by stripping whitespace"""
        interface.current_session_id = "test-session"
        
        with patch('src.chatbot.chatbot_interface.process_user_input') as mock_process:
            mock_process.return_value = "Response"
            interface.send_message("  Hello  ")
            
            # Verify the message was stripped
            mock_process.assert_called_once_with("test-session", "Hello")
    
    def test_input_sanitization_empty_message(self, interface):
        """Test that empty messages are handled"""
        interface.current_session_id = "test-session"
        
        response = interface.send_message("   ")
        
        assert response == "Please enter a message."
    
    def test_help_command(self, interface):
        """Test /help command"""
        interface.current_session_id = "test-session"
        
        response = interface.send_message("/help")
        
        assert "O-Zone Chatbot Help" in response
        assert "/help" in response
        assert "/restart" in response
    
    def test_help_command_without_slash(self, interface):
        """Test help command without slash"""
        interface.current_session_id = "test-session"
        
        response = interface.send_message("help")
        
        assert "O-Zone Chatbot Help" in response
    
    @patch('src.chatbot.chatbot_interface.create_session')
    def test_restart_command(self, mock_create_session, interface, mock_session):
        """Test /restart command"""
        interface.current_session_id = "old-session"
        mock_create_session.return_value = mock_session
        
        response = interface.send_message("/restart")
        
        assert "Starting a new conversation" in response
        assert interface.current_session_id == "test-session-123"
        mock_create_session.assert_called_once()
    
    @patch('src.chatbot.chatbot_interface.create_session')
    def test_restart_command_without_slash(self, mock_create_session, interface, mock_session):
        """Test restart command without slash"""
        interface.current_session_id = "old-session"
        mock_create_session.return_value = mock_session
        
        response = interface.send_message("restart")
        
        assert "Starting a new conversation" in response
        assert interface.current_session_id == "test-session-123"
    
    @patch('src.chatbot.chatbot_interface.process_user_input')
    def test_error_handling(self, mock_process, interface):
        """Test error handling when process_user_input raises an exception"""
        interface.current_session_id = "test-session"
        mock_process.side_effect = Exception("Test error")
        
        response = interface.send_message("Hello")
        
        assert "I encountered an error" in response
        assert "/restart" in response
    
    def test_get_help_message(self, interface):
        """Test help message content"""
        help_msg = interface._get_help_message()
        
        assert "O-Zone Chatbot Help" in help_msg
        assert "air quality" in help_msg.lower()
        assert "recommendations" in help_msg.lower()
        assert "/help" in help_msg
        assert "/restart" in help_msg
    
    @patch('src.chatbot.chatbot_interface.process_user_input')
    def test_send_message_with_explicit_session_id(self, mock_process, interface):
        """Test sending a message with an explicit session ID"""
        interface.current_session_id = "current-session"
        mock_process.return_value = "Response"
        
        response = interface.send_message("Hello", session_id="different-session")
        
        # Should use the explicit session ID, not the current one
        mock_process.assert_called_once_with("different-session", "Hello")
        # Current session should remain unchanged
        assert interface.current_session_id == "current-session"
