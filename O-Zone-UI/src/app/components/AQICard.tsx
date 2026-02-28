import { Wind } from "lucide-react";

interface AQICardProps {
  aqi: number;
  location: string;
}

export function AQICard({ aqi, location }: AQICardProps) {
  const getAQIInfo = (aqi: number) => {
    if (aqi <= 50) {
      return {
        level: "Good",
        color: "bg-green-500",
        textColor: "text-green-500",
        description: "Air quality is satisfactory, and air pollution poses little or no risk.",
      };
    } else if (aqi <= 100) {
      return {
        level: "Moderate",
        color: "bg-yellow-500",
        textColor: "text-yellow-500",
        description: "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution.",
      };
    } else if (aqi <= 150) {
      return {
        level: "Unhealthy for Sensitive Groups",
        color: "bg-orange-500",
        textColor: "text-orange-500",
        description: "Members of sensitive groups may experience health effects. The general public is less likely to be affected.",
      };
    } else if (aqi <= 200) {
      return {
        level: "Unhealthy",
        color: "bg-red-500",
        textColor: "text-red-500",
        description: "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects.",
      };
    } else if (aqi <= 300) {
      return {
        level: "Very Unhealthy",
        color: "bg-purple-600",
        textColor: "text-purple-600",
        description: "Health alert: The risk of health effects is increased for everyone.",
      };
    } else {
      return {
        level: "Hazardous",
        color: "bg-rose-900",
        textColor: "text-rose-900",
        description: "Health warning of emergency conditions: everyone is more likely to be affected.",
      };
    }
  };

  const aqiInfo = getAQIInfo(aqi);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Wind className="w-6 h-6 text-gray-600" />
          <h2 className="text-xl">{location}</h2>
        </div>
      </div>
      
      <div className="flex items-center justify-center mb-6">
        <div className={`w-32 h-32 rounded-full ${aqiInfo.color} flex items-center justify-center`}>
          <div className="text-center text-white">
            <div className="text-4xl">{aqi}</div>
            <div className="text-sm">AQI</div>
          </div>
        </div>
      </div>

      <div className="text-center">
        <h3 className={`text-2xl mb-2 ${aqiInfo.textColor}`}>{aqiInfo.level}</h3>
        <p className="text-gray-600 text-sm">{aqiInfo.description}</p>
      </div>
    </div>
  );
}
