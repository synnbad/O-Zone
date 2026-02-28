"""Quick test to verify chatbot runs"""
import sys
import os

# Add to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.chatbot.session_manager import create_session
from src.chatbot.conversation_manager import process_user_input

# Create a session
session = create_session()
print(f"✓ Session created: {session.session_id}")

# Test greeting
response = process_user_input(session.session_id, "Hello")
print(f"\n✓ Chatbot responded to greeting:")
print(f"  {response[:100]}...")

# Test location
response = process_user_input(session.session_id, "San Francisco")
print(f"\n✓ Chatbot responded to location:")
print(f"  {response[:100]}...")

print("\n✅ Chatbot is working! You can now run:")
print("   python src/chatbot/chatbot_interface.py")
