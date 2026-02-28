import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, Shield, User, AlertTriangle, Bell } from "lucide-react";

export function Safety() {
  const navigate = useNavigate();
  const [monitoredPeople, setMonitoredPeople] = useState([
    {
      id: 1,
      name: "Emma (Child, 8)",
      location: "School - Playground",
      aqi: 52,
      status: "caution",
      alerts: ["Moderate AQI detected"],
    },
    {
      id: 2,
      name: "Grandma Rose (72)",
      location: "Home - Garden",
      aqi: 45,
      status: "safe",
      alerts: [],
    },
    {
      id: 3,
      name: "Tommy (Child, 5)",
      location: "Daycare Center",
      aqi: 68,
      status: "warning",
      alerts: ["Unhealthy for sensitive groups", "High pollen count"],
    },
  ]);

  const getStatusColor = (status: string) => {
    if (status === "safe") return "bg-green-100 border-green-500 text-green-800";
    if (status === "caution") return "bg-yellow-100 border-yellow-500 text-yellow-800";
    return "bg-red-100 border-red-500 text-red-800";
  };

  const getStatusIcon = (status: string) => {
    if (status === "safe") return "✅";
    if (status === "caution") return "⚠️";
    return "🚨";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-red-500 text-white p-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl">Child / Elder Safety</h1>
            <p className="text-sm opacity-90">Monitor vulnerable family members</p>
          </div>
          <button className="relative">
            <Bell className="w-6 h-6" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full text-xs flex items-center justify-center text-black">
              2
            </span>
          </button>
        </div>
      </header>

      <div className="p-4">
        {/* Alert Summary */}
        <div className="bg-gradient-to-r from-red-100 to-orange-100 rounded-2xl border-2 border-red-300 p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h3 className="text-lg text-red-800">Active Alerts</h3>
          </div>
          <p className="text-sm text-red-700">
            2 people need attention due to elevated air quality levels
          </p>
        </div>

        {/* Monitored People */}
        <div className="space-y-4">
          {monitoredPeople.map((person) => (
            <div key={person.id} className={`rounded-2xl border-2 p-4 ${getStatusColor(person.status)}`}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white bg-opacity-50 rounded-full flex items-center justify-center">
                    <User className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="text-lg">{person.name}</h3>
                    <p className="text-xs opacity-75">{person.location}</p>
                  </div>
                </div>
                <div className="text-2xl">{getStatusIcon(person.status)}</div>
              </div>

              <div className="flex items-center justify-between mb-3 pb-3 border-b border-current border-opacity-20">
                <div>
                  <div className="text-xs opacity-75">Current AQI</div>
                  <div className="text-2xl">{person.aqi}</div>
                </div>
                <div className="text-right">
                  <div className="text-xs opacity-75">Status</div>
                  <div className="capitalize">{person.status}</div>
                </div>
              </div>

              {person.alerts.length > 0 && (
                <div className="space-y-2">
                  <div className="text-xs opacity-75">Active Alerts:</div>
                  {person.alerts.map((alert, idx) => (
                    <div key={idx} className="text-sm flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4" />
                      {alert}
                    </div>
                  ))}
                </div>
              )}

              {person.status === "safe" && (
                <div className="text-sm">
                  ✅ Air quality is safe. No action needed.
                </div>
              )}

              {person.status !== "safe" && (
                <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                  <div className="text-xs opacity-75 mb-2">Recommendations:</div>
                  <div className="space-y-1 text-sm">
                    {person.status === "caution" && (
                      <>
                        <p>• Limit outdoor activities to 30 minutes</p>
                        <p>• Take breaks if symptoms occur</p>
                      </>
                    )}
                    {person.status === "warning" && (
                      <>
                        <p>• Move indoors immediately</p>
                        <p>• Contact guardian if symptoms worsen</p>
                        <p>• Keep rescue medication nearby</p>
                      </>
                    )}
                  </div>
                </div>
              )}

              <div className="mt-3 flex gap-2">
                <button className="flex-1 bg-white bg-opacity-50 py-2 rounded-lg text-sm hover:bg-opacity-70">
                  View Location
                </button>
                <button className="flex-1 bg-white bg-opacity-50 py-2 rounded-lg text-sm hover:bg-opacity-70">
                  Send Alert
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Add Person Button */}
        <button className="w-full mt-4 bg-white rounded-2xl shadow-lg p-4 flex items-center justify-center gap-2 text-red-500 hover:bg-red-50">
          <Shield className="w-5 h-5" />
          <span>Add Person to Monitor</span>
        </button>
      </div>
    </div>
  );
}
