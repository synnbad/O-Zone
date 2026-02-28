/**
 * Type Definitions
 * 
 * TypeScript interfaces matching backend API contracts.
 */

// Location Types
export interface Location {
  id: string;
  name: string;
  country: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  providers: string[];
}

// AQI Types
export interface AQIData {
  location: Location;
  overall: {
    aqi: number;
    category: string;
    color: string;
    dominant_pollutant: string;
    timestamp: string;
  };
  pollutants: Pollutant[];
  metadata: {
    source: 'api' | 'demo';
  };
}

export interface Pollutant {
  name: string;
  aqi: number;
  category: string;
  color: string;
  value: number;
  unit: string;
}

// Chat Types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  timestamp: string;
  metadata: {
    model: string;
    source: 'bedrock' | 'fallback';
  };
}

// Recommendation Types
export interface Recommendation {
  safety_assessment: 'Safe' | 'Moderate Risk' | 'Unsafe';
  recommendation_text: string;
  precautions: string[];
  time_windows: TimeWindow[];
  reasoning: string;
  metadata: {
    source: 'ai' | 'rule-based';
    location: string;
    current_aqi: number;
  };
}

export interface TimeWindow {
  start_time: string;
  end_time: string;
  expected_aqi_range: [number, number];
  confidence: string;
}

// Map Types
export interface Station {
  id: string;
  name: string;
  country: string;
  coordinates: {
    latitude: number;
    longitude: number;
  };
  current_aqi: number | null;
  aqi_category: string | null;
  aqi_color: string | null;
  last_updated: string | null;
}
