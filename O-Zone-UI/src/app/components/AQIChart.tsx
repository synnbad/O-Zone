import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

interface AQIChartProps {
  data: { time: string; aqi: number }[];
}

export function AQIChart({ data }: AQIChartProps) {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl mb-4">24-Hour AQI Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <Tooltip />
          <ReferenceLine y={50} stroke="#22c55e" strokeDasharray="3 3" label="Good" />
          <ReferenceLine y={100} stroke="#eab308" strokeDasharray="3 3" label="Moderate" />
          <ReferenceLine y={150} stroke="#f97316" strokeDasharray="3 3" label="Unhealthy" />
          <Line type="monotone" dataKey="aqi" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
