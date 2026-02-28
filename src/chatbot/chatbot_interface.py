"""
Chatbot Interface Module

Provides CLI and web-based chat interface for the O-Zone Chatbot.
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import logging
from typing import Optional

from src.chatbot.session_manager import create_session, get_session
from src.chatbot.conversation_manager import process_user_input
from src.chatbot.chatbot_config import ChatbotConfig

logger = logging.getLogger(__name__)


class ChatbotInterface:
    """Main interface for O-Zone Chatbot"""
    
    def __init__(self):
        """Initialize chatbot interface"""
        self.current_session_id: Optional[str] = None
        logger.info("Chatbot interface initialized")
    
    def start_session(self) -> str:
        """
        Starts a new chatbot session.
        
        Returns:
            Session ID
        """
        session = create_session()
        self.current_session_id = session.session_id
        logger.info(f"Started new session: {self.current_session_id}")
        return self.current_session_id
    
    def send_message(self, message: str, session_id: Optional[str] = None) -> str:
        """
        Sends a message to the chatbot.
        
        Args:
            message: User message
            session_id: Optional session ID (uses current session if not provided)
            
        Returns:
            Bot response
        """
        if session_id is None:
            session_id = self.current_session_id
        
        if session_id is None:
            # Start new session if none exists
            session_id = self.start_session()
        
        # Validate and sanitize input
        message = message.strip()
        if not message:
            return "Please enter a message."
        
        # Check for special commands
        if message.lower() in ["/help", "help"]:
            return self._get_help_message()
        elif message.lower() in ["/restart", "restart"]:
            self.start_session()
            return "Starting a new conversation..."
        
        # Process message
        try:
            response = process_user_input(session_id, message)
            return response
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return "I encountered an error. Please try again or type /restart to start over."
    
    def _get_help_message(self) -> str:
        """Returns help message"""
        return """O-Zone Chatbot Help:

I can help you with:
- Checking air quality for your location
- Getting personalized recommendations for outdoor activities
- Finding the best time windows for your activity
- Viewing air quality trends

Commands:
- /help - Show this help message
- /restart - Start a new conversation

Just chat with me naturally and I'll guide you through the process!"""
    
    def run_cli(self):
        """Runs the chatbot in CLI mode"""
        print("=" * 60)
        print("O-Zone Air Quality Chatbot")
        print("=" * 60)
        print("Type 'exit' or 'quit' to end the conversation")
        print("Type '/help' for help")
        print("=" * 60)
        print()
        
        # Start session and get greeting
        session_id = self.start_session()
        greeting = process_user_input(session_id, "")
        print(f"Bot: {greeting}\n")
        
        # Main conversation loop
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                    print("\nBot: Thank you for using O-Zone! Stay safe and breathe easy!")
                    break
                
                response = self.send_message(user_input, session_id)
                print(f"\nBot: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nBot: Goodbye!")
                break
            except Exception as e:
                logger.error(f"CLI error: {e}", exc_info=True)
                print(f"\nBot: I encountered an error. Please try again.\n")


def main():
    """Main entry point for CLI chatbot"""
    # Configure logging
    from src.chatbot.logging_config import setup_chatbot_logging, get_log_level_from_env, get_log_file_from_env
    
    setup_chatbot_logging(
        log_level=get_log_level_from_env(),
        log_file=get_log_file_from_env()
    )
    
    try:
        # Validate configuration
        ChatbotConfig.validate()
        
        # Start chatbot interface
        interface = ChatbotInterface()
        interface.run_cli()
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nConfiguration Error: {e}")
        print("Please check your environment variables and try again.")
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        print(f"\nStartup Error: {e}")


if __name__ == "__main__":
    main()
