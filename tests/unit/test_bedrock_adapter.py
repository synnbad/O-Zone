"""
Unit tests for bedrock_adapter module.

Tests the Claude Opus 4.6 integration including prompt construction,
adaptive response generation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json

from src.chatbot.bedrock_adapter import (
    generate_adaptive_response,
    construct_adaptive_prompt,
    call_claude_opus
)
from src.chatbot.session_manager import UserProfile


class TestConstructAdaptivePrompt:
    """Tests for construct_adaptive_prompt function"""
    
    def test_basic_profile_prompt(self):
        """Test prompt construction with basic user profile"""
        profile = UserProfile(
            age_group="child",
            education_level="basic",
            technical_expertise="none",
            communication_preference="concise"
        )
        
        prompt = construct_adaptive_prompt("What is AQI?", profile, {})
        
        assert "What is AQI?" in prompt
        assert "child" in prompt
        assert "basic" in prompt
        assert "simple" in prompt.lower()
        assert "brief" in prompt.lower()
    
    def test_expert_profile_prompt(self):
        """Test prompt construction with expert user profile"""
        profile = UserProfile(
            age_group="adult",
            education_level="advanced",
            technical_expertise="expert",
            communication_preference="detailed",
            occupation_category="environmental_scientist"
        )
        
        prompt = construct_adaptive_prompt("Explain PM2.5", profile, {})
        
        assert "Explain PM2.5" in prompt
        assert "expert" in prompt
        assert "advanced" in prompt
        assert "technical" in prompt.lower()
        assert "detailed" in prompt.lower() or "comprehensive" in prompt.lower()
    
    def test_prompt_with_context(self):
        """Test prompt construction with context data"""
        profile = UserProfile(
            age_group="adult",
            education_level="high_school",
            technical_expertise="basic"
        )
        
        context = {
            "aqi": 85,
            "location": "Seattle",
            "activity": "Walking"
        }
        
        prompt = construct_adaptive_prompt("Should I go outside?", profile, context)
        
        assert "Should I go outside?" in prompt
        assert "aqi" in prompt.lower() or "85" in prompt
        assert "Seattle" in prompt or "location" in prompt.lower()
    
    def test_prompt_without_optional_fields(self):
        """Test prompt construction with minimal profile"""
        profile = UserProfile()
        
        prompt = construct_adaptive_prompt("Test prompt", profile, {})
        
        assert "Test prompt" in prompt
        # Should still generate valid prompt even with no profile data
        assert len(prompt) > 0


class TestGenerateAdaptiveResponse:
    """Tests for generate_adaptive_response function"""
    
    @patch('src.chatbot.bedrock_adapter.call_claude_opus')
    def test_successful_response_generation(self, mock_call):
        """Test successful adaptive response generation"""
        mock_call.return_value = "Air quality is good today!"
        
        profile = UserProfile(
            age_group="adult",
            education_level="high_school",
            technical_expertise="basic"
        )
        
        response = generate_adaptive_response("What's the air quality?", profile, {})
        
        assert response == "Air quality is good today!"
        assert mock_call.called
    
    @patch('src.chatbot.bedrock_adapter.call_claude_opus')
    def test_error_handling_returns_fallback(self, mock_call):
        """Test that errors return fallback message"""
        mock_call.side_effect = Exception("Bedrock unavailable")
        
        profile = UserProfile()
        
        response = generate_adaptive_response("Test prompt", profile, {})
        
        assert "trouble" in response.lower() or "try again" in response.lower()
        assert len(response) > 0


class TestCallClaudeOpus:
    """Tests for call_claude_opus function"""
    
    @patch('src.chatbot.bedrock_adapter.boto3.client')
    @patch('src.config.Config')
    def test_successful_bedrock_call(self, mock_config, mock_boto_client):
        """Test successful call to Claude Opus via Bedrock"""
        # Setup config
        mock_config.AWS_ACCESS_KEY_ID = "test_key"
        mock_config.AWS_SECRET_ACCESS_KEY = "test_secret"
        mock_config.AWS_REGION = "us-east-1"
        mock_config.BEDROCK_MODEL_ID = "anthropic.claude-opus-4-6-20250514"
        
        # Setup mock Bedrock response
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'Test response from Claude'}]
        }).encode()
        
        mock_client.invoke_model.return_value = mock_response
        
        # Call function
        response = call_claude_opus("Test prompt", {"temperature": 0.7, "max_tokens": 500})
        
        assert response == "Test response from Claude"
        assert mock_client.invoke_model.called
    
    @patch('src.config.Config')
    def test_missing_credentials_raises_error(self, mock_config):
        """Test that missing AWS credentials raises error"""
        mock_config.AWS_ACCESS_KEY_ID = None
        mock_config.AWS_SECRET_ACCESS_KEY = None
        
        with pytest.raises(Exception) as exc_info:
            call_claude_opus("Test prompt", {})
        
        assert "credentials" in str(exc_info.value).lower()
    
    @patch('src.chatbot.bedrock_adapter.boto3.client')
    @patch('src.config.Config')
    @patch('src.chatbot.bedrock_adapter.time.sleep')
    def test_retry_logic_on_transient_failure(self, mock_sleep, mock_config, mock_boto_client):
        """Test retry logic for transient failures"""
        # Setup config
        mock_config.AWS_ACCESS_KEY_ID = "test_key"
        mock_config.AWS_SECRET_ACCESS_KEY = "test_secret"
        mock_config.AWS_REGION = "us-east-1"
        mock_config.BEDROCK_MODEL_ID = "anthropic.claude-opus-4-6-20250514"
        
        # Setup mock to fail twice then succeed
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'Success after retry'}]
        }).encode()
        
        mock_client.invoke_model.side_effect = [
            Exception("Transient error"),
            Exception("Another transient error"),
            mock_response
        ]
        
        # Call function
        response = call_claude_opus("Test prompt", {"temperature": 0.7})
        
        assert response == "Success after retry"
        assert mock_client.invoke_model.call_count == 3
        assert mock_sleep.call_count == 2  # Should sleep between retries
    
    @patch('src.chatbot.bedrock_adapter.boto3.client')
    @patch('src.config.Config')
    def test_authentication_error_no_retry(self, mock_config, mock_boto_client):
        """Test that authentication errors don't trigger retries"""
        # Setup config
        mock_config.AWS_ACCESS_KEY_ID = "test_key"
        mock_config.AWS_SECRET_ACCESS_KEY = "test_secret"
        mock_config.AWS_REGION = "us-east-1"
        mock_config.BEDROCK_MODEL_ID = "anthropic.claude-opus-4-6-20250514"
        
        # Setup mock to fail with auth error
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_client.invoke_model.side_effect = Exception("Invalid credentials")
        
        # Call function and expect immediate failure
        with pytest.raises(Exception) as exc_info:
            call_claude_opus("Test prompt", {})
        
        assert "authentication" in str(exc_info.value).lower()
        assert mock_client.invoke_model.call_count == 1  # No retries
    
    @patch('src.chatbot.bedrock_adapter.boto3.client')
    @patch('src.config.Config')
    @patch('src.chatbot.bedrock_adapter.time.sleep')
    def test_all_retries_exhausted(self, mock_sleep, mock_config, mock_boto_client):
        """Test behavior when all retries are exhausted"""
        # Setup config
        mock_config.AWS_ACCESS_KEY_ID = "test_key"
        mock_config.AWS_SECRET_ACCESS_KEY = "test_secret"
        mock_config.AWS_REGION = "us-east-1"
        mock_config.BEDROCK_MODEL_ID = "anthropic.claude-opus-4-6-20250514"
        
        # Setup mock to always fail
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        mock_client.invoke_model.side_effect = Exception("Persistent error")
        
        # Call function and expect failure after retries
        with pytest.raises(Exception) as exc_info:
            call_claude_opus("Test prompt", {})
        
        assert "failed after" in str(exc_info.value).lower()
        assert mock_client.invoke_model.call_count == 3  # Max retries
    
    @patch('src.chatbot.bedrock_adapter.boto3.client')
    @patch('src.config.Config')
    def test_optional_parameters_included(self, mock_config, mock_boto_client):
        """Test that optional parameters are included in request"""
        # Setup config
        mock_config.AWS_ACCESS_KEY_ID = "test_key"
        mock_config.AWS_SECRET_ACCESS_KEY = "test_secret"
        mock_config.AWS_REGION = "us-east-1"
        mock_config.BEDROCK_MODEL_ID = "anthropic.claude-opus-4-6-20250514"
        
        # Setup mock
        mock_client = MagicMock()
        mock_boto_client.return_value = mock_client
        
        mock_response = {
            'body': MagicMock()
        }
        mock_response['body'].read.return_value = json.dumps({
            'content': [{'text': 'Response'}]
        }).encode()
        
        mock_client.invoke_model.return_value = mock_response
        
        # Call with optional parameters
        call_claude_opus("Test", {
            "temperature": 0.5,
            "max_tokens": 1000,
            "top_p": 0.9,
            "top_k": 50
        })
        
        # Verify parameters were passed
        call_args = mock_client.invoke_model.call_args
        body = json.loads(call_args[1]['body'])
        
        assert body['temperature'] == 0.5
        assert body['max_tokens'] == 1000
        assert body['top_p'] == 0.9
        assert body['top_k'] == 50
