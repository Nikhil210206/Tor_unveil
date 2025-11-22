"""
REST API for TOR Network Analysis Tool.

FastAPI-based backend that exposes all core functionality via HTTP endpoints.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from src.db.models import init_database, Flow, TorNode, Correlation, Report
from src.collector.pcap_ingest import PcapIngestor
from src.parser.tor_extractor import TorExtractor
from src.correlator.correlation_engine import CorrelationEngine
from src.scorer.confidence import ConfidenceScorer
from src.report.generator import ForensicReportGenerator

# Initialize FastAPI app
app = FastAPI(
    title="TOR Network Analysis API",
    description="REST API for analyzing network traffic and detecting TOR usage",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
db_manager = init_database(Path("tor_analysis.db"))


# Pydantic models for request/response
class AnalysisRequest(BaseModel):
    time_window: int = 10
    min_correlation_weight: float = 0.3


class FlowResponse(BaseModel):
    id: int
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str
    ts_start: str
    pkt_count: int
    byte_count: int
    confidence_score: float
    confidence_category: Optional[str]
    possible_tor_handshake: bool
    relay_comm: bool
    directory_fetch: bool
    obfsproxy_candidate: bool


class StatsResponse(BaseModel):
    total_flows: int
    suspect_flows: int
    critical_flows: int
    high_flows: int
    total_correlations: int
    total_tor_nodes: int


class CorrelationResponse(BaseModel):
    id: int
    flow_id: int
    correlated_flow_id: int
    correlation_weight: float
    correlation_type: Optional[str]


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "TOR Network Analysis API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "stats": "/api/stats",
            "flows": "/api/flows",
            "upload": "/api/upload",
            "analyze": "/api/analyze",
            "correlations": "/api/correlations",
            "reports": "/api/reports"
        }
    }


@app.get("/api/stats", response_model=StatsResponse)
async def get_stats():
    """Get overall statistics."""
    session = db_manager.get_session()
    try:
        total_flows = session.query(Flow).count()
        suspect_flows = session.query(Flow).filter(
            Flow.confidence_score >= 30.0
        ).count()
        critical_flows = session.query(Flow).filter(
            Flow.confidence_category == 'Critical'
        ).count()
        high_flows = session.query(Flow).filter(
            Flow.confidence_category == 'High'
        ).count()
        total_correlations = session.query(Correlation).count()
        total_tor_nodes = session.query(TorNode).count()
        
        return StatsResponse(
            total_flows=total_flows,
            suspect_flows=suspect_flows,
            critical_flows=critical_flows,
            high_flows=high_flows,
            total_correlations=total_correlations,
            total_tor_nodes=total_tor_nodes
        )
    finally:
        session.close()


@app.get("/api/flows", response_model=List[FlowResponse])
async def get_flows(
    min_score: float = 0.0,
    category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get flows with optional filtering."""
    session = db_manager.get_session()
    try:
        query = session.query(Flow).filter(Flow.confidence_score >= min_score)
        
        if category:
            query = query.filter(Flow.confidence_category == category)
        
        flows = query.order_by(Flow.confidence_score.desc()).offset(offset).limit(limit).all()
        
        return [
            FlowResponse(
                id=flow.id,
                src_ip=flow.src_ip,
                src_port=flow.src_port,
                dst_ip=flow.dst_ip,
                dst_port=flow.dst_port,
                protocol=flow.protocol,
                ts_start=flow.ts_start.isoformat() if flow.ts_start else "",
                pkt_count=flow.pkt_count,
                byte_count=flow.byte_count,
                confidence_score=flow.confidence_score,
                confidence_category=flow.confidence_category,
                possible_tor_handshake=flow.possible_tor_handshake or False,
                relay_comm=flow.relay_comm or False,
                directory_fetch=flow.directory_fetch or False,
                obfsproxy_candidate=flow.obfsproxy_candidate or False
            )
            for flow in flows
        ]
    finally:
        session.close()


@app.get("/api/flows/{flow_id}")
async def get_flow_detail(flow_id: int):
    """Get detailed information about a specific flow."""
    session = db_manager.get_session()
    try:
        flow = session.query(Flow).filter_by(id=flow_id).first()
        if not flow:
            raise HTTPException(status_code=404, detail="Flow not found")
        
        # Get correlations
        correlations = session.query(Correlation).filter(
            (Correlation.flow_id == flow_id) | (Correlation.correlated_flow_id == flow_id)
        ).all()
        
        return {
            "flow": FlowResponse(
                id=flow.id,
                src_ip=flow.src_ip,
                src_port=flow.src_port,
                dst_ip=flow.dst_ip,
                dst_port=flow.dst_port,
                protocol=flow.protocol,
                ts_start=flow.ts_start.isoformat() if flow.ts_start else "",
                pkt_count=flow.pkt_count,
                byte_count=flow.byte_count,
                confidence_score=flow.confidence_score,
                confidence_category=flow.confidence_category,
                possible_tor_handshake=flow.possible_tor_handshake or False,
                relay_comm=flow.relay_comm or False,
                directory_fetch=flow.directory_fetch or False,
                obfsproxy_candidate=flow.obfsproxy_candidate or False
            ),
            "correlations": [
                {
                    "id": c.id,
                    "flow_id": c.flow_id,
                    "correlated_flow_id": c.correlated_flow_id,
                    "weight": c.correlation_weight,
                    "type": c.correlation_type
                }
                for c in correlations
            ],
            "payload_sample": flow.payload_sample
        }
    finally:
        session.close()


