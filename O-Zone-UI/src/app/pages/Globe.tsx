import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, Globe as GlobeIcon, MapPin } from "lucide-react";

export function Globe() {
  const navigate = useNavigate();
  const [selectedRegion, setSelectedRegion] = useState("North America");

  const globalData = [
    { city: "San Francisco", country: "USA", aqi: 45, lat: 37, lng: -122 },
    { city: "Los Angeles", country: "USA", aqi: 95, lat: 34, lng: -118 },
    { city: "New York", country: "USA", aqi: 62, lat: 40, lng: -74 },
    { city: "London", country: "UK", aqi: 58, lat: 51, lng: 0 },
    { city: "Paris", country: "France", aqi: 52, lat: 48, lng: 2 },
    { city: "Tokyo", country: "Japan", aqi: 48, lat: 35, lng: 139 },
    { city: "Beijing", country: "China", aqi: 156, lat: 39, lng: 116 },
    { city: "New Delhi", country: "India", aqi: 168, lat: 28, lng: 77 },
    { city: "Sydney", country: "Australia", aqi: 32, lat: -33, lng: 151 },
    { city: "São Paulo", country: "Brazil", aqi: 72, lat: -23, lng: -46 },
  ];

  const getAQIColor = (aqi: number) => {
    if (aqi <= 50) return "bg-green-500";
    if (aqi <= 100) return "bg-yellow-500";
    if (aqi <= 150) return "bg-orange-500";
    return "bg-red-500";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-500 to-purple-500 text-white p-4">
        <div className="flex items-center gap-3 mb-4">
          <button onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl">Real-Time Global AQI</h1>
            <p className="text-sm opacity-90">Air quality around the world</p>
          </div>
        </div>
      </header>

      <div className="p-4">
        {/* Globe Visualization */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <GlobeIcon className="w-6 h-6 text-blue-500" />
              <h2 className="text-xl">World Map</h2>
            </div>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option>North America</option>
              <option>Europe</option>
              <option>Asia</option>
              <option>South America</option>
              <option>Oceania</option>
              <option>All Regions</option>
            </select>
          </div>

          {/* Globe Visual */}
          <div className="bg-gradient-to-br from-blue-100 via-green-50 to-blue-100 rounded-xl h-64 flex items-center justify-center relative overflow-hidden">
            <div className="absolute inset-0 opacity-20">
              <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-300 rounded-full blur-3xl"></div>
              <div className="absolute bottom-1/4 right-1/4 w-32 h-32 bg-green-300 rounded-full blur-3xl"></div>
            </div>
            
            {/* Sample cities plotted */}
            {globalData.slice(0, 6).map((city, idx) => (
              <div
                key={city.city}
                className="absolute"
                style={{
                  left: `${15 + idx * 13}%`,
                  top: `${20 + (idx % 3) * 25}%`,
                }}
              >
                <div className={`w-10 h-10 rounded-full ${getAQIColor(city.aqi)} flex items-center justify-center text-white text-xs shadow-lg cursor-pointer hover:scale-110 transition-transform`}>
                  {city.aqi}
                </div>
              </div>
            ))}
            
            <div className="text-gray-400 z-10">
              <GlobeIcon className="w-24 h-24 opacity-30" />
            </div>
          </div>
        </div>

        {/* City List */}
        <div className="bg-white rounded-2xl shadow-lg p-4">
          <h3 className="text-lg mb-3 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-blue-500" />
            Major Cities
          </h3>
          <div className="space-y-2">
            {globalData.map((city) => (
              <div
                key={city.city}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-12 h-12 rounded-full ${getAQIColor(city.aqi)} flex items-center justify-center text-white`}>
                    {city.aqi}
                  </div>
                  <div>
                    <div className="text-sm">{city.city}</div>
                    <div className="text-xs text-gray-500">{city.country}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-500">
                    {city.aqi <= 50
                      ? "Good"
                      : city.aqi <= 100
                      ? "Moderate"
                      : city.aqi <= 150
                      ? "Unhealthy"
                      : "Very Unhealthy"}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
