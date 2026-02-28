/**
 * useRecommendations Hook
 * 
 * Fetches activity recommendations.
 */

import { useState, useEffect } from 'react';
import { recommendationService } from '../services/recommendationService';
import { Recommendation } from '../types';

export function useRecommendations(
  location: string | null,
  activity: string | null,
  health: string = 'None'
) {
  const [recommendation, setRecommendation] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!location || !activity) {
      setRecommendation(null);
      return;
    }

    const fetchRecommendation = async () => {
      setLoading(true);
      setError(null);

      try {
        const data = await recommendationService.getRecommendations(location, activity, health);
        setRecommendation(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch recommendations');
        setRecommendation(null);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendation();
  }, [location, activity, health]);

  return { recommendation, loading, error };
}
