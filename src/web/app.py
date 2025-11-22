"""
Streamlit dashboard for TOR network analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
from pyvis.network import Network
import tempfile
from pathlib import Path
from datetime import datetime
import base64

from sqlalchemy import or_, func

from src.db.models import Flow, TorNode, Correlation, Alert, DatabaseManager, init_database
from src.collector.pcap_ingest import PcapIngestor
from src.parser.tor_extractor import TorExtractor
from src.correlator.correlation_engine import CorrelationEngine
from src.scorer.confidence import ConfidenceScorer
from src.report.generator import ForensicReportGenerator

# Page configuration
st.set_page_config(
    page_title="TOR Network Analysis",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .critical-alert {
        background-color: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    .high-alert {
        background-color: #ff8800;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_manager():
    """Get cached database manager."""
    return init_database(Path("tor_analysis.db"))


def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">🔍 TOR Network Analysis Dashboard</div>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/667eea/ffffff?text=TOR+Unveil", 
                use_container_width=True)
        st.title("Navigation")
        
        page = st.radio(
            "Select View",
            ["📊 Overview", "📁 Data Ingestion", "🔍 Flow Analysis", 
             "🕸️ Network Graph", "📈 Timeline", "📄 Reports"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Database stats
        st.subheader("Database Stats")
        db_manager = get_db_manager()
        session = db_manager.get_session()
        
        try:
            total_flows = session.query(Flow).count()
            total_nodes = session.query(TorNode).count()
            total_correlations = session.query(Correlation).count()
            
            st.metric("Total Flows", f"{total_flows:,}")
            st.metric("TOR Nodes", f"{total_nodes:,}")
            st.metric("Correlations", f"{total_correlations:,}")
        finally:
            session.close()
    
    # Route to pages
    if page == "📊 Overview":
        show_overview()
    elif page == "📁 Data Ingestion":
        show_data_ingestion()
    elif page == "🔍 Flow Analysis":
        show_flow_analysis()
    elif page == "🕸️ Network Graph":
        show_network_graph()
    elif page == "📈 Timeline":
        show_timeline()
    elif page == "📄 Reports":
        show_reports()


def show_overview():
    """Show overview dashboard."""
    st.header("📊 Analysis Overview")
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
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
        
        with col1:
            st.metric("Total Flows", f"{total_flows:,}")
        with col2:
            st.metric("Suspect Flows", f"{suspect_flows:,}", 
                     delta=f"{(suspect_flows/total_flows*100):.1f}%" if total_flows > 0 else "0%")
        with col3:
            st.metric("Critical", f"{critical_flows:,}", delta="⚠️")
        with col4:
            st.metric("High", f"{high_flows:,}", delta="⚠️")
        
        st.divider()
        
        # Confidence distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Confidence Score Distribution")
            
            # Get flows with scores
            flows_df = pd.read_sql(
                session.query(Flow.confidence_score, Flow.confidence_category)
                .filter(Flow.confidence_score > 0)
                .statement,
                session.bind
            )
            
            if not flows_df.empty:
                fig = px.histogram(
                    flows_df,
                    x='confidence_score',
                    nbins=20,
                    color='confidence_category',
                    title="Flow Confidence Scores",
                    labels={'confidence_score': 'Confidence Score', 'count': 'Number of Flows'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No scored flows available. Run analysis first.")
        
        with col2:
            st.subheader("Confidence Categories")
            
            category_counts = session.query(
                Flow.confidence_category,
                func.count(Flow.id)
            ).filter(
                Flow.confidence_category.isnot(None)
            ).group_by(Flow.confidence_category).all()
            
            if category_counts:
                category_df = pd.DataFrame(
                    category_counts,
                    columns=['Category', 'Count']
                )
                
                fig = px.pie(
                    category_df,
                    values='Count',
                    names='Category',
                    title="Flows by Category",
                    color='Category',
                    color_discrete_map={
                        'Low': '#90EE90',
                        'Medium': '#FFD700',
                        'High': '#FF8C00',
                        'Critical': '#FF0000'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Top suspect flows
        st.divider()
        st.subheader("🚨 Top Suspect Flows")
        
        top_flows = session.query(Flow).filter(
            Flow.confidence_score >= 60.0
        ).order_by(Flow.confidence_score.desc()).limit(10).all()
        
        if top_flows:
            flows_data = []
            for flow in top_flows:
                flows_data.append({
                    'ID': flow.id,
                    'Source': f"{flow.src_ip}:{flow.src_port}",
                    'Destination': f"{flow.dst_ip}:{flow.dst_port}",
                    'Protocol': flow.protocol,
                    'Score': f"{flow.confidence_score:.1f}",
                    'Category': flow.confidence_category,
                    'Packets': flow.pkt_count,
                    'Bytes': flow.byte_count
                })
            
            df = pd.DataFrame(flows_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No high-confidence flows detected.")
        
    finally:
        session.close()


def show_data_ingestion():
    """Show data ingestion interface."""
    st.header("📁 Data Ingestion")
    
    tab1, tab2 = st.tabs(["Upload PCAP", "Load TOR Nodes"])
    
    with tab1:
        st.subheader("Upload PCAP File")
        
        uploaded_file = st.file_uploader(
            "Choose a PCAP file",
            type=['pcap', 'pcapng'],
            help="Upload network capture file for analysis"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            batch_size = st.number_input("Batch Size", min_value=100, max_value=10000, 
                                        value=1000, step=100)
        with col2:
            streaming = st.checkbox("Use Streaming Mode", value=True,
                                   help="Recommended for large files")
        
        if uploaded_file is not None:
            if st.button("🚀 Ingest PCAP", type="primary"):
                with st.spinner("Ingesting PCAP file..."):
                    # Save uploaded file temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pcap') as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = Path(tmp_file.name)
                    
                    try:
                        db_manager = get_db_manager()
                        ingestor = PcapIngestor(db_manager, batch_size=batch_size)
                        flow_count = ingestor.ingest_pcap(tmp_path, streaming=streaming)
                        
                        st.success(f"✅ Successfully ingested {flow_count:,} flows!")
                        
                        # Auto-run analysis
                        if st.checkbox("Run TOR analysis automatically", value=True):
                            run_tor_analysis()
                        
                    except Exception as e:
                        st.error(f"Error ingesting PCAP: {e}")
                    finally:
                        tmp_path.unlink()
    
    with tab2:
        st.subheader("Load TOR Node List")
        
        uploaded_json = st.file_uploader(
            "Choose TOR node list JSON file",
            type=['json'],
            help="Upload JSON file with TOR relay information"
        )
        
        if uploaded_json is not None:
            if st.button("📥 Load TOR Nodes", type="primary"):
                with st.spinner("Loading TOR nodes..."):
                    try:
                        import json
                        
                        # Save temporarily
                        with tempfile.NamedTemporaryFile(mode='w', delete=False, 
                                                        suffix='.json') as tmp_file:
                            tmp_file.write(uploaded_json.getvalue().decode('utf-8'))
                            tmp_path = Path(tmp_file.name)
                        
                        db_manager = get_db_manager()
                        extractor = TorExtractor(db_manager)
                        extractor.load_tor_nodes_from_file(tmp_path)
                        
                        st.success("✅ TOR nodes loaded successfully!")
                        
                        tmp_path.unlink()
                        
                    except Exception as e:
                        st.error(f"Error loading TOR nodes: {e}")
        
        st.divider()
        
        if st.button("🌐 Download Latest TOR Consensus"):
            with st.spinner("Downloading TOR consensus..."):
                try:
                    from src.parser.tor_extractor import download_tor_consensus
                    
                    output_path = Path("data/tor_node_list.json")
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    node_count = download_tor_consensus(output_path)
                    st.success(f"✅ Downloaded {node_count} TOR nodes!")
                    
                except Exception as e:
                    st.error(f"Error downloading consensus: {e}")


def run_tor_analysis():
    """Run complete TOR analysis pipeline."""
    db_manager = get_db_manager()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Extract TOR indicators
        status_text.text("Extracting TOR indicators...")
        progress_bar.progress(25)
        
        extractor = TorExtractor(db_manager)
        tor_count = extractor.analyze_flows()
        
        # Step 2: Correlate flows
        status_text.text("Correlating flows...")
        progress_bar.progress(50)
        
        correlator = CorrelationEngine(db_manager)
        corr_count = correlator.correlate_flows()
        
        # Step 3: Score flows
        status_text.text("Calculating confidence scores...")
        progress_bar.progress(75)
        
        scorer = ConfidenceScorer(db_manager)
        scored_count = scorer.score_all_flows()
        
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        
        st.success(f"""
        ✅ Analysis Complete!
        - {tor_count} TOR-related flows identified
        - {corr_count} correlations found
        - {scored_count} flows scored
        """)
        
    except Exception as e:
        st.error(f"Error during analysis: {e}")


def show_flow_analysis():
    """Show detailed flow analysis."""
    st.header("🔍 Flow Analysis")
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_score = st.slider("Minimum Confidence Score", 0.0, 100.0, 30.0)
        with col2:
            category_filter = st.multiselect(
                "Categories",
                ['Low', 'Medium', 'High', 'Critical'],
                default=['High', 'Critical']
            )
        with col3:
            limit = st.number_input("Max Results", min_value=10, max_value=1000, 
                                   value=100, step=10)
        
        # Query flows
        query = session.query(Flow).filter(Flow.confidence_score >= min_score)
        
        if category_filter:
            query = query.filter(Flow.confidence_category.in_(category_filter))
        
        flows = query.order_by(Flow.confidence_score.desc()).limit(limit).all()
        
        st.write(f"Found {len(flows)} flows matching criteria")
        
        if flows:
            # Create DataFrame
            flows_data = []
            for flow in flows:
                flows_data.append({
                    'ID': flow.id,
                    'Source IP': flow.src_ip,
                    'Src Port': flow.src_port,
                    'Dest IP': flow.dst_ip,
                    'Dst Port': flow.dst_port,
                    'Protocol': flow.protocol,
                    'Start Time': flow.ts_start.strftime('%Y-%m-%d %H:%M:%S'),
                    'Packets': flow.pkt_count,
                    'Bytes': flow.byte_count,
                    'Score': f"{flow.confidence_score:.1f}",
                    'Category': flow.confidence_category
                })
            
            df = pd.DataFrame(flows_data)
            
            # Display table
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Flow detail viewer
            st.divider()
            st.subheader("Flow Details")
            
            flow_id = st.selectbox("Select Flow ID", [f.id for f in flows])
            
            if flow_id:
                selected_flow = session.query(Flow).filter_by(id=flow_id).first()
                
                if selected_flow:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Flow Information**")
                        st.write(f"- Source: {selected_flow.src_ip}:{selected_flow.src_port}")
                        st.write(f"- Destination: {selected_flow.dst_ip}:{selected_flow.dst_port}")
                        st.write(f"- Protocol: {selected_flow.protocol}")
                        st.write(f"- Packets: {selected_flow.pkt_count}")
                        st.write(f"- Bytes: {selected_flow.byte_count}")
                        
                        st.write("**TOR Indicators**")
                        st.write(f"- Handshake: {'✅' if selected_flow.possible_tor_handshake else '❌'}")
                        st.write(f"- Relay Comm: {'✅' if selected_flow.relay_comm else '❌'}")
                        st.write(f"- Directory: {'✅' if selected_flow.directory_fetch else '❌'}")
                        st.write(f"- Obfsproxy: {'✅' if selected_flow.obfsproxy_candidate else '❌'}")
                    
                    with col2:
                        st.write("**Confidence Analysis**")
                        st.write(f"- Score: {selected_flow.confidence_score:.1f}")
                        st.write(f"- Category: {selected_flow.confidence_category}")
                        
                        # Get correlations
                        correlations = session.query(Correlation).filter(
                            or_(
                                Correlation.flow_id == flow_id,
                                Correlation.correlated_flow_id == flow_id
                            )
                        ).all()
                        
                        st.write(f"**Correlations: {len(correlations)}**")
                        for corr in correlations[:5]:
                            other_id = corr.correlated_flow_id if corr.flow_id == flow_id else corr.flow_id
                            st.write(f"- Flow {other_id} (weight: {corr.correlation_weight:.2f})")
                    
                    # Payload viewer
                    if selected_flow.payload_sample:
                        st.write("**Payload Sample (first 512 bytes)**")
                        try:
                            payload = base64.b64decode(selected_flow.payload_sample)
                            st.code(payload.hex(), language='text')
                        except:
                            st.write("Could not decode payload")
        
        else:
            st.info("No flows match the selected criteria.")
    
    finally:
        session.close()


def show_network_graph():
    """Show network correlation graph."""
    st.header("🕸️ Network Correlation Graph")
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        # Get correlations
        correlations = session.query(Correlation).all()
        
        if not correlations:
            st.info("No correlations available. Run analysis first.")
            return
        
        # Build NetworkX graph
        G = nx.Graph()
        
        for corr in correlations:
            flow1 = session.query(Flow).filter_by(id=corr.flow_id).first()
            flow2 = session.query(Flow).filter_by(id=corr.correlated_flow_id).first()
            
            if flow1 and flow2:
                label1 = f"{flow1.src_ip}→{flow1.dst_ip}"
                label2 = f"{flow2.src_ip}→{flow2.dst_ip}"
                
                G.add_node(corr.flow_id, label=label1, 
                          score=flow1.confidence_score,
                          category=flow1.confidence_category)
                G.add_node(corr.correlated_flow_id, label=label2,
                          score=flow2.confidence_score,
                          category=flow2.confidence_category)
                
                G.add_edge(corr.flow_id, corr.correlated_flow_id, 
                          weight=corr.correlation_weight)
        
        st.write(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Create Pyvis network
        net = Network(height="600px", width="100%", bgcolor="#222222", 
                     font_color="white")
        
        # Add nodes with colors based on category
        color_map = {
            'Low': '#90EE90',
            'Medium': '#FFD700',
            'High': '#FF8C00',
            'Critical': '#FF0000'
        }
        
        for node, data in G.nodes(data=True):
            color = color_map.get(data.get('category', 'Low'), '#888888')
            net.add_node(node, label=data.get('label', str(node)), 
                        color=color, title=f"Score: {data.get('score', 0):.1f}")
        
        for edge in G.edges(data=True):
            net.add_edge(edge[0], edge[1], 
                        value=edge[2].get('weight', 1) * 10)
        
        # Save and display
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w') as tmp_file:
            net.save_graph(tmp_file.name)
            tmp_path = Path(tmp_file.name)
        
        with open(tmp_path, 'r') as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=650)
        
        tmp_path.unlink()
        
    finally:
        session.close()


def show_timeline():
    """Show timeline visualization."""
    st.header("📈 Flow Timeline")
    
    db_manager = get_db_manager()
    session = db_manager.get_session()
    
    try:
        # Get flows with timestamps
        flows = session.query(Flow).filter(
            Flow.ts_start.isnot(None),
            Flow.confidence_score >= 30.0
        ).order_by(Flow.ts_start).all()
        
        if not flows:
            st.info("No flows available for timeline.")
            return
        
        # Create timeline data
        timeline_data = []
        for flow in flows:
            timeline_data.append({
                'Time': flow.ts_start,
                'Flow ID': flow.id,
                'Source': flow.src_ip,
                'Destination': flow.dst_ip,
                'Score': flow.confidence_score,
                'Category': flow.confidence_category or 'Unknown'
            })
        
        df = pd.DataFrame(timeline_data)
        
        # Scatter plot
        fig = px.scatter(
            df,
            x='Time',
            y='Score',
            color='Category',
            hover_data=['Flow ID', 'Source', 'Destination'],
            title="Flow Confidence Over Time",
            color_discrete_map={
                'Low': '#90EE90',
                'Medium': '#FFD700',
                'High': '#FF8C00',
                'Critical': '#FF0000'
            }
        )
        
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Flow count over time
        df['Hour'] = pd.to_datetime(df['Time']).dt.floor('H')
        hourly_counts = df.groupby('Hour').size().reset_index(name='Count')
        
        fig2 = px.line(
            hourly_counts,
            x='Hour',
            y='Count',
            title="Flow Count Over Time (Hourly)",
            markers=True
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
    finally:
        session.close()


def show_reports():
    """Show report generation interface."""
    st.header("📄 Forensic Reports")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Generate New Report")
        
        report_title = st.text_input(
            "Report Title",
            value=f"TOR Analysis Report - {datetime.now().strftime('%Y-%m-%d')}"
        )
        
        include_viz = st.checkbox("Include Visualizations", value=False,
                                 help="Note: Requires pre-generated visualization images")
        
        if st.button("📝 Generate PDF Report", type="primary"):
            with st.spinner("Generating report..."):
                try:
                    db_manager = get_db_manager()
                    generator = ForensicReportGenerator(db_manager)
                    
                    output_path = Path(f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    report_path = generator.generate_report(
                        output_path,
                        title=report_title,
                        include_visualizations=include_viz
                    )
                    
                    st.success(f"✅ Report generated: {report_path}")
                    
                    # Provide download link
                    with open(report_path, 'rb') as f:
                        st.download_button(
                            label="📥 Download Report",
                            data=f,
                            file_name=report_path.name,
                            mime="application/pdf"
                        )
                    
                except Exception as e:
                    st.error(f"Error generating report: {e}")
    
    with col2:
        st.subheader("Previous Reports")
        
        db_manager = get_db_manager()
        session = db_manager.get_session()
        
        try:
            from src.db.models import Report
            
            reports = session.query(Report).order_by(
                Report.created_at.desc()
            ).limit(10).all()
            
            if reports:
                for report in reports:
                    with st.expander(f"📄 {report.title}"):
                        st.write(f"**Created:** {report.created_at.strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Flows:** {report.total_flows}")
                        st.write(f"**Suspects:** {report.suspect_flows}")
                        st.write(f"**Critical:** {report.critical_alerts}")
                        
                        if report.file_path and Path(report.file_path).exists():
                            with open(report.file_path, 'rb') as f:
                                st.download_button(
                                    label="Download",
                                    data=f,
                                    file_name=Path(report.file_path).name,
                                    mime="application/pdf",
                                    key=f"download_{report.id}"
                                )
            else:
                st.info("No reports generated yet.")
        
        finally:
            session.close()


if __name__ == '__main__':
    main()
