import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, TrendingUp, Calendar } from "lucide-react";
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

export function Trends() {
  const navigate = useNavigate();
  const [timeRange, setTimeRange] = useState<"day" | "week" | "month">("week");

  const weekData = [
    { date: "Mon", aqi: 42, pm25: 12, pm10: 18 },
    { date: "Tue", aqi: 38, pm25: 10, pm10: 15 },
    { date: "Wed", aqi: 45, pm25: 14, pm10: 20 },
    { date: "Thu", aqi: 52, pm25: 18, pm10: 24 },
    { date: "Fri", aqi: 48, pm25: 15, pm10: 22 },
    { date: "Sat", aqi: 35, pm25: 9, pm10: 14 },
    { date: "Sun", aqi: 40, pm25: 11, pm10: 17 },
  ];

  const monthData = [
    { date: "Week 1", aqi: 45, pm25: 13, pm10: 19 },
    { date: "Week 2", aqi: 52, pm25: 16, pm10: 23 },
    { date: "Week 3", aqi: 48, pm25: 14, pm10: 21 },
    { date: "Week 4", aqi: 42, pm25: 12, pm10: 18 },
  ];

  const dayData = [
    { date: "00:00", aqi: 38 },
    { date: "03:00", aqi: 35 },
    { date: "06:00", aqi: 42 },
    { date: "09:00", aqi: 48 },
    { date: "12:00", aqi: 52 },
    { date: "15:00", aqi: 47 },
    { date: "18:00", aqi: 45 },
    { date: "21:00", aqi: 40 },
  ];

  const getData = () => {
    if (timeRange === "day") return dayData;
    if (timeRange === "week") return weekData;
    return monthData;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-purple-500 text-white p-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl">Trends & History</h1>
            <p className="text-sm opacity-90">Air quality over time</p>
          </div>
        </div>
      </header>

      <div className="p-4">
        {/* Time Range Selector */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <Calendar className="w-5 h-5 text-purple-500" />
            <h3 className="text-lg">Time Range</h3>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => setTimeRange("day")}
              className={`py-2 px-4 rounded-lg text-sm ${
                timeRange === "day"
                  ? "bg-purple-500 text-white"
                  : "bg-gray-100 text-gray-700"
              }`}
            >
              24 Hours
            </button>
            <button
              onClick={() => setTimeRange("week")}
              className={`py-2 px-4 rounded-lg text-sm ${
                timeRange === "week"
                  ? "bg-purple-500 text-white"
                  : "bg-gray-100 text-gray-700"
              }`}
            >
              7 Days
            </button>
            <button
              onClick={() => setTimeRange("month")}
              className={`py-2 px-4 rounded-lg text-sm ${
                timeRange === "month"
                  ? "bg-purple-500 text-white"
                  : "bg-gray-100 text-gray-700"
              }`}
            >
              30 Days
            </button>
          </div>
        </div>

        {/* AQI Trend Chart */}
        <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-purple-500" />
            <h3 className="text-lg">AQI Trend</h3>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={getData()}>
              <defs>
                <linearGradient id="colorAqi" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" style={{ fontSize: "12px" }} />
              <YAxis style={{ fontSize: "12px" }} />
              <Tooltip />
              <Area type="monotone" dataKey="aqi" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorAqi)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Pollutants Trend */}
        {timeRange !== "day" && (
          <div className="bg-white rounded-2xl shadow-lg p-4 mb-4">
            <h3 className="text-lg mb-4">Pollutant Levels</h3>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={getData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" style={{ fontSize: "12px" }} />
                <YAxis style={{ fontSize: "12px" }} />
                <Tooltip />
                <Line type="monotone" dataKey="pm25" stroke="#f59e0b" strokeWidth={2} name="PM2.5" />
                <Line type="monotone" dataKey="pm10" stroke="#3b82f6" strokeWidth={2} name="PM10" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Statistics */}
        <div className="bg-white rounded-2xl shadow-lg p-4">
          <h3 className="text-lg mb-4">Statistics</h3>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-green-50 rounded-lg p-3">
              <div className="text-xs text-gray-600 mb-1">Average AQI</div>
              <div className="text-2xl text-green-600">43</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="text-xs text-gray-600 mb-1">Best Day</div>
              <div className="text-2xl text-blue-600">35</div>
            </div>
            <div className="bg-orange-50 rounded-lg p-3">
              <div className="text-xs text-gray-600 mb-1">Worst Day</div>
              <div className="text-2xl text-orange-600">52</div>
            </div>
            <div className="bg-purple-50 rounded-lg p-3">
              <div className="text-xs text-gray-600 mb-1">Good Days</div>
              <div className="text-2xl text-purple-600">85%</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
