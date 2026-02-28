import { Heart, AlertTriangle, CheckCircle } from "lucide-react";

interface HealthRecommendationsProps {
  aqi: number;
}

export function HealthRecommendations({ aqi }: HealthRecommendationsProps) {
  const getRecommendations = (aqi: number) => {
    if (aqi <= 50) {
      return {
        icon: <CheckCircle className="w-6 h-6 text-green-500" />,
        general: "It's a great day to be active outside.",
        sensitive: "Enjoy your usual outdoor activities.",
        color: "border-green-200 bg-green-50",
      };
    } else if (aqi <= 100) {
      return {
        icon: <Heart className="w-6 h-6 text-yellow-500" />,
        general: "Unusually sensitive people should consider reducing prolonged or heavy outdoor exertion.",
        sensitive: "Consider reducing prolonged or heavy outdoor activities if you experience symptoms.",
        color: "border-yellow-200 bg-yellow-50",
      };
    } else if (aqi <= 150) {
      return {
        icon: <AlertTriangle className="w-6 h-6 text-orange-500" />,
        general: "People with respiratory or heart conditions should limit prolonged outdoor exertion.",
        sensitive: "Reduce prolonged or heavy outdoor exertion. Take more breaks during outdoor activities.",
        color: "border-orange-200 bg-orange-50",
      };
    } else {
      return {
        icon: <AlertTriangle className="w-6 h-6 text-red-500" />,
        general: "Everyone should avoid prolonged outdoor exertion.",
        sensitive: "Avoid prolonged or heavy outdoor activities. Move activities indoors or reschedule.",
        color: "border-red-200 bg-red-50",
      };
    }
  };

  const recommendations = getRecommendations(aqi);

  return (
    <div className={`rounded-lg border-2 p-6 ${recommendations.color}`}>
      <div className="flex items-center gap-2 mb-4">
        {recommendations.icon}
        <h3 className="text-xl">Health Recommendations</h3>
      </div>
      
      <div className="space-y-3">
        <div>
          <h4 className="text-sm mb-1">General Public:</h4>
          <p className="text-sm text-gray-700">{recommendations.general}</p>
        </div>
        
        <div>
          <h4 className="text-sm mb-1">Sensitive Groups:</h4>
          <p className="text-sm text-gray-700">{recommendations.sensitive}</p>
        </div>
      </div>
    </div>
  );
}
