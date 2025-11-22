import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Slider } from "@/components/ui/slider";
import { Upload, FileUp, Check, Loader2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { api, AnalysisResults } from "@/lib/api";
import { toast } from "sonner";

type AnalysisStep = {
  label: string;
  status: "pending" | "active" | "complete";
};

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [timeWindow, setTimeWindow] = useState(10);
  const [minWeight, setMinWeight] = useState(0.3);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisSteps, setAnalysisSteps] = useState<AnalysisStep[]>([
    { label: "Uploading file", status: "pending" },
    { label: "Extracting flows", status: "pending" },
    { label: "Detecting TOR patterns", status: "pending" },
    { label: "Correlating flows", status: "pending" },
    { label: "Scoring confidence", status: "pending" },
  ]);
  const [results, setResults] = useState<AnalysisResults | null>(null);

  const uploadMutation = useMutation({
    mutationFn: api.uploadFile,
    onSuccess: (data) => {
      toast.success(`Uploaded successfully! ${data.flow_count} flows extracted.`);
      updateStep(0, "complete");
      updateStep(1, "active");
      analyzeMutation.mutate({ time_window: timeWindow, min_correlation_weight: minWeight });
    },
    onError: (error) => {
      toast.error("Upload failed: " + error.message);
      resetSteps();
    },
  });

  const analyzeMutation = useMutation({
    mutationFn: api.analyzeFlows,
    onSuccess: (data) => {
      // Simulate step progression
      updateStep(1, "complete");
      updateStep(2, "active");
      setTimeout(() => {
        updateStep(2, "complete");
        updateStep(3, "active");
        setTimeout(() => {
          updateStep(3, "complete");
          updateStep(4, "active");
          setTimeout(() => {
            updateStep(4, "complete");
            setResults(data.results);
            toast.success("Analysis complete!");
          }, 1000);
        }, 1000);
      }, 1000);
    },
    onError: (error) => {
      toast.error("Analysis failed: " + error.message);
      resetSteps();
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setResults(null);
      resetSteps();
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/vnd.tcpdump.pcap": [".pcap", ".pcapng"],
    },
    maxFiles: 1,
  });

  const handleUpload = () => {
    if (!file) return;
    resetSteps();
    setResults(null);
    updateStep(0, "active");
    uploadMutation.mutate(file);
  };

  const updateStep = (index: number, status: AnalysisStep["status"]) => {
    setAnalysisSteps((prev) =>
      prev.map((step, i) => (i === index ? { ...step, status } : step))
    );
    if (status === "active") {
      setUploadProgress(((index + 1) / analysisSteps.length) * 100);
    }
  };

  const resetSteps = () => {
    setAnalysisSteps((prev) => prev.map((step) => ({ ...step, status: "pending" })));
    setUploadProgress(0);
  };

  const isAnalyzing = uploadMutation.isPending || analyzeMutation.isPending;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Upload & Analyze</h1>
          <p className="text-muted-foreground">
            Upload a PCAP file to analyze TOR network traffic patterns
          </p>
        </div>

        {/* Dropzone */}
        <Card
          {...getRootProps()}
          className="p-12 border-2 border-dashed cursor-pointer hover:border-primary transition-colors"
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center justify-center gap-4 text-center">
            {file ? (
              <>
                <FileUp className="h-16 w-16 text-primary" />
                <div>
                  <p className="text-lg font-semibold">{file.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </>
            ) : (
              <>
                <Upload className="h-16 w-16 text-muted-foreground" />
                <div>
                  <p className="text-lg font-semibold">
                    {isDragActive ? "Drop the file here" : "Drag & drop PCAP file here"}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    or click to browse (.pcap, .pcapng only)
                  </p>
                </div>
              </>
            )}
          </div>
        </Card>

        {/* Configuration */}
        <Card className="p-6 space-y-6">
          <h2 className="text-xl font-semibold">Analysis Configuration</h2>
          
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium">Time Window (seconds)</label>
              <span className="text-sm font-semibold text-primary">{timeWindow}s</span>
            </div>
            <Slider
              value={[timeWindow]}
              onValueChange={([value]) => setTimeWindow(value)}
              min={1}
              max={30}
              step={1}
              disabled={isAnalyzing}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Time window for flow correlation analysis
            </p>
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-sm font-medium">Min Correlation Weight</label>
              <span className="text-sm font-semibold text-primary">{minWeight.toFixed(1)}</span>
            </div>
            <Slider
              value={[minWeight * 10]}
              onValueChange={([value]) => setMinWeight(value / 10)}
              min={1}
              max={10}
              step={1}
              disabled={isAnalyzing}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Minimum weight threshold for correlation detection
            </p>
          </div>
        </Card>

        {/* Upload Button */}
        <Button
          size="lg"
          className="w-full"
          onClick={handleUpload}
          disabled={!file || isAnalyzing}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="mr-2 h-5 w-5 animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <Upload className="mr-2 h-5 w-5" />
              Upload & Analyze
            </>
          )}
        </Button>

        {/* Progress Section */}
        {isAnalyzing && (
          <Card className="p-6 space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">Analysis Progress</h3>
                <span className="text-sm text-muted-foreground">
                  {uploadProgress.toFixed(0)}%
                </span>
              </div>
              <Progress value={uploadProgress} className="h-2" />
            </div>

            <div className="space-y-2">
              {analysisSteps.map((step, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 rounded-lg bg-muted/50"
                >
                  <div className="flex-shrink-0">
                    {step.status === "complete" ? (
                      <div className="h-6 w-6 rounded-full bg-success flex items-center justify-center">
                        <Check className="h-4 w-4 text-background" />
                      </div>
                    ) : step.status === "active" ? (
                      <Loader2 className="h-6 w-6 text-primary animate-spin" />
                    ) : (
                      <div className="h-6 w-6 rounded-full border-2 border-muted-foreground" />
                    )}
                  </div>
                  <span className={step.status === "pending" ? "text-muted-foreground" : ""}>
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
          </Card>
        )}

        {/* Results Card */}
        {results && (
          <Card className="p-6 border-primary">
            <h3 className="text-xl font-semibold mb-4 text-primary">Analysis Complete!</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground mb-1">TOR Flows Identified</p>
                <p className="text-2xl font-bold">{results.tor_flows_identified}</p>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground mb-1">Correlations Created</p>
                <p className="text-2xl font-bold">{results.correlations_created}</p>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground mb-1">Flows Scored</p>
                <p className="text-2xl font-bold">{results.flows_scored}</p>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm text-muted-foreground mb-1">High Confidence Flows</p>
                <p className="text-2xl font-bold text-high">{results.high_confidence_flows}</p>
              </div>
            </div>
            <Button className="w-full mt-4" asChild>
              <a href="/flows">View All Flows</a>
            </Button>
          </Card>
        )}
      </div>
    </div>
  );
}
