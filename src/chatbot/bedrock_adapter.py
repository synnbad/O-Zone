"""
Bedrock Adapter Module

Interfaces with Amazon Bedrock for adaptive communication using Claude Opus 4.6.
Provides adaptive response generation with user profile context, retry logic, and error handling.
"""

import boto3
import json
import logging
import time
from typing import Optional

from .session_manager import UserProfile

logger = logging.getLogger(__name__)


def generate_adaptive_response(prompt: str, user_profile: UserProfile, context: dict) -> str:
    """
    Generates adaptive response using Claude Opus 4.6 via Bedrock.
    
    Constructs a prompt with user profile information and communication style instructions,
    then calls Claude Opus 4.6 to generate an adaptive response. Falls back to a generic
    message if the call fails.
    
    Args:
        prompt: Base prompt text
        user_profile: User profile for communication adaptation
        context: Additional context data (AQI, location, activity, etc.)
        
    Returns:
        Generated adaptive response text
    """
    full_prompt = construct_adaptive_prompt(prompt, user_profile, context)
    
    try:
        response = call_claude_opus(full_prompt, {
            "temperature": 0.7,
            "max_tokens": 500
        })
        return response
    except Exception as e:
        logger.error(f"Bedrock adapter error: {e}")
        # Fail gracefully - return a generic message
        return "I'm having trouble generating a response right now. Please try again in a moment."


def construct_adaptive_prompt(base_prompt: str, user_profile: UserProfile, context: dict) -> str:
    """
    Constructs prompt with user profile context and communication style instructions.
    
    Adds user demographic information (age, education, technical expertise) and
    communication preferences to the base prompt, along with specific instructions
    for adapting vocabulary level, sentence complexity, and explanation depth.
    
    Args:
        base_prompt: Base prompt text
        user_profile: User profile with demographic and preference information
        context: Additional context data to include in prompt
        
    Returns:
        Complete prompt with profile context and style instructions
    """
    prompt_parts = [base_prompt, "\n\n--- User Profile ---"]
    
    # Add user profile information
    if user_profile.age_group:
        prompt_parts.append(f"Age group: {user_profile.age_group}")
    
    if user_profile.education_level:
        prompt_parts.append(f"Education level: {user_profile.education_level}")
    
    if user_profile.technical_expertise:
        prompt_parts.append(f"Technical expertise: {user_profile.technical_expertise}")
    
    if user_profile.communication_preference:
        prompt_parts.append(f"Communication preference: {user_profile.communication_preference}")
    
    if user_profile.occupation_category:
        prompt_parts.append(f"Occupation category: {user_profile.occupation_category}")
    
    # Add communication style instructions
    prompt_parts.append("\n--- Communication Style Instructions ---")
    prompt_parts.append("Please adapt your response to match the user's profile:")
    
    # Vocabulary level instructions
    if user_profile.education_level == "basic" or user_profile.age_group == "child":
        prompt_parts.append("- Use simple, everyday vocabulary (avoid technical jargon)")
        prompt_parts.append("- Use short, clear sentences")
        prompt_parts.append("- Explain concepts in simple terms")
    elif user_profile.technical_expertise in ["expert", "intermediate"] or \
         user_profile.occupation_category in ["environmental_scientist", "health_professional"]:
        prompt_parts.append("- Include technical details and scientific terminology")
        prompt_parts.append("- Provide pollutant concentrations and measurements")
        prompt_parts.append("- Reference scientific concepts where relevant")
    else:
        prompt_parts.append("- Use standard vocabulary with occasional technical terms")
        prompt_parts.append("- Balance accessibility with accuracy")
    
    # Detail level instructions
    if user_profile.communication_preference == "concise":
        prompt_parts.append("- Be brief and to the point")
        prompt_parts.append("- Provide key information without extensive elaboration")
        prompt_parts.append("- Use bullet points for clarity")
    elif user_profile.communication_preference == "detailed":
        prompt_parts.append("- Provide comprehensive explanations with context")
        prompt_parts.append("- Include background information and reasoning")
        prompt_parts.append("- Explain the 'why' behind recommendations")
    else:
        prompt_parts.append("- Provide moderate detail - enough context without overwhelming")
    
    # Add context data
    if context:
        prompt_parts.append("\n--- Context Data ---")
        for key, value in context.items():
            prompt_parts.append(f"{key}: {value}")
    
    return "\n".join(prompt_parts)


