import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, Filter, MapPin, TrendingUp, TrendingDown, Minus } from "lucide-react";

export function Pollutants() {
  const navigate = useNavigate();
  const [selectedFilter, setSelectedFilter] = useState<string | null>(null);

  const pollutantData = [
    {
      name: "PM2.5",
      value: 12.5,
      unit: "µg/m³",
      level: "Good",
      trend: "down",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      name: "PM10",
      value: 24.8,
      unit: "µg/m³",
      level: "Good",
      trend: "stable",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      name: "Ozone (O₃)",
      value: 45.2,
      unit: "ppb",
      level: "Moderate",
      trend: "up",
      color: "text-yellow-600",
      bgColor: "bg-yellow-50",
    },
    {
      name: "NO₂",
      value: 18.5,
      unit: "ppb",
      level: "Good",
      trend: "down",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      name: "CO",
      value: 0.5,
      unit: "ppm",
      level: "Good",
      trend: "stable",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
    {
      name: "SO₂",
      value: 3.2,
      unit: "ppb",
      level: "Good",
      trend: "down",
      color: "text-green-600",
      bgColor: "bg-green-50",
    },
  ];

  const locations = [
    { name: "San Francisco", aqi: 45, distance: "Current" },
    { name: "Oakland", aqi: 52, distance: "8 mi" },
    { name: "San Jose", aqi: 48, distance: "42 mi" },
    { name: "Berkeley", aqi: 50, distance: "10 mi" },
  ];

  const filters = ["Air Quality", "Pollutants", "PM2.5", "Ozone", "NO₂ Warning", "Air Quality Change"];

  const getTrendIcon = (trend: string) => {
    if (trend === "up") return <TrendingUp className="w-4 h-4 text-red-500" />;
    if (trend === "down") return <TrendingDown className="w-4 h-4 text-green-500" />;
    return <Minus className="w-4 h-4 text-gray-500" />;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-indigo-500 text-white p-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl">Pollutants & Locations</h1>
            <p className="text-sm opacity-90">Detailed air quality data</p>
          </div>
        </div>
      </header>

      <div className="p-4">
        {/* Filters */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <Filter className="w-5 h-5 text-indigo-500" />
            <h3 className="text-lg">Filters</h3>
          </div>
          <div className="flex gap-2 overflow-x-auto pb-2">
            {filters.map((filter) => (
              <button
                key={filter}
                onClick={() =>
                  setSelectedFilter(selectedFilter === filter ? null : filter)
                }
                className={`px-4 py-2 rounded-full text-sm whitespace-nowrap ${
                  selectedFilter === filter
                    ? "bg-indigo-500 text-white"
                    : "bg-gray-100 text-gray-700"
                }`}
              >
                {filter}
              </button>
            ))}
          </div>
        </div>

        {/* Pollutants Grid */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
          <h3 className="text-lg mb-4">Current Pollutant Levels</h3>
          <div className="grid grid-cols-2 gap-3">
            {pollutantData.map((pollutant) => (
              <div
                key={pollutant.name}
                className={`rounded-xl p-4 ${pollutant.bgColor}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h4 className={`text-sm ${pollutant.color}`}>{pollutant.name}</h4>
                  {getTrendIcon(pollutant.trend)}
                </div>
                <div className={`text-2xl mb-1 ${pollutant.color}`}>
                  {pollutant.value}
                </div>
                <div className="text-xs text-gray-600 mb-1">{pollutant.unit}</div>
                <div className={`text-xs ${pollutant.color}`}>{pollutant.level}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Nearby Locations */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="w-5 h-5 text-indigo-500" />
            <h3 className="text-lg">Nearby Locations</h3>
          </div>
          <div className="space-y-2">
            {locations.map((location) => (
              <div
                key={location.name}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                    location.aqi <= 50 ? "bg-green-500" : "bg-yellow-500"
                  }`}>
                    <div className="text-white text-sm">{location.aqi}</div>
                  </div>
                  <div>
                    <div className="text-sm">{location.name}</div>
                    <div className="text-xs text-gray-500">{location.distance}</div>
                  </div>
                </div>
                <button className="text-indigo-500 text-sm">View</button>
              </div>
            ))}
          </div>
        </div>

        {/* Air Quality Change Alert */}
        <div className="bg-gradient-to-r from-indigo-100 to-purple-100 rounded-2xl border-2 border-indigo-300 p-4">
          <h3 className="text-lg mb-3">📊 Air Quality Changes</h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-center gap-2">
              <TrendingDown className="w-4 h-4 text-green-500" />
              <span>PM2.5 decreased by 15% from yesterday</span>
            </div>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-yellow-500" />
              <span>Ozone levels rising, peak expected at 3 PM</span>
            </div>
            <div className="flex items-center gap-2">
              <Minus className="w-4 h-4 text-gray-500" />
              <span>Overall AQI stable over the past 24 hours</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
