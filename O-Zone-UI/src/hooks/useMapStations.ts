/**
 * useMapStations Hook
 * 
 * Fetches monitoring stations for map.
 */

import { useState, useEffect } from 'react';
import { mapService } from '../services/mapService';
import { Station } from '../types';

export function useMapStations(bounds?: {
  north: number;
  south: number;
  east: number;
  west: number;
}) {
  const [stations, setStations] = useState<Station[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStations = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await mapService.getMapStations(bounds);
        setStations(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch stations');
        setStations([]);
      } finally {
        setLoading(false);
      }
    };

    fetchStations();
  }, [bounds?.north, bounds?.south, bounds?.east, bounds?.west]);

  return { stations, loading, error };
}
