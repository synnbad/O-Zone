/**
 * useLocationSearch Hook
 * 
 * Handles location search with debouncing.
 */

import { useState, useEffect } from 'react';
import { locationService } from '../services/locationService';
import { Location } from '../types';

export function useLocationSearch(query: string, debounceMs: number = 500) {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query || query.length < 2) {
      setLocations([]);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      setError(null);

      try {
        const results = await locationService.searchLocations(query);
        setLocations(results);
      } catch (err: any) {
        setError(err.message || 'Failed to search locations');
        setLocations([]);
      } finally {
        setLoading(false);
      }
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs]);

  return { locations, loading, error };
}
