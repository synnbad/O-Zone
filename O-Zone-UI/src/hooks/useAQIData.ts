/**
 * useAQIData Hook
 * 
 * Fetches AQI data for a location with auto-refresh.
 */

import { useState, useEffect } from 'react';
import { locationService } from '../services/locationService';
import { AQIData } from '../types';

export function useAQIData(locationId: string | null, refreshInterval: number = 300000) {
  const [aqiData, setAqiData] = useState<AQIData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!locationId) {
      setAqiData(null);
      return;
    }

    const fetchAQI = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await locationService.getLocationAQI(locationId);
        setAqiData(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch AQI data');
        setAqiData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchAQI();

    // Auto-refresh
    const interval = setInterval(fetchAQI, refreshInterval);

    return () => clearInterval(interval);
  }, [locationId, refreshInterval]);

  return { aqiData, loading, error };
}
