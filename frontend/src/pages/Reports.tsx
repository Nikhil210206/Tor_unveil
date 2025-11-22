import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FileText, Download, Loader2, Plus } from "lucide-react";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";
import { format } from "date-fns";

export default function ReportsPage() {
  const [newReportTitle, setNewReportTitle] = useState("");
  const queryClient = useQueryClient();

  const { data: reports, isLoading } = useQuery({
    queryKey: ["reports"],
    queryFn: api.getReports,
  });

  const generateMutation = useMutation({
    mutationFn: (title: string) => api.generateReport(title),
    onSuccess: () => {
      toast.success("Report generated successfully!");
      setNewReportTitle("");
      queryClient.invalidateQueries({ queryKey: ["reports"] });
    },
    onError: (error) => {
      toast.error("Failed to generate report: " + error.message);
    },
  });

  const handleGenerate = () => {
    if (!newReportTitle.trim()) {
      toast.error("Please enter a report title");
      return;
    }
    generateMutation.mutate(newReportTitle);
  };

  const handleDownload = async (filename: string, title: string) => {
    try {
      const blob = await api.downloadReport(filename);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Report downloaded successfully!");
    } catch (error) {
      toast.error("Failed to download report");
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Reports</h1>
          <p className="text-muted-foreground">
            Generate and download comprehensive PDF reports of your TOR analysis
          </p>
        </div>

        {/* Generate New Report */}
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Generate New Report</h2>
          <div className="flex gap-4">
            <Input
              placeholder="Enter report title..."
              value={newReportTitle}
              onChange={(e) => setNewReportTitle(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleGenerate()}
              className="flex-1"
            />
            <Button
              onClick={handleGenerate}
              disabled={generateMutation.isPending || !newReportTitle.trim()}
              className="min-w-[200px]"
            >
              {generateMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Plus className="mr-2 h-4 w-4" />
                  Generate PDF Report
                </>
              )}
            </Button>
          </div>
          {generateMutation.isPending && (
            <div className="mt-4 p-4 rounded-lg bg-primary/10 border border-primary/20">
              <div className="flex items-center gap-3">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                <p className="text-sm">
                  Generating report... This may take a few moments as we compile all the data.
                </p>
              </div>
            </div>
          )}
        </Card>

        {/* Previous Reports */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Previous Reports</h2>
          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <Skeleton key={i} className="h-48" />
              ))}
            </div>
          ) : reports && reports.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {reports.map((report) => (
                <Card key={report.id} className="p-6 hover:shadow-lg transition-shadow">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-lg bg-primary/10">
                      <FileText className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-semibold mb-1 truncate">{report.title}</h3>
                      <p className="text-xs text-muted-foreground mb-3">
                        {format(new Date(report.created_at), "PPp")}
                      </p>
                      <div className="grid grid-cols-3 gap-2 text-xs mb-4">
                        <div>
                          <p className="text-muted-foreground">Total</p>
                          <p className="font-semibold">{report.total_flows}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Suspects</p>
                          <p className="font-semibold text-warning">{report.suspect_flows}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Critical</p>
                          <p className="font-semibold text-critical">{report.critical_alerts}</p>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        className="w-full"
                        onClick={() => handleDownload(report.file_path, report.title)}
                      >
                        <Download className="mr-2 h-3 w-3" />
                        Download PDF
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted mb-4">
                <FileText className="h-8 w-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No Reports Yet</h3>
              <p className="text-muted-foreground mb-4">
                Generate your first report to get started
              </p>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
