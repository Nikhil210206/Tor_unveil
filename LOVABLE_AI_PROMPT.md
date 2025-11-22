# 🔍 TOR Network Analysis Dashboard - Complete Build Prompt

Build a complete, production-ready TOR network analysis web application with a modern dark theme.

## Tech Stack
- React with TypeScript
- Tailwind CSS
- shadcn/ui components
- React Query (TanStack Query) for API calls
- Recharts for charts
- React Flow for network graph
- react-dropzone for file uploads

## Backend API
Base URL: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## Design System

### Colors
- Background: `#0f172a` (slate-950)
- Cards: `#1e293b` (slate-800)
- Primary: `#3b82f6` (blue-500)
- Success/Low: `#10b981` (green-500)
- Warning/Medium: `#f59e0b` (amber-500)
- High: `#f97316` (orange-500)
- Critical: `#ef4444` (red-500)

### Typography
- Font: Inter
- Headings: Bold, larger sizes
- Body: Regular weight

### Components Style
- Cards: rounded-lg, shadow-lg, border border-slate-700
- Buttons: rounded-md, px-4 py-2, hover effects
- Badges: rounded-full, px-3 py-1, semi-transparent backgrounds
- Inputs: dark backgrounds, focus rings

## Pages to Build

### 1. Dashboard (/)
**Layout:**
- Header with "🔍 TOR Unveil" logo and navigation
- 4 stat cards in grid:
  - Total Flows (blue icon)
  - Suspect Flows (yellow icon, shows flows with score ≥30)
  - High Confidence (orange icon, shows High category)
  - Critical Alerts (red icon, pulsing animation, shows Critical category)
- Two-column section:
  - Left: Bar chart "Confidence Score Distribution"
  - Right: Donut chart "Flows by Category"
- Bottom: Table "Top Suspect Flows" (10 rows)

**API Calls:**
```typescript
// Stats
GET http://localhost:8000/api/stats
Response: {
  total_flows: number,
  suspect_flows: number,
  critical_flows: number,
  high_flows: number,
  total_correlations: number,
  total_tor_nodes: number
}

// Top flows
GET http://localhost:8000/api/flows?min_score=60&limit=10
Response: Array<{
  id: number,
  src_ip: string,
  src_port: number,
  dst_ip: string,
  dst_port: number,
  protocol: string,
  ts_start: string,
  pkt_count: number,
  byte_count: number,
  confidence_score: number,
  confidence_category: string
}>
```

### 2. Upload & Analysis (/upload)
**Layout:**
- Large drag-and-drop zone for PCAP files (.pcap, .pcapng only)
- File info display after selection (name, size)
- Configuration section:
  - "Time Window" slider (1-30 seconds, default 10)
  - "Min Correlation Weight" slider (0.1-1.0, default 0.3)
- "Upload & Analyze" button (primary, large)
- Progress section (shows after upload starts):
  - Progress bar
  - Step indicators:
    1. Uploading file ✓
    2. Extracting flows ⏳
    3. Detecting TOR patterns ⏳
    4. Correlating flows ⏳
    5. Scoring confidence ⏳
- Results card (shows after completion):
  - TOR flows identified: X
  - Correlations created: Y
  - Flows scored: Z
  - High confidence flows: W

**API Calls:**
```typescript
// Upload
POST http://localhost:8000/api/upload
Body: FormData with 'file' field
Response: { status: string, flow_count: number }

// Analyze
POST http://localhost:8000/api/analyze
Body: { time_window: number, min_correlation_weight: number }
Response: {
  status: string,
  results: {
    tor_flows_identified: number,
    correlations_created: number,
    flows_scored: number,
    high_confidence_flows: number
  }
}
```

### 3. Flows Explorer (/flows)
**Layout:**
- Left sidebar with filters:
  - "Min Confidence Score" slider (0-100)
  - "Categories" checkboxes (Low, Medium, High, Critical)
  - "Search IP" text input
  - "Apply Filters" button
- Main area:
  - Data table with columns:
    - ID
    - Source (IP:Port)
    - Destination (IP:Port)
    - Protocol
    - Time
    - Packets
    - Bytes
    - Score (colored badge)
    - Category (colored badge)
    - Actions (View Details button)
  - Pagination controls (50 per page)
  - "Export CSV" button

**API Call:**
```typescript
GET http://localhost:8000/api/flows?min_score=0&category=High&limit=50&offset=0
```

**Badge Colors:**
- Low: green background, green text
- Medium: yellow background, yellow text
- High: orange background, orange text
- Critical: red background, red text, pulsing animation

### 4. Flow Details Modal
**Triggered by:** Clicking "View Details" in flows table

**Content:**
- Flow Information card:
  - Source: IP:Port
  - Destination: IP:Port
  - Protocol, Packets, Bytes
  - Start/End time
- TOR Indicators section with checkmarks:
  - ✓/✗ TOR Handshake Detected
  - ✓/✗ Relay Communication
  - ✓/✗ Directory Fetch
  - ✓/✗ Obfsproxy Candidate
- Confidence Breakdown (horizontal progress bars):
  - TOR Node Match: X/40
  - Timing Correlation: Y/30
  - Payload Similarity: Z/20
  - Unusual Patterns: W/10
  - Total: Score/100
- Correlated Flows mini-table
- Close button

**API Call:**
```typescript
GET http://localhost:8000/api/flows/{id}
Response: {
  flow: { /* flow details */ },
  correlations: Array<{ id, flow_id, correlated_flow_id, weight, type }>,
  payload_sample: string
}
```