@app.post("/api/upload")
async def upload_pcap(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and ingest PCAP file."""
    if not file.filename.endswith(('.pcap', '.pcapng')):
        raise HTTPException(status_code=400, detail="Invalid file type. Must be .pcap or .pcapng")
    
    # Save uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pcap') as tmp_file:
        shutil.copyfileobj(file.file, tmp_file)
        tmp_path = Path(tmp_file.name)
    
    try:
        # Ingest PCAP
        ingestor = PcapIngestor(db_manager, batch_size=1000)
        flow_count = ingestor.ingest_pcap(tmp_path, streaming=True)
        
        # Clean up
        tmp_path.unlink()
        
        return {
            "status": "success",
            "message": f"Ingested {flow_count} flows",
            "flow_count": flow_count
        }
    except Exception as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def run_analysis(request: AnalysisRequest):
    """Run complete TOR analysis pipeline."""
    try:
        results = {}
        
        # Step 1: Extract TOR indicators
        extractor = TorExtractor(db_manager)
        
        # Load TOR nodes if available
        tor_nodes_path = Path("data/tor_node_list.json")
        if tor_nodes_path.exists():
            extractor.load_tor_nodes_from_file(tor_nodes_path)
        
        tor_count = extractor.analyze_flows()
        results['tor_flows_identified'] = tor_count
        
        # Step 2: Correlate flows
        correlator = CorrelationEngine(db_manager, time_window_seconds=request.time_window)
        corr_count = correlator.correlate_flows(min_correlation_weight=request.min_correlation_weight)
        results['correlations_created'] = corr_count
        
        # Step 3: Score flows
        scorer = ConfidenceScorer(db_manager)
        scored_count = scorer.score_all_flows()
        results['flows_scored'] = scored_count
        
        # Get high confidence flows
        high_conf = scorer.get_high_confidence_flows(min_score=60.0)
        results['high_confidence_flows'] = len(high_conf)
        
        return {
            "status": "success",
            "message": "Analysis complete",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/correlations", response_model=List[CorrelationResponse])
async def get_correlations(limit: int = 100, offset: int = 0):
    """Get flow correlations."""
    session = db_manager.get_session()
    try:
        correlations = session.query(Correlation).order_by(
            Correlation.correlation_weight.desc()
        ).offset(offset).limit(limit).all()
        
        return [
            CorrelationResponse(
                id=c.id,
                flow_id=c.flow_id,
                correlated_flow_id=c.correlated_flow_id,
                correlation_weight=c.correlation_weight,
                correlation_type=c.correlation_type
            )
            for c in correlations
        ]
    finally:
        session.close()


@app.get("/api/graph")
async def get_correlation_graph():
    """Get correlation graph data for visualization."""
    session = db_manager.get_session()
    try:
        correlations = session.query(Correlation).all()
        
        nodes = {}
        edges = []
        
        for corr in correlations:
            # Get flow details
            flow1 = session.query(Flow).filter_by(id=corr.flow_id).first()
            flow2 = session.query(Flow).filter_by(id=corr.correlated_flow_id).first()
            
            if flow1 and flow2:
                # Add nodes
                if corr.flow_id not in nodes:
                    nodes[corr.flow_id] = {
                        "id": corr.flow_id,
                        "label": f"{flow1.src_ip}→{flow1.dst_ip}",
                        "score": flow1.confidence_score,
                        "category": flow1.confidence_category
                    }
                
                if corr.correlated_flow_id not in nodes:
                    nodes[corr.correlated_flow_id] = {
                        "id": corr.correlated_flow_id,
                        "label": f"{flow2.src_ip}→{flow2.dst_ip}",
                        "score": flow2.confidence_score,
                        "category": flow2.confidence_category
                    }
                
                # Add edge
                edges.append({
                    "source": corr.flow_id,
                    "target": corr.correlated_flow_id,
                    "weight": corr.correlation_weight,
                    "type": corr.correlation_type
                })
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }
    finally:
        session.close()


@app.get("/api/timeline")
async def get_timeline_data():
    """Get timeline data for visualization."""
    session = db_manager.get_session()
    try:
        flows = session.query(Flow).filter(
            Flow.ts_start.isnot(None),
            Flow.confidence_score >= 30.0
        ).order_by(Flow.ts_start).all()
        
        timeline_data = [
            {
                "time": flow.ts_start.isoformat(),
                "flow_id": flow.id,
                "source": flow.src_ip,
                "destination": flow.dst_ip,
                "score": flow.confidence_score,
                "category": flow.confidence_category
            }
            for flow in flows
        ]
        
        return timeline_data
    finally:
        session.close()


@app.post("/api/reports/generate")
async def generate_report(title: str = "TOR Analysis Report"):
    """Generate PDF forensic report."""
    try:
        generator = ForensicReportGenerator(db_manager)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = Path(f"reports/report_{timestamp}.pdf")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report_path = generator.generate_report(output_path, title=title)
        
        return {
            "status": "success",
            "message": "Report generated",
            "report_path": str(report_path),
            "download_url": f"/api/reports/download/{report_path.name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/download/{filename}")
async def download_report(filename: str):
    """Download generated report."""
    file_path = Path(f"reports/{filename}")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/pdf'
    )


@app.get("/api/reports")
async def list_reports():
    """List all generated reports."""
    session = db_manager.get_session()
    try:
        reports = session.query(Report).order_by(Report.created_at.desc()).all()
        
        return [
            {
                "id": r.id,
                "title": r.title,
                "created_at": r.created_at.isoformat(),
                "total_flows": r.total_flows,
                "suspect_flows": r.suspect_flows,
                "critical_alerts": r.critical_alerts,
                "file_path": r.file_path
            }
            for r in reports
        ]
    finally:
        session.close()


@app.delete("/api/database/reset")
async def reset_database():
    """Reset database (development only)."""
    try:
        db_manager.reset_database()
        return {"status": "success", "message": "Database reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
