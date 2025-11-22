import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, Flow } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { FlowDetailsModal } from "@/components/FlowDetailsModal";
import { ZoomIn, ZoomOut, RotateCcw } from "lucide-react";
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Skeleton } from "@/components/ui/skeleton";

const categoryColors = {
  Low: "hsl(var(--success))",
  Medium: "hsl(var(--warning))",
  High: "hsl(var(--high))",
  Critical: "hsl(var(--critical))",
};

export default function GraphPage() {
  const [layout, setLayout] = useState("force");
  const [minWeight, setMinWeight] = useState(0.3);
  const [selectedFlow, setSelectedFlow] = useState<Flow | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  const { data: graphData, isLoading } = useQuery({
    queryKey: ["graph"],
    queryFn: api.getGraphData,
  });

  // Transform graph data to React Flow format
  const getLayoutedElements = useCallback(() => {
    if (!graphData) return { nodes: [], edges: [] };

    const nodes: Node[] = graphData.nodes.map((node, index) => {
      const radius = 40 + (node.score / 100) * 30;
      const angle = (index / graphData.nodes.length) * 2 * Math.PI;
      const x = 400 + Math.cos(angle) * 300;
      const y = 400 + Math.sin(angle) * 300;

      return {
        id: node.id.toString(),
        data: { label: node.label, score: node.score, category: node.category },
        position: { x, y },
        style: {
          background: categoryColors[node.category as keyof typeof categoryColors],
          width: radius,
          height: radius,
          borderRadius: "50%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          fontSize: "12px",
          fontWeight: "bold",
          border: "2px solid rgba(255,255,255,0.3)",
        },
      };
    });

    const edges: Edge[] = graphData.edges
      .filter((edge) => edge.weight >= minWeight)
      .map((edge) => ({
        id: `${edge.source}-${edge.target}`,
        source: edge.source.toString(),
        target: edge.target.toString(),
        style: {
          strokeWidth: edge.weight * 5,
          stroke: "hsl(var(--muted-foreground))",
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: "hsl(var(--muted-foreground))",
        },
        label: edge.type,
        labelStyle: { fontSize: 10, fill: "hsl(var(--foreground))" },
      }));

    return { nodes, edges };
  }, [graphData, minWeight]);

  const { nodes, edges } = getLayoutedElements();
  const [nodesState, , onNodesChange] = useNodesState(nodes);
  const [edgesState, , onEdgesChange] = useEdgesState(edges);

  const handleNodeClick = useCallback(
    async (_event: React.MouseEvent, node: Node) => {
      const flowId = parseInt(node.id);
      try {
        const flows = await api.getFlows({ limit: 1000 });
        const flow = flows.find((f) => f.id === flowId);
        if (flow) {
          setSelectedFlow(flow);
          setModalOpen(true);
        }
      } catch (error) {
        console.error("Failed to fetch flow:", error);
      }
    },
    []
  );

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Network Graph</h1>
        </div>

        <Card className="p-6 h-[800px] relative">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <Skeleton className="w-full h-full" />
            </div>
          ) : (
            <>
              {/* Controls Panel */}
              <div className="absolute top-4 right-4 z-10 space-y-4">
                <Card className="p-4 space-y-4 bg-card/95 backdrop-blur">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Layout</label>
                    <Select value={layout} onValueChange={setLayout}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="force">Force-Directed</SelectItem>
                        <SelectItem value="hierarchical">Hierarchical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium">Min Weight</label>
                      <span className="text-sm font-semibold text-primary">
                        {minWeight.toFixed(1)}
                      </span>
                    </div>
                    <Slider
                      value={[minWeight * 10]}
                      onValueChange={([value]) => setMinWeight(value / 10)}
                      min={1}
                      max={10}
                      step={1}
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button variant="outline" size="icon">
                      <ZoomIn className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="icon">
                      <ZoomOut className="h-4 w-4" />
                    </Button>
                    <Button variant="outline" size="icon">
                      <RotateCcw className="h-4 w-4" />
                    </Button>
                  </div>
                </Card>
              </div>

              {/* Legend */}
              <div className="absolute bottom-4 left-4 z-10">
                <Card className="p-4 bg-card/95 backdrop-blur">
                  <h4 className="text-sm font-semibold mb-2">Legend</h4>
                  <div className="space-y-2">
                    {Object.entries(categoryColors).map(([category, color]) => (
                      <div key={category} className="flex items-center gap-2">
                        <div
                          className="w-4 h-4 rounded-full"
                          style={{ backgroundColor: color }}
                        />
                        <span className="text-sm">{category}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Edge thickness = correlation weight
                  </p>
                </Card>
              </div>

              {/* React Flow */}
              <ReactFlow
                nodes={nodesState}
                edges={edgesState}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={handleNodeClick}
                fitView
                className="rounded-lg"
              >
                <Background />
                <Controls />
              </ReactFlow>
            </>
          )}
        </Card>
      </div>

      <FlowDetailsModal flow={selectedFlow} open={modalOpen} onOpenChange={setModalOpen} />
    </div>
  );
}
