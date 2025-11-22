import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, Flow } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { CategoryBadge } from "@/components/CategoryBadge";
import { FlowDetailsModal } from "@/components/FlowDetailsModal";
import { Skeleton } from "@/components/ui/skeleton";
import { Download, ChevronLeft, ChevronRight } from "lucide-react";

const CATEGORIES = ["Low", "Medium", "High", "Critical"];
const PAGE_SIZE = 50;

export default function FlowsPage() {
  const [minScore, setMinScore] = useState(0);
  const [selectedCategories, setSelectedCategories] = useState<string[]>(CATEGORIES);
  const [searchIp, setSearchIp] = useState("");
  const [page, setPage] = useState(0);
  const [selectedFlow, setSelectedFlow] = useState<Flow | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const { data: flows, isLoading } = useQuery({
    queryKey: ["flows", minScore, selectedCategories, searchIp, page],
    queryFn: () =>
      api.getFlows({
        min_score: minScore,
        category: selectedCategories.join(","),
        search_ip: searchIp || undefined,
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
      }),
  });

  const toggleCategory = (category: string) => {
    setSelectedCategories((prev) =>
      prev.includes(category)
        ? prev.filter((c) => c !== category)
        : [...prev, category]
    );
    setPage(0);
  };

  const handleExportCSV = () => {
    if (!flows) return;
    
    const headers = ["ID", "Source", "Destination", "Protocol", "Time", "Packets", "Bytes", "Score", "Category"];
    const rows = flows.map((flow) => [
      flow.id,
      `${flow.src_ip}:${flow.src_port}`,
      `${flow.dst_ip}:${flow.dst_port}`,
      flow.protocol,
      flow.ts_start,
      flow.pkt_count,
      flow.byte_count,
      flow.confidence_score,
      flow.confidence_category,
    ]);

    const csv = [headers, ...rows].map((row) => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `flows-export-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleViewDetails = (flow: Flow) => {
    setSelectedFlow(flow);
    setModalOpen(true);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex gap-6">
        {/* Sidebar Filters */}
        <aside className="w-64 flex-shrink-0">
          <Card className="p-6 space-y-6 sticky top-24">
            <div>
              <h3 className="font-semibold mb-4">Filters</h3>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium">Min Confidence Score</label>
                <span className="text-sm font-semibold text-primary">{minScore}</span>
              </div>
              <Slider
                value={[minScore]}
                onValueChange={([value]) => {
                  setMinScore(value);
                  setPage(0);
                }}
                min={0}
                max={100}
                step={5}
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-3 block">Categories</label>
              <div className="space-y-2">
                {CATEGORIES.map((category) => (
                  <div key={category} className="flex items-center gap-2">
                    <Checkbox
                      id={category}
                      checked={selectedCategories.includes(category)}
                      onCheckedChange={() => toggleCategory(category)}
                    />
                    <label htmlFor={category} className="text-sm cursor-pointer">
                      {category}
                    </label>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Search IP</label>
              <Input
                placeholder="192.168.1.1"
                value={searchIp}
                onChange={(e) => {
                  setSearchIp(e.target.value);
                  setPage(0);
                }}
              />
            </div>
          </Card>
        </aside>

        {/* Main Content */}
        <div className="flex-1 space-y-4">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold">Flows Explorer</h1>
            <Button variant="outline" onClick={handleExportCSV} disabled={!flows}>
              <Download className="mr-2 h-4 w-4" />
              Export CSV
            </Button>
          </div>

          <Card className="overflow-hidden">
            {isLoading ? (
              <div className="p-6 space-y-2">
                {[...Array(10)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : flows && flows.length > 0 ? (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr className="border-b border-border">
                        <th className="text-left py-3 px-4 font-medium">ID</th>
                        <th className="text-left py-3 px-4 font-medium">Source</th>
                        <th className="text-left py-3 px-4 font-medium">Destination</th>
                        <th className="text-left py-3 px-4 font-medium">Protocol</th>
                        <th className="text-left py-3 px-4 font-medium">Time</th>
                        <th className="text-left py-3 px-4 font-medium">Packets</th>
                        <th className="text-left py-3 px-4 font-medium">Bytes</th>
                        <th className="text-left py-3 px-4 font-medium">Score</th>
                        <th className="text-left py-3 px-4 font-medium">Category</th>
                        <th className="text-left py-3 px-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {flows.map((flow) => (
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
                          <td className="py-3 px-4 text-sm">
                            {new Date(flow.ts_start).toLocaleTimeString()}
                          </td>
                          <td className="py-3 px-4 text-sm">{flow.pkt_count.toLocaleString()}</td>
                          <td className="py-3 px-4 text-sm">{flow.byte_count.toLocaleString()}</td>
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

                {/* Pagination */}
                <div className="flex items-center justify-between p-4 border-t border-border">
                  <p className="text-sm text-muted-foreground">
                    Showing {page * PAGE_SIZE + 1} - {page * PAGE_SIZE + flows.length}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(0, p - 1))}
                      disabled={page === 0}
                    >
                      <ChevronLeft className="h-4 w-4 mr-1" />
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => p + 1)}
                      disabled={flows.length < PAGE_SIZE}
                    >
                      Next
                      <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="p-12 text-center text-muted-foreground">
                <p>No flows found matching your filters.</p>
              </div>
            )}
          </Card>
        </div>
      </div>

      <FlowDetailsModal flow={selectedFlow} open={modalOpen} onOpenChange={setModalOpen} />
    </div>
  );
}
