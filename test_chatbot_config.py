"""
Test script to verify chatbot configuration validation.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from chatbot.chatbot_config import ChatbotConfig
from chatbot.logging_config import setup_chatbot_logging

def test_config_validation():
    """Test configuration validation"""
    print("Testing chatbot configuration validation...")
    
    # Setup logging
    setup_chatbot_logging(log_level="INFO")
    
    try:
        # This should validate all required environment variables
        ChatbotConfig.validate()
        print("✓ Configuration validation passed!")
        return True
    except ValueError as e:
        print(f"✗ Configuration validation failed (expected if env vars not set):")
        print(f"  {e}")
        return False

def test_config_values():
    """Test configuration values"""
    print("\nTesting configuration values...")
    
    print(f"✓ Session TTL: {ChatbotConfig.SESSION_TTL_MINUTES} minutes")
    print(f"✓ Max conversation history: {ChatbotConfig.MAX_CONVERSATION_HISTORY} messages")
    print(f"✓ Activity options: {len(ChatbotConfig.ACTIVITY_OPTIONS)} options")
    print(f"✓ Health sensitivity options: {len(ChatbotConfig.HEALTH_SENSITIVITY_OPTIONS)} options")
    
    # Test formatted options
    activity_text = ChatbotConfig.get_activity_options_text()
    health_text = ChatbotConfig.get_health_options_text()
    
    print(f"✓ Activity options formatted: {len(activity_text)} chars")
    print(f"✓ Health options formatted: {len(health_text)} chars")
    
    return True

def test_session_creation():
    """Test session creation"""
    print("\nTesting session creation...")
    
    from chatbot.session_manager import create_session, get_session
    
    # Create a session
    session = create_session()
    print(f"✓ Created session: {session.session_id}")
    
    # Retrieve the session
    retrieved = get_session(session.session_id)
    if retrieved and retrieved.session_id == session.session_id:
        print(f"✓ Retrieved session successfully")
        return True
    else:
        print(f"✗ Failed to retrieve session")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("O-Zone Chatbot Configuration Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Config Values", test_config_values()))
    results.append(("Session Creation", test_session_creation()))
    results.append(("Config Validation", test_config_validation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nPassed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print(f"\n✗ {total_count - passed_count} test(s) failed")
        sys.exit(1)
