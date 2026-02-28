import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, Home, Wind, Droplets, Thermometer, Fan } from "lucide-react";

export function CleanRoom() {
  const navigate = useNavigate();
  const [selectedRoom, setSelectedRoom] = useState("Living Room");

  const rooms = {
    "Living Room": {
      aqi: 18,
      temperature: 22,
      humidity: 45,
      pm25: 4.2,
      devices: ["Air Purifier", "Smart Thermostat"],
      status: "excellent",
    },
    "Bedroom": {
      aqi: 22,
      temperature: 20,
      humidity: 50,
      pm25: 5.8,
      devices: ["Air Purifier"],
      status: "good",
    },
    "Kitchen": {
      aqi: 35,
      temperature: 24,
      humidity: 55,
      pm25: 9.2,
      devices: ["Range Hood"],
      status: "moderate",
    },
    "Home Office": {
      aqi: 15,
      temperature: 21,
      humidity: 48,
      pm25: 3.5,
      devices: ["Air Purifier", "Dehumidifier"],
      status: "excellent",
    },
  };

  const currentRoom = rooms[selectedRoom as keyof typeof rooms];

  const getStatusColor = (status: string) => {
    if (status === "excellent") return "bg-green-500";
    if (status === "good") return "bg-blue-500";
    return "bg-yellow-500";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-orange-500 text-white p-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl">Clean Room Monitor</h1>
            <p className="text-sm opacity-90">Indoor air quality</p>
          </div>
        </div>
      </header>

      <div className="p-4">
        {/* Room Selector */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <Home className="w-5 h-5 text-orange-500" />
            <h3 className="text-lg">Select Room</h3>
          </div>
          <select
            value={selectedRoom}
            onChange={(e) => setSelectedRoom(e.target.value)}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            {Object.keys(rooms).map((room) => (
              <option key={room} value={room}>
                {room}
              </option>
            ))}
          </select>
        </div>

        {/* Current Status */}
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-4">
          <div className="text-center mb-6">
            <div className={`w-24 h-24 mx-auto rounded-full ${getStatusColor(currentRoom.status)} flex items-center justify-center mb-3`}>
              <div className="text-white">
                <div className="text-3xl">{currentRoom.aqi}</div>
                <div className="text-xs">AQI</div>
              </div>
            </div>
            <h3 className="text-xl capitalize">{currentRoom.status}</h3>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Thermometer className="w-5 h-5 text-blue-500" />
                <span className="text-xs text-gray-600">Temperature</span>
              </div>
              <div className="text-2xl text-blue-600">{currentRoom.temperature}°C</div>
            </div>

            <div className="bg-cyan-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Droplets className="w-5 h-5 text-cyan-500" />
                <span className="text-xs text-gray-600">Humidity</span>
              </div>
              <div className="text-2xl text-cyan-600">{currentRoom.humidity}%</div>
            </div>

            <div className="bg-orange-50 rounded-lg p-4 col-span-2">
              <div className="flex items-center gap-2 mb-2">
                <Wind className="w-5 h-5 text-orange-500" />
                <span className="text-xs text-gray-600">PM2.5 Level</span>
              </div>
              <div className="text-2xl text-orange-600">{currentRoom.pm25} µg/m³</div>
            </div>
          </div>
        </div>

        {/* Active Devices */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-4">
            <Fan className="w-5 h-5 text-orange-500" />
            <h3 className="text-lg">Active Devices</h3>
          </div>
          <div className="space-y-3">
            {currentRoom.devices.map((device) => (
              <div key={device} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                    <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  </div>
                  <div>
                    <div className="text-sm">{device}</div>
                    <div className="text-xs text-gray-500">Running</div>
                  </div>
                </div>
                <button className="px-3 py-1 bg-orange-500 text-white text-xs rounded-full">
                  Control
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-gradient-to-r from-orange-100 to-yellow-100 rounded-2xl p-4 border-2 border-orange-200">
          <h3 className="text-lg mb-3">💡 Recommendations</h3>
          <div className="space-y-2 text-sm">
            {currentRoom.status === "excellent" && (
              <>
                <p>✅ Air quality is excellent!</p>
                <p>✅ Continue current ventilation settings</p>
              </>
            )}
            {currentRoom.status === "good" && (
              <>
                <p>✅ Air quality is good</p>
                <p>💡 Consider running air purifier for 30 minutes</p>
              </>
            )}
            {currentRoom.status === "moderate" && (
              <>
                <p>⚠️ Air quality could be improved</p>
                <p>💡 Run air purifier on high setting</p>
                <p>💡 Increase ventilation if weather permits</p>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
