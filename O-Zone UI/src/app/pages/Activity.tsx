import { useState } from "react";
import { useNavigate } from "react-router";
import { ArrowLeft, Activity, AlertCircle, CheckCircle } from "lucide-react";

export function ActivityPage() {
  const navigate = useNavigate();
  const [selectedActivity, setSelectedActivity] = useState<"easy" | "hard" | null>(null);
  const currentAQI = 45;

  const activities = {
    easy: {
      name: "Light Activities",
      examples: ["Walking", "Yoga", "Stretching", "Light Gardening"],
      recommendation: currentAQI <= 100 ? "safe" : currentAQI <= 150 ? "caution" : "avoid",
    },
    hard: {
      name: "Intense Activities",
      examples: ["Running", "Cycling", "Sports", "Heavy Exercise"],
      recommendation: currentAQI <= 50 ? "safe" : currentAQI <= 100 ? "caution" : "avoid",
    },
  };

  const getRecommendationColor = (rec: string) => {
    if (rec === "safe") return "bg-green-100 border-green-500 text-green-800";
    if (rec === "caution") return "bg-yellow-100 border-yellow-500 text-yellow-800";
    return "bg-red-100 border-red-500 text-red-800";
  };

  const getRecommendationIcon = (rec: string) => {
    if (rec === "safe") return <CheckCircle className="w-6 h-6 text-green-500" />;
    return <AlertCircle className="w-6 h-6 text-yellow-500" />;
  };

  const getRecommendationText = (rec: string) => {
    if (rec === "safe") return "Safe to proceed";
    if (rec === "caution") return "Proceed with caution";
    return "Not recommended";
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-blue-500 text-white p-4">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate("/dashboard")}>
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-xl">Plan Outdoor Activity</h1>
            <p className="text-sm opacity-90">Current AQI: {currentAQI}</p>
          </div>
        </div>
      </header>

      <div className="p-4">
        <div className="bg-white rounded-2xl shadow-lg p-6 mb-4">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-6 h-6 text-blue-500" />
            <h2 className="text-xl">Choose Activity Level</h2>
          </div>
          <p className="text-gray-600 text-sm mb-6">
            Select the intensity of your planned outdoor activity to get personalized recommendations.
          </p>

          <div className="space-y-4">
            {/* Easy Activities */}
            <button
              onClick={() => setSelectedActivity("easy")}
              className={`w-full p-5 rounded-xl border-2 text-left transition-all ${
                selectedActivity === "easy"
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 bg-white hover:border-blue-300"
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="text-lg mb-1">🚶 Easy Activities</h3>
                  <p className="text-sm text-gray-600">Low-intensity outdoor activities</p>
                </div>
                {getRecommendationIcon(activities.easy.recommendation)}
              </div>
              <div className="flex flex-wrap gap-2 mt-3">
                {activities.easy.examples.map((example) => (
                  <span
                    key={example}
                    className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700"
                  >
                    {example}
                  </span>
                ))}
              </div>
            </button>

            {/* Hard Activities */}
            <button
              onClick={() => setSelectedActivity("hard")}
              className={`w-full p-5 rounded-xl border-2 text-left transition-all ${
                selectedActivity === "hard"
                  ? "border-blue-500 bg-blue-50"
                  : "border-gray-200 bg-white hover:border-blue-300"
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="text-lg mb-1">🏃 Intense Activities</h3>
                  <p className="text-sm text-gray-600">High-intensity outdoor activities</p>
                </div>
                {getRecommendationIcon(activities.hard.recommendation)}
              </div>
              <div className="flex flex-wrap gap-2 mt-3">
                {activities.hard.examples.map((example) => (
                  <span
                    key={example}
                    className="px-3 py-1 bg-gray-100 rounded-full text-xs text-gray-700"
                  >
                    {example}
                  </span>
                ))}
              </div>
            </button>
          </div>
        </div>

        {/* Recommendation Card */}
        {selectedActivity && (
          <div
            className={`rounded-2xl border-2 p-6 ${getRecommendationColor(
              activities[selectedActivity].recommendation
            )}`}
          >
            <div className="flex items-center gap-3 mb-4">
              {getRecommendationIcon(activities[selectedActivity].recommendation)}
              <h3 className="text-xl">
                {getRecommendationText(activities[selectedActivity].recommendation)}
              </h3>
            </div>

            <div className="space-y-3 text-sm">
              {activities[selectedActivity].recommendation === "safe" && (
                <>
                  <p>✅ Air quality is good for outdoor activities</p>
                  <p>✅ No special precautions needed</p>
                  <p>✅ Enjoy your outdoor time!</p>
                </>
              )}
              {activities[selectedActivity].recommendation === "caution" && (
                <>
                  <p>⚠️ Air quality is acceptable for most people</p>
                  <p>⚠️ Take breaks if you experience symptoms</p>
                  <p>⚠️ Consider reducing duration</p>
                </>
              )}
              {activities[selectedActivity].recommendation === "avoid" && (
                <>
                  <p>🚫 Air quality is poor for outdoor activities</p>
                  <p>🚫 Consider moving activities indoors</p>
                  <p>🚫 Reschedule if possible</p>
                </>
              )}
            </div>

            <div className="mt-4 pt-4 border-t border-current border-opacity-20">
              <p className="text-xs opacity-75">
                Best time for outdoor activities: Early morning (6-8 AM) or evening (6-8 PM)
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
