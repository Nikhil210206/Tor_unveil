import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import {
  ScatterChart,
  Scatter,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";

const categoryColors = {
  Low: "hsl(var(--success))",
  Medium: "hsl(var(--warning))",
  High: "hsl(var(--high))",
  Critical: "hsl(var(--critical))",
};

export default function TimelinePage() {
  const { data: timelineData, isLoading } = useQuery({
    queryKey: ["timeline"],
    queryFn: api.getTimeline,
  });

  // Transform data for scatter plot
  const scatterData = timelineData?.map((point) => ({
    time: new Date(point.time).getTime(),
    score: point.score,
    category: point.category,
    flow_id: point.flow_id,
    source: point.source,
    destination: point.destination,
  }));

  // Aggregate data by hour for line chart
  const lineData = timelineData?.reduce((acc, point) => {
    const hour = new Date(point.time).setMinutes(0, 0, 0);
    const existing = acc.find((item) => item.time === hour);
    if (existing) {
      existing.count += 1;
    } else {
      acc.push({ time: hour, count: 1 });
    }
    return acc;
  }, [] as { time: number; count: number }[]);

  // Group scatter data by category
  const dataByCategory = {
    Low: scatterData?.filter((d) => d.category === "Low") || [],
    Medium: scatterData?.filter((d) => d.category === "Medium") || [],
    High: scatterData?.filter((d) => d.category === "High") || [],
    Critical: scatterData?.filter((d) => d.category === "Critical") || [],
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload[0]) {
      const data = payload[0].payload;
      return (
        <Card className="p-3">
          <p className="font-semibold">Flow #{data.flow_id}</p>
          <p className="text-sm">Score: {data.score}</p>
          <p className="text-sm">Category: {data.category}</p>
          <p className="text-sm font-mono">{data.source} → {data.destination}</p>
          <p className="text-xs text-muted-foreground">
            {format(new Date(data.time), "PPpp")}
          </p>
        </Card>
      );
    }
    return null;
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Timeline Analysis</h1>
        <p className="text-muted-foreground">
          Visualize flow patterns and confidence scores over time
        </p>
      </div>

      {/* Scatter Plot */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Confidence Score Distribution Over Time</h2>
        {isLoading ? (
          <Skeleton className="w-full h-[500px]" />
        ) : (
          <ResponsiveContainer width="100%" height={500}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 80, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="time"
                domain={["auto", "auto"]}
                name="Time"
                tickFormatter={(unixTime) => format(new Date(unixTime), "HH:mm")}
                type="number"
                stroke="hsl(var(--muted-foreground))"
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                dataKey="score"
                name="Score"
                domain={[0, 100]}
                stroke="hsl(var(--muted-foreground))"
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              {Object.entries(dataByCategory).map(([category, data]) => (
                <Scatter
                  key={category}
                  name={category}
                  data={data}
                  fill={categoryColors[category as keyof typeof categoryColors]}
                />
              ))}
            </ScatterChart>
          </ResponsiveContainer>
        )}
      </Card>

      {/* Line Chart */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Flow Count Over Time</h2>
        {isLoading ? (
          <Skeleton className="w-full h-[400px]" />
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={lineData} margin={{ top: 20, right: 20, bottom: 60, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="time"
                tickFormatter={(unixTime) => format(new Date(unixTime), "HH:mm")}
                stroke="hsl(var(--muted-foreground))"
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
                labelFormatter={(unixTime) => format(new Date(unixTime), "PPpp")}
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="count"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={{ fill: "hsl(var(--primary))", r: 4 }}
                activeDot={{ r: 6 }}
                name="Flow Count"
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </Card>
    </div>
  );
}