def call_claude_opus(prompt: str, parameters: dict) -> str:
    """
    Calls Claude Opus 4.6 via Amazon Bedrock with authentication, retry logic, and error handling.
    
    Authenticates with AWS Bedrock using credentials from environment/config, invokes
    Claude Opus 4.6 model, and implements retry logic for transient failures. Falls back
    gracefully if AWS credentials are not configured.
    
    Args:
        prompt: Complete prompt text
        parameters: Model parameters (temperature, max_tokens, etc.)
        
    Returns:
        Model response text
        
    Raises:
        Exception: If Bedrock call fails after retries or credentials are invalid
    """
    # Import config to check AWS credentials
    try:
        from src.config import Config
    except ImportError:
        # If config not available, check environment variables directly
        import os
        class Config:
            AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
            AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
            AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN')
            AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
            BEDROCK_MODEL_ID = os.getenv('BEDROCK_MODEL_ID', 'anthropic.claude-opus-4-6-20250514')
    
    # Check if AWS credentials are configured
    if not Config.AWS_ACCESS_KEY_ID or not Config.AWS_SECRET_ACCESS_KEY:
        logger.warning("AWS credentials not configured - cannot call Claude Opus")
        raise Exception("AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
    
    # Retry configuration
    max_retries = 3
    retry_delay = 1  # seconds
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Initialize Bedrock client with credentials
            client_kwargs = {
                'service_name': 'bedrock-runtime',
                'region_name': Config.AWS_REGION,
                'aws_access_key_id': Config.AWS_ACCESS_KEY_ID,
                'aws_secret_access_key': Config.AWS_SECRET_ACCESS_KEY,
            }
            
            # Add session token if present (for temporary credentials)
            if hasattr(Config, 'AWS_SESSION_TOKEN') and Config.AWS_SESSION_TOKEN:
                client_kwargs['aws_session_token'] = Config.AWS_SESSION_TOKEN
            
            bedrock = boto3.client(**client_kwargs)
            
            # Prepare request body for Claude Opus 4.6
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": parameters.get("max_tokens", 500),
                "temperature": parameters.get("temperature", 0.7),
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Add optional parameters if provided
            if "top_p" in parameters:
                request_body["top_p"] = parameters["top_p"]
            if "top_k" in parameters:
                request_body["top_k"] = parameters["top_k"]
            
            logger.info(f"Calling Claude Opus 4.6 (attempt {attempt + 1}/{max_retries})")
            
            # Invoke model
            response = bedrock.invoke_model(
                modelId=Config.BEDROCK_MODEL_ID,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text from Claude response
            if 'content' in response_body and len(response_body['content']) > 0:
                response_text = response_body['content'][0]['text']
                logger.info("Successfully received response from Claude Opus 4.6")
                return response_text
            else:
                raise Exception("Invalid response format from Bedrock - no content field")
        
        except Exception as e:
            last_error = e
            logger.warning(f"Bedrock call attempt {attempt + 1} failed: {e}")
            
            # Don't retry on authentication errors
            if "credentials" in str(e).lower() or "unauthorized" in str(e).lower():
                logger.error(f"Authentication error - not retrying: {e}")
                raise Exception(f"Bedrock authentication failed: {str(e)}")
            
            # Retry on transient errors
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error(f"All {max_retries} attempts failed")
    
    # All retries exhausted
    raise Exception(f"Bedrock API call failed after {max_retries} attempts: {str(last_error)}")
