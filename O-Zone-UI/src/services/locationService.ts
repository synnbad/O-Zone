/**
 * Location Service
 * 
 * Handles location search and AQI data retrieval.
 */

import apiClient from '../api/client';
import { Location, AQIData } from '../types';

export const locationService = {
  /**
   * Search for locations by name or coordinates
   */
  async searchLocations(query: string): Promise<Location[]> {
    const response = await apiClient.get('/api/locations/search', {
      params: { q: query }
    });
    return response.data.results;
  },

  /**
   * Get current AQI data for a location
   */
  async getLocationAQI(locationId: string): Promise<AQIData> {
    const response = await apiClient.get(`/api/locations/${locationId}/aqi`);
    return response.data;
  }
};
