import { useState } from "react";
import { useNavigate } from "react-router";
import { useUser } from "../context/UserContext";
import {
  MapPin,
  Wind,
  Activity,
  TrendingUp,
  Home,
  MessageCircle,
  Bell,
  Menu,
  Shield,
  Filter,
  Globe,
} from "lucide-react";

export function Dashboard() {
  const navigate = useNavigate();
  const { profile } = useUser();
  const [selectedLocation, setSelectedLocation] = useState("San Francisco, CA");

  const locations = [
    { name: "San Francisco, CA", aqi: 45, lat: 37.7749, lng: -122.4194 },
    { name: "Los Angeles, CA", aqi: 95, lat: 34.0522, lng: -118.2437 },
    { name: "New York, NY", aqi: 62, lat: 40.7128, lng: -74.006 },
    { name: "Seattle, WA", aqi: 28, lat: 47.6062, lng: -122.3321 },
  ];

  const currentLocation = locations.find((l) => l.name === selectedLocation) || locations[0];

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return "bg-green-500";
    if (aqi <= 100) return "bg-yellow-500";
    if (aqi <= 150) return "bg-orange-500";
    return "bg-red-500";
  };

  const getAQILevel = (aqi: number) => {
    if (aqi <= 50) return "Good";
    if (aqi <= 100) return "Moderate";
    if (aqi <= 150) return "Unhealthy for Sensitive";
    return "Unhealthy";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-500 text-white p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Menu className="w-6 h-6" />
            <h1 className="text-xl">O-Zone</h1>
          </div>
          <button onClick={() => navigate("/notifications")}>
            <Bell className="w-6 h-6" />
          </button>
        </div>
        
        {profile && (
          <div className="bg-blue-400 bg-opacity-50 rounded-lg p-3 mb-3">
            <p className="text-sm">Welcome back, {profile.name}!</p>
            <p className="text-xs opacity-90">
              {profile.hasAsthma && "🫁 Asthma "} 
              {profile.hasAllergies && "🤧 Allergies "}
              Sensitivity: {profile.sensitivityLevel}
            </p>
          </div>
        )}

        <div className="flex items-center gap-2">
          <MapPin className="w-5 h-5" />
          <select
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="flex-1 bg-white bg-opacity-20 border border-white border-opacity-30 rounded-lg px-3 py-2 text-white focus:outline-none"
          >
            {locations.map((loc) => (
              <option key={loc.name} value={loc.name} className="text-gray-900">
                {loc.name}
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* AQI Display */}
      <div className="p-4">
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-4">
          <div className="text-center">
            <div className={`w-32 h-32 mx-auto rounded-full ${getAQIColor(currentLocation.aqi)} flex items-center justify-center mb-4`}>
              <div className="text-white">
                <div className="text-4xl">{currentLocation.aqi}</div>
                <div className="text-sm">AQI</div>
              </div>
            </div>
            <h2 className="text-2xl mb-2">{getAQILevel(currentLocation.aqi)}</h2>
            <p className="text-gray-600 text-sm">
              {currentLocation.aqi <= 50
                ? "Great day for outdoor activities!"
                : currentLocation.aqi <= 100
                ? "Acceptable for most people"
                : "Sensitive groups should limit outdoor activities"}
            </p>
          </div>
        </div>

        {/* Map Preview */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
          <h3 className="text-lg mb-3 flex items-center gap-2">
            <MapPin className="w-5 h-5" />
            Air Quality Map
          </h3>
          <div className="bg-gradient-to-br from-blue-100 to-green-100 h-48 rounded-lg flex items-center justify-center relative">
            {locations.map((loc, idx) => (
              <div
                key={loc.name}
                className="absolute"
                style={{
                  left: `${25 + idx * 20}%`,
                  top: `${30 + (idx % 2) * 30}%`,
                }}
              >
                <div className={`w-12 h-12 rounded-full ${getAQIColor(loc.aqi)} flex items-center justify-center text-white text-sm shadow-lg`}>
                  {loc.aqi}
                </div>
              </div>
            ))}
            <div className="text-gray-400 text-sm">Interactive Map View</div>
          </div>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => navigate("/activity")}
            className="bg-white rounded-xl shadow p-4 flex flex-col items-center gap-2 hover:shadow-lg transition-shadow"
          >
            <Activity className="w-8 h-8 text-blue-500" />
            <span className="text-sm">Activity</span>
            <span className="text-xs text-gray-500">Plan Outdoor</span>
          </button>

          <button
            onClick={() => navigate("/globe")}
            className="bg-white rounded-xl shadow p-4 flex flex-col items-center gap-2 hover:shadow-lg transition-shadow"
          >
            <Globe className="w-8 h-8 text-green-500" />
            <span className="text-sm">Real-Time</span>
            <span className="text-xs text-gray-500">Global View</span>
          </button>

          <button
            onClick={() => navigate("/trends")}
            className="bg-white rounded-xl shadow p-4 flex flex-col items-center gap-2 hover:shadow-lg transition-shadow"
          >
            <TrendingUp className="w-8 h-8 text-purple-500" />
            <span className="text-sm">Trends</span>
            <span className="text-xs text-gray-500">History</span>
          </button>

          <button
            onClick={() => navigate("/clean-room")}
            className="bg-white rounded-xl shadow p-4 flex flex-col items-center gap-2 hover:shadow-lg transition-shadow"
          >
            <Home className="w-8 h-8 text-orange-500" />
            <span className="text-sm">Clean Room</span>
            <span className="text-xs text-gray-500">Monitor</span>
          </button>

          <button
            onClick={() => navigate("/chat")}
            className="bg-white rounded-xl shadow p-4 flex flex-col items-center gap-2 hover:shadow-lg transition-shadow"
          >
            <MessageCircle className="w-8 h-8 text-pink-500" />
            <span className="text-sm">Assistant</span>
            <span className="text-xs text-gray-500">Ask AI</span>
          </button>

          <button
            onClick={() => navigate("/safety")}
            className="bg-white rounded-xl shadow p-4 flex flex-col items-center gap-2 hover:shadow-lg transition-shadow"
          >
            <Shield className="w-8 h-8 text-red-500" />
            <span className="text-sm">Safety</span>
            <span className="text-xs text-gray-500">Monitor</span>
          </button>

          <button
            onClick={() => navigate("/pollutants")}
            className="bg-white rounded-xl shadow p-4 flex flex-col items-center gap-2 hover:shadow-lg transition-shadow col-span-2"
          >
            <Filter className="w-8 h-8 text-indigo-500" />
            <span className="text-sm">Pollutants & Locations</span>
            <span className="text-xs text-gray-500">Filter & Details</span>
          </button>
        </div>
      </div>
    </div>
  );
}
