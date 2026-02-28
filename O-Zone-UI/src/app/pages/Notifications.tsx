import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, Bell, AlertTriangle, Info, CheckCircle, TrendingUp } from "lucide-react";

export function Notifications() {
  const navigate = useNavigate();
  const [notifications] = useState([
    {
      id: 1,
      type: "warning",
      title: "AQI Warning",
      message: "Air quality index has reached 95 (Moderate). Consider reducing outdoor activities.",
      time: "5 minutes ago",
      read: false,
    },
    {
      id: 2,
      type: "alert",
      title: "Child Safety Alert",
      message: "Tommy's location has AQI of 68. Unhealthy for sensitive groups.",
      time: "15 minutes ago",
      read: false,
    },
    {
      id: 3,
      type: "info",
      title: "Daily Forecast",
      message: "Tomorrow's air quality: Good in the morning, Moderate in the afternoon.",
      time: "1 hour ago",
      read: true,
    },
    {
      id: 4,
      type: "tip",
      title: "Health Tip",
      message: "Run your air purifier for 30 minutes before bedtime for better sleep quality.",
      time: "2 hours ago",
      read: true,
    },
    {
      id: 5,
      type: "success",
      title: "Air Quality Improved",
      message: "Your area's AQI has dropped to 40 (Good). Great time for outdoor activities!",
      time: "3 hours ago",
      read: true,
    },
    {
      id: 6,
      type: "trend",
      title: "Weekly Summary",
      message: "This week's average AQI: 45 (Good). 85% of days had good air quality.",
      time: "1 day ago",
      read: true,
    },
  ]);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "warning":
      case "alert":
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case "info":
        return <Info className="w-5 h-5 text-blue-500" />;
      case "success":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "tip":
        return <Bell className="w-5 h-5 text-purple-500" />;
      case "trend":
        return <TrendingUp className="w-5 h-5 text-indigo-500" />;
      default:
        return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch (type) {
      case "warning":
      case "alert":
        return "bg-red-50 border-red-200";
      case "info":
        return "bg-blue-50 border-blue-200";
      case "success":
        return "bg-green-50 border-green-200";
      case "tip":
        return "bg-purple-50 border-purple-200";
      case "trend":
        return "bg-indigo-50 border-indigo-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-500 text-white p-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div className="flex-1">
            <h1 className="text-xl">Notifications</h1>
            <p className="text-sm opacity-90">
              {unreadCount > 0 ? `${unreadCount} unread notifications` : "All caught up!"}
            </p>
          </div>
          <button className="text-sm bg-white bg-opacity-20 px-3 py-1 rounded-full">
            Mark all read
          </button>
        </div>
      </header>

      <div className="p-4">
        {/* Unread Notifications */}
        {unreadCount > 0 && (
          <div className="mb-4">
            <h2 className="text-sm text-gray-500 mb-3">Unread</h2>
            <div className="space-y-3">
              {notifications
                .filter((n) => !n.read)
                .map((notification) => (
                  <div
                    key={notification.id}
                    className={`rounded-2xl border-2 p-4 ${getNotificationColor(notification.type)}`}
                  >
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 mt-1">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-1">
                          <h3 className="text-sm">{notification.title}</h3>
                          <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                        </div>
                        <p className="text-sm text-gray-700 mb-2">
                          {notification.message}
                        </p>
                        <p className="text-xs text-gray-500">{notification.time}</p>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* Read Notifications */}
        <div>
          <h2 className="text-sm text-gray-500 mb-3">Earlier</h2>
          <div className="space-y-3">
            {notifications
              .filter((n) => n.read)
              .map((notification) => (
                <div
                  key={notification.id}
                  className="bg-white rounded-2xl border border-gray-200 p-4 opacity-75"
                >
                  <div className="flex gap-3">
                    <div className="flex-shrink-0 mt-1">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-sm mb-1">{notification.title}</h3>
                      <p className="text-sm text-gray-700 mb-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-500">{notification.time}</p>
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