### 5. Network Graph (/graph)
**Layout:**
- Full-width interactive graph area
- Controls panel (top-right):
  - Zoom In/Out buttons
  - Reset View button
  - Layout dropdown (Force-Directed, Hierarchical)
  - "Min Correlation Weight" slider
- Legend (bottom-left):
  - Node colors: Low (green), Medium (yellow), High (orange), Critical (red)
  - Edge thickness = correlation weight
- Click node → show flow details modal

**Graph Rendering:**
- Use React Flow
- Nodes: circles, size based on confidence score, color by category
- Edges: lines, thickness based on weight
- Interactive: drag nodes, zoom, pan

**API Call:**
```typescript
GET http://localhost:8000/api/graph
Response: {
  nodes: Array<{ id: number, label: string, score: number, category: string }>,
  edges: Array<{ source: number, target: number, weight: number, type: string }>
}
```

### 6. Timeline (/timeline)
**Layout:**
- Top: Time range selector (date pickers)
- Main chart: Scatter plot
  - X-axis: Time
  - Y-axis: Confidence Score (0-100)
  - Points colored by category
  - Hover shows flow details
- Bottom chart: Line chart "Flow Count Over Time"
  - X-axis: Time (hourly buckets)
  - Y-axis: Number of flows

**API Call:**
```typescript
GET http://localhost:8000/api/timeline
Response: Array<{
  time: string,
  flow_id: number,
  source: string,
  destination: string,
  score: number,
  category: string
}>
```

### 7. Reports (/reports)
**Layout:**
- "Generate New Report" section:
  - "Report Title" text input
  - "Generate PDF Report" button
  - Loading spinner (during generation)
- "Previous Reports" section:
  - Grid of report cards:
    - Title
    - Created date
    - Stats (Total Flows, Suspects, Critical)
    - "Download PDF" button
- Empty state when no reports

**API Calls:**
```typescript
// Generate
POST http://localhost:8000/api/reports/generate?title=My%20Report
Response: { status: string, report_path: string, download_url: string }

// List
GET http://localhost:8000/api/reports
Response: Array<{
  id: number,
  title: string,
  created_at: string,
  total_flows: number,
  suspect_flows: number,
  critical_alerts: number,
  file_path: string
}>

// Download
GET http://localhost:8000/api/reports/download/{filename}
Returns: PDF file
```

## Navigation

**Header (all pages):**
- Logo: "🔍 TOR Unveil" (left)
- Nav links: Dashboard | Upload | Flows | Graph | Timeline | Reports
- Live stats badge (right): "X Critical Alerts" (red, pulsing if > 0)

## React Query Setup

```typescript
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Example hook
function useStats() {
  return useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const res = await fetch('http://localhost:8000/api/stats');
      if (!res.ok) throw new Error('Failed to fetch stats');
      return res.json();
    },
    refetchInterval: 5000, // Auto-refresh every 5 seconds
  });
}
```

## Key Components to Build

### StatCard
```typescript
interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: 'blue' | 'yellow' | 'orange' | 'red';
  pulse?: boolean;
}
```
Style: Card with icon on left, value (large) and title below, colored accent border

### CategoryBadge
```typescript
interface CategoryBadgeProps {
  category: 'Low' | 'Medium' | 'High' | 'Critical';
}
```
Style: Rounded pill, semi-transparent background, colored text, pulse animation for Critical

### FlowsTable
- Sortable columns
- Pagination
- Row hover effect
- Click row → open details modal

### FileDropzone
- Drag-and-drop area with dashed border
- "Click to browse" text
- File type validation
- Show file info after selection

## Animations

- Stat cards: Number counter animation on load
- Critical badges: Pulsing animation (scale 1.0 to 1.05)
- Buttons: Hover scale (1.0 to 1.02)
- Cards: Hover shadow increase
- Page transitions: Fade in
- Loading states: Skeleton loaders or spinners

## Error Handling

- Toast notifications for errors (use sonner or react-hot-toast)
- Loading skeletons while fetching data
- Empty states with helpful messages
- Retry buttons on failed requests
- Form validation with error messages

## Responsive Design

- Mobile: Stack cards vertically, hide sidebar, hamburger menu
- Tablet: 2-column grid for stats
- Desktop: Full layout as described

## Additional Features

- Dark theme only (no toggle needed)
- Smooth scrolling
- Keyboard shortcuts (optional)
- Tooltips on hover for icons
- Copy-to-clipboard for IP addresses

## Implementation Priority

1. **Start with Dashboard**: Stats cards + flows table
2. **Add Upload page**: File upload + analysis
3. **Build Flows Explorer**: Table with filters
4. **Create Graph page**: Network visualization
5. **Add Timeline**: Charts
6. **Finish with Reports**: PDF generation

## Testing Checklist

- [ ] All API endpoints work
- [ ] File upload accepts .pcap files
- [ ] Charts render with data
- [ ] Network graph is interactive
- [ ] Pagination works
- [ ] Filters apply correctly
- [ ] PDF downloads work
- [ ] Responsive on mobile
- [ ] Loading states show
- [ ] Error messages display

## Notes

- Backend is already running at `http://localhost:8000`
- Use `http://localhost:8000/docs` to see full API documentation
- All endpoints return JSON
- CORS is enabled for localhost
- No authentication required (development mode)

Build this as a single-page application with client-side routing. Use modern React best practices, TypeScript for type safety, and ensure the UI is polished and professional. The app should feel fast, responsive, and visually impressive.
