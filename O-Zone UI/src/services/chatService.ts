/**
 * Chat Service
 * 
 * Handles chatbot interactions.
 */

import apiClient from '../api/client';
import { ChatMessage, ChatResponse } from '../types';

export const chatService = {
  /**
   * Send a message to the chatbot
   */
  async sendMessage(
    message: string,
    sessionId?: string,
    context?: any
  ): Promise<ChatResponse> {
    const response = await apiClient.post('/api/chat', {
      message,
      session_id: sessionId,
      context
    });
    return response.data;
  }
};
