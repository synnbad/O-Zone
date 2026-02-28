/**
 * Map Service
 * 
 * Handles map station data.
 */

import apiClient from '../api/client';
import { Station } from '../types';

export const mapService = {
  /**
   * Get monitoring stations for map
   */
  async getMapStations(bounds?: {
    north: number;
    south: number;
    east: number;
    west: number;
  }): Promise<Station[]> {
    const response = await apiClient.get('/api/stations/map', {
      params: bounds
    });
    return response.data.stations;
  }
};
