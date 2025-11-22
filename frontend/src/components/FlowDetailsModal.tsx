import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { useQuery } from "@tanstack/react-query";
import { api, Flow } from "@/lib/api";
import { Check, X, ArrowRight } from "lucide-react";
import { CategoryBadge } from "./CategoryBadge";
import { Skeleton } from "@/components/ui/skeleton";

interface FlowDetailsModalProps {
  flow: Flow | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function FlowDetailsModal({ flow, open, onOpenChange }: FlowDetailsModalProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["flow-detail", flow?.id],
    queryFn: () => (flow ? api.getFlowDetail(flow.id) : null),
    enabled: !!flow && open,
  });

  if (!flow) return null;

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between">
            <span>Flow Details #{flow.id}</span>
            <CategoryBadge category={flow.confidence_category as any} />
          </DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-48 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        ) : data ? (
          <div className="space-y-6">
            {/* Flow Information */}
            <Card className="p-4">
              <h3 className="font-semibold mb-4">Flow Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Source</p>
                  <p className="font-mono font-medium">
                    {data.flow.src_ip}:{data.flow.src_port}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Destination</p>
                  <p className="font-mono font-medium">
                    {data.flow.dst_ip}:{data.flow.dst_port}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Protocol</p>
                  <Badge variant="secondary">{data.flow.protocol}</Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Packets / Bytes</p>
                  <p className="font-medium">
                    {data.flow.pkt_count.toLocaleString()} / {data.flow.byte_count.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Start Time</p>
                  <p className="text-sm">{formatDateTime(data.flow.ts_start)}</p>
                </div>
                {data.flow.ts_end && (
                  <div>
                    <p className="text-sm text-muted-foreground">End Time</p>
                    <p className="text-sm">{formatDateTime(data.flow.ts_end)}</p>
                  </div>
                )}
              </div>
            </Card>

            {/* TOR Indicators */}
            <Card className="p-4">
              <h3 className="font-semibold mb-4">TOR Indicators</h3>
              <div className="space-y-2">
                <IndicatorRow
                  label="TOR Handshake Detected"
                  detected={data.flow.tor_handshake_detected}
                />
                <IndicatorRow
                  label="Relay Communication"
                  detected={data.flow.relay_communication}
                />
                <IndicatorRow
                  label="Directory Fetch"
                  detected={data.flow.directory_fetch}
                />
                <IndicatorRow
                  label="Obfsproxy Candidate"
                  detected={data.flow.obfsproxy_candidate}
                />
              </div>
            </Card>

            {/* Confidence Breakdown */}
            <Card className="p-4">
              <h3 className="font-semibold mb-4">Confidence Breakdown</h3>
              <div className="space-y-4">
                <ScoreBar label="TOR Node Match" value={16} max={40} />
                <ScoreBar label="Timing Correlation" value={12} max={30} />
                <ScoreBar label="Payload Similarity" value={8} max={20} />
                <ScoreBar label="Unusual Patterns" value={4} max={10} />
                <div className="pt-2 border-t border-border">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Total Score</span>
                    <span className="text-2xl font-bold text-primary">
                      {data.flow.confidence_score}/100
                    </span>
                  </div>
                </div>
              </div>
            </Card>

            {/* Correlated Flows */}
            {data.correlations && data.correlations.length > 0 && (
              <Card className="p-4">
                <h3 className="font-semibold mb-4">Correlated Flows</h3>
                <div className="space-y-2">
                  {data.correlations.map((corr) => (
                    <div
                      key={corr.id}
                      className="flex items-center justify-between p-2 rounded bg-muted/50"
                    >
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-mono">
                          Flow #{corr.correlated_flow_id}
                        </span>
                        <ArrowRight className="h-4 w-4 text-muted-foreground" />
                        <Badge variant="secondary" className="text-xs">
                          {corr.type}
                        </Badge>
                      </div>
                      <span className="text-sm font-medium">
                        Weight: {corr.weight.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Payload Sample */}
            {data.payload_sample && (
              <Card className="p-4">
                <h3 className="font-semibold mb-2">Payload Sample</h3>
                <pre className="text-xs font-mono bg-background p-3 rounded overflow-x-auto">
                  {data.payload_sample}
                </pre>
              </Card>
            )}
          </div>
        ) : null}
      </DialogContent>
    </Dialog>
  );
}

function IndicatorRow({ label, detected }: { label: string; detected?: boolean }) {
  return (
    <div className="flex items-center justify-between p-2 rounded bg-muted/50">
      <span className="text-sm">{label}</span>
      {detected ? (
        <Check className="h-5 w-5 text-success" />
      ) : (
        <X className="h-5 w-5 text-muted-foreground" />
      )}
    </div>
  );
}

function ScoreBar({ label, value, max }: { label: string; value: number; max: number }) {
  const percentage = (value / max) * 100;
  
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span className="font-medium">
          {value}/{max}
        </span>
      </div>
      <Progress value={percentage} className="h-2" />
    </div>
  );
}
