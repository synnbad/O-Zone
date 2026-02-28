interface PollutantCardProps {
  name: string;
  value: number;
  unit: string;
  level: "good" | "moderate" | "unhealthy";
}

export function PollutantCard({ name, value, unit, level }: PollutantCardProps) {
  const getLevelColor = (level: string) => {
    switch (level) {
      case "good":
        return "bg-green-100 text-green-800 border-green-200";
      case "moderate":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "unhealthy":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const levelText = level.charAt(0).toUpperCase() + level.slice(1);

  return (
    <div className={`rounded-lg border-2 p-4 ${getLevelColor(level)}`}>
      <div className="text-sm mb-1">{name}</div>
      <div className="text-2xl mb-1">
        {value} <span className="text-sm">{unit}</span>
      </div>
      <div className="text-xs">{levelText}</div>
    </div>
  );
}
