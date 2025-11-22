import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { StatCard } from "@/components/StatCard";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CategoryBadge } from "@/components/CategoryBadge";
import { FlowDetailsModal } from "@/components/FlowDetailsModal";
import {
  Activity,
  AlertTriangle,
  TrendingUp,
  AlertCircle,
  ExternalLink,
} from "lucide-react";
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useState } from "react";
import { Flow } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

export default function Dashboard() {
  const [selectedFlow, setSelectedFlow] = useState<Flow | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["stats"],
    queryFn: api.getStats,
    refetchInterval: 5000,
  });

  const { data: topFlows, isLoading: flowsLoading } = useQuery({
    queryKey: ["top-flows"],
    queryFn: () => api.getFlows({ min_score: 60, limit: 10 }),
    refetchInterval: 5000,
  });

  const scoreDistribution = [
    { range: "0-20", count: stats ? Math.floor(stats.total_flows * 0.4) : 0 },
    { range: "21-40", count: stats ? Math.floor(stats.total_flows * 0.3) : 0 },
    { range: "41-60", count: stats ? Math.floor(stats.total_flows * 0.2) : 0 },
    { range: "61-80", count: stats ? Math.floor(stats.total_flows * 0.08) : 0 },
    { range: "81-100", count: stats ? Math.floor(stats.total_flows * 0.02) : 0 },
  ];

  const categoryData = [
    { name: "Low", value: stats ? stats.total_flows - stats.suspect_flows : 0, color: "hsl(var(--success))" },
    { name: "Medium", value: stats ? stats.suspect_flows - stats.high_flows - stats.critical_flows : 0, color: "hsl(var(--warning))" },
    { name: "High", value: stats?.high_flows || 0, color: "hsl(var(--high))" },
    { name: "Critical", value: stats?.critical_flows || 0, color: "hsl(var(--critical))" },
  ];

  const handleViewDetails = (flow: Flow) => {
    setSelectedFlow(flow);
    setModalOpen(true);
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsLoading ? (
          <>
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </>
        ) : stats ? (
          <>
            <StatCard
              title="Total Flows"
              value={stats.total_flows}
              icon={Activity}
              color="blue"
            />
            <StatCard
              title="Suspect Flows"
              value={stats.suspect_flows}
              icon={AlertTriangle}
              color="yellow"
            />
            <StatCard
              title="High Confidence"
              value={stats.high_flows}
              icon={TrendingUp}
              color="orange"
            />
            <StatCard
              title="Critical Alerts"
              value={stats.critical_flows}
              icon={AlertCircle}
              color="red"
              pulse={stats.critical_flows > 0}
            />
          </>
        ) : null}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Bar Chart */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Confidence Score Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={scoreDistribution}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis dataKey="range" stroke="hsl(var(--muted-foreground))" />
              <YAxis stroke="hsl(var(--muted-foreground))" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
              />
              <Bar dataKey="count" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        {/* Pie Chart */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Flows by Category</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "0.5rem",
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Top Suspect Flows Table */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">Top Suspect Flows</h2>
          <Button variant="outline" size="sm" asChild>
            <a href="/flows">View All <ExternalLink className="ml-2 h-4 w-4" /></a>
          </Button>
        </div>
        {flowsLoading ? (
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">ID</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Source</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Destination</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Protocol</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Score</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Category</th>
                  <th className="text-left py-3 px-4 font-medium text-muted-foreground">Actions</th>
                </tr>
              </thead>
              <tbody>
                {topFlows?.map((flow) => (
                  <tr
                    key={flow.id}
                    className="border-b border-border hover:bg-muted/50 transition-colors"
                  >
                    <td className="py-3 px-4 font-mono text-sm">{flow.id}</td>
                    <td className="py-3 px-4 font-mono text-sm">
                      {flow.src_ip}:{flow.src_port}
                    </td>
                    <td className="py-3 px-4 font-mono text-sm">
                      {flow.dst_ip}:{flow.dst_port}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-1 rounded bg-muted text-xs font-medium">
                        {flow.protocol}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-primary">{flow.confidence_score}</span>
                    </td>
                    <td className="py-3 px-4">
                      <CategoryBadge category={flow.confidence_category as any} />
                    </td>
                    <td className="py-3 px-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewDetails(flow)}
                      >
                        Details
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <FlowDetailsModal
        flow={selectedFlow}
        open={modalOpen}
        onOpenChange={setModalOpen}
      />
    </div>
  );
}
