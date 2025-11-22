const API_BASE_URL = 'https://tor-unveil-dil6.onrender.com';

export interface Stats {
  total_flows: number;
  suspect_flows: number;
  critical_flows: number;
  high_flows: number;
  total_correlations: number;
  total_tor_nodes: number;
}

export interface Flow {
  id: number;
  src_ip: string;
  src_port: number;
  dst_ip: string;
  dst_port: number;
  protocol: string;
  ts_start: string;
  pkt_count: number;
  byte_count: number;
  confidence_score: number;
  confidence_category: string;
}

export interface FlowDetail extends Flow {
  ts_end?: string;
  tor_handshake_detected?: boolean;
  relay_communication?: boolean;
  directory_fetch?: boolean;
  obfsproxy_candidate?: boolean;
  payload_sample?: string;
}

export interface Correlation {
  id: number;
  flow_id: number;
  correlated_flow_id: number;
  weight: number;
  type: string;
}

export interface FlowDetailResponse {
  flow: FlowDetail;
  correlations: Correlation[];
  payload_sample?: string;
}

export interface GraphNode {
  id: number;
  label: string;
  score: number;
  category: string;
}

export interface GraphEdge {
  source: number;
  target: number;
  weight: number;
  type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface TimelinePoint {
  time: string;
  flow_id: number;
  source: string;
  destination: string;
  score: number;
  category: string;
}

export interface Report {
  id: number;
  title: string;
  created_at: string;
  total_flows: number;
  suspect_flows: number;
  critical_alerts: number;
  file_path: string;
}

export interface AnalysisResults {
  tor_flows_identified: number;
  correlations_created: number;
  flows_scored: number;
  high_confidence_flows: number;
}

export const api = {
  async getStats(): Promise<Stats> {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    if (!response.ok) throw new Error('Failed to fetch stats');
    return response.json();
  },

  async getFlows(params?: {
    min_score?: number;
    category?: string;
    limit?: number;
    offset?: number;
    search_ip?: string;
  }): Promise<Flow[]> {
    const queryParams = new URLSearchParams();
    if (params?.min_score !== undefined) queryParams.append('min_score', params.min_score.toString());
    if (params?.category) queryParams.append('category', params.category);
    if (params?.limit) queryParams.append('limit', params.limit.toString());
    if (params?.offset) queryParams.append('offset', params.offset.toString());
    if (params?.search_ip) queryParams.append('search_ip', params.search_ip);

    const response = await fetch(`${API_BASE_URL}/api/flows?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch flows');
    return response.json();
  },

  async getFlowDetail(id: number): Promise<FlowDetailResponse> {
    const response = await fetch(`${API_BASE_URL}/api/flows/${id}`);
    if (!response.ok) throw new Error('Failed to fetch flow details');
    return response.json();
  },

  async uploadFile(file: File): Promise<{ status: string; flow_count: number }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) throw new Error('Failed to upload file');
    return response.json();
  },

  async analyzeFlows(config: {
    time_window: number;
    min_correlation_weight: number;
  }): Promise<{ status: string; results: AnalysisResults }> {
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error('Failed to analyze flows');
    return response.json();
  },

  async getGraphData(): Promise<GraphData> {
    const response = await fetch(`${API_BASE_URL}/api/graph`);
    if (!response.ok) throw new Error('Failed to fetch graph data');
    return response.json();
  },

  async getTimeline(): Promise<TimelinePoint[]> {
    const response = await fetch(`${API_BASE_URL}/api/timeline`);
    if (!response.ok) throw new Error('Failed to fetch timeline data');
    return response.json();
  },

  async getReports(): Promise<Report[]> {
    const response = await fetch(`${API_BASE_URL}/api/reports`);
    if (!response.ok) throw new Error('Failed to fetch reports');
    return response.json();
  },

  async generateReport(title: string): Promise<{
    status: string;
    report_path: string;
    download_url: string;
  }> {
    const response = await fetch(
      `${API_BASE_URL}/api/reports/generate?title=${encodeURIComponent(title)}`,
      { method: 'POST' }
    );
    if (!response.ok) throw new Error('Failed to generate report');
    return response.json();
  },

  async downloadReport(filename: string): Promise<Blob> {
    const response = await fetch(`${API_BASE_URL}/api/reports/download/${filename}`);
    if (!response.ok) throw new Error('Failed to download report');
    return response.blob();
  },
};
