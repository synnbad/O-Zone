/**
 * useChat Hook
 * 
 * Manages chat session and message history.
 */

import { useState, useEffect } from 'react';
import { chatService } from '../services/chatService';
import { ChatMessage } from '../types';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load session ID from localStorage
  useEffect(() => {
    const savedSessionId = localStorage.getItem('chat_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
    }
  }, []);

  // Save session ID to localStorage
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem('chat_session_id', sessionId);
    }
  }, [sessionId]);

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);

    setLoading(true);
    setError(null);

    try {
      const response = await chatService.sendMessage(content, sessionId || undefined);
      
      // Update session ID
      setSessionId(response.session_id);

      // Add bot message
      const botMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (err: any) {
      setError(err.message || 'Failed to send message');
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setSessionId(null);
    localStorage.removeItem('chat_session_id');
  };

  return { messages, sendMessage, loading, error, clearChat };
}
