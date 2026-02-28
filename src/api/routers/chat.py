"""
Chat Router

Handles chatbot interactions with session management.
"""

import sys
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, UTC
import logging

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.chatbot import create_session, get_session, process_user_input
from src.api.session import session_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    session_id: Optional[str] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    session_id: str
    timestamp: str
    metadata: dict


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to the chatbot.
    
    Args:
        request: Chat request with message and optional session_id
        
    Returns:
        Bot response with session_id for continuity
    """
    try:
        logger.info(f"Chat request: session_id={request.session_id}, message={request.message[:50]}...")
        
        # Get or create session
        if request.session_id:
            # Try to get existing session
            chatbot_session = get_session(request.session_id)
            if not chatbot_session:
                # Session expired or not found, create new one
                logger.info(f"Session {request.session_id} not found, creating new session")
                chatbot_session = create_session()
                session_id = chatbot_session.session_id
            else:
                session_id = request.session_id
        else:
            # Create new session
            chatbot_session = create_session()
            session_id = chatbot_session.session_id
            logger.info(f"Created new chat session: {session_id}")
        
        # Process user input through chatbot
        bot_response = process_user_input(session_id, request.message)
        
        # Determine if using AI or fallback
        # Check if AWS Bedrock is configured
        import os
        has_bedrock = bool(os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'))
        source = "bedrock" if has_bedrock else "fallback"
        
        return ChatResponse(
            response=bot_response,
            session_id=session_id,
            timestamp=datetime.now(UTC).isoformat(),
            metadata={
                "model": "claude-opus-4.6" if has_bedrock else "rule-based",
                "source": source
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")
