/**
 * Recommendation Service
 * 
 * Handles activity recommendations.
 */

import apiClient from '../api/client';
import { Recommendation } from '../types';

export const recommendationService = {
  /**
   * Get activity recommendations
   */
  async getRecommendations(
    location: string,
    activity: string,
    health: string = 'None'
  ): Promise<Recommendation> {
    const response = await apiClient.get('/api/recommendations', {
      params: { location, activity, health }
    });
    return response.data;
  }
};
