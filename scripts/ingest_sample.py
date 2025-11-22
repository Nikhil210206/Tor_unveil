"""
Demo script to ingest sample PCAP and run analysis.
"""

import sys
from pathlib import Path
import click

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.models import init_database
from src.collector.pcap_ingest import PcapIngestor
from src.parser.tor_extractor import TorExtractor
from src.correlator.correlation_engine import CorrelationEngine
from src.scorer.confidence import ConfidenceScorer
from src.report.generator import ForensicReportGenerator


@click.command()
@click.option('--pcap', '-p', required=True, type=click.Path(exists=True),
              help='Path to PCAP file')
@click.option('--tor-nodes', '-t', type=click.Path(exists=True),
              default='data/tor_node_list.json',
              help='Path to TOR node list JSON')
@click.option('--db', '-d', default='tor_analysis.db',
              help='Database path')
@click.option('--report', '-r', default='reports/analysis_report.pdf',
              help='Output report path')
def main(pcap: str, tor_nodes: str, db: str, report: str):
    """
    Run complete TOR analysis pipeline on sample PCAP.
    
    Example:
        python scripts/ingest_sample.py --pcap data/sample.pcap
    """
    click.echo("🔍 TOR Network Analysis - Sample Ingestion")
    click.echo("=" * 50)
    
    # Initialize database
    click.echo("\n1️⃣  Initializing database...")
    db_manager = init_database(Path(db))
    click.echo(f"   ✓ Database: {db}")
    
    # Ingest PCAP
    click.echo("\n2️⃣  Ingesting PCAP file...")
    ingestor = PcapIngestor(db_manager, batch_size=1000)
    flow_count = ingestor.ingest_pcap(Path(pcap), streaming=True)
    click.echo(f"   ✓ Ingested {flow_count:,} flows")
    
    # Load TOR nodes
    click.echo("\n3️⃣  Loading TOR nodes...")
    extractor = TorExtractor(db_manager)
    if Path(tor_nodes).exists():
        extractor.load_tor_nodes_from_file(Path(tor_nodes))
        click.echo(f"   ✓ Loaded TOR nodes from {tor_nodes}")
    else:
        click.echo(f"   ⚠️  TOR node list not found: {tor_nodes}")
    
    # Analyze flows
    click.echo("\n4️⃣  Analyzing flows for TOR indicators...")
    tor_flow_count = extractor.analyze_flows()
    click.echo(f"   ✓ Identified {tor_flow_count:,} TOR-related flows")
    
    # Correlate flows
    click.echo("\n5️⃣  Correlating flows...")
    correlator = CorrelationEngine(db_manager, time_window_seconds=10)
    correlation_count = correlator.correlate_flows(min_correlation_weight=0.3)
    click.echo(f"   ✓ Created {correlation_count:,} correlations")
    
    # Score flows
    click.echo("\n6️⃣  Calculating confidence scores...")
    scorer = ConfidenceScorer(db_manager)
    scored_count = scorer.score_all_flows()
    click.echo(f"   ✓ Scored {scored_count:,} flows")
    
    # Get high confidence flows
    high_conf = scorer.get_high_confidence_flows(min_score=60.0)
    click.echo(f"   ✓ Found {len(high_conf)} high-confidence flows")
    
    # Generate report
    click.echo("\n7️⃣  Generating forensic report...")
    generator = ForensicReportGenerator(db_manager)
    report_path = Path(report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    generator.generate_report(
        report_path,
        title=f"TOR Analysis Report - {Path(pcap).name}"
    )
    click.echo(f"   ✓ Report saved: {report_path}")
    
    # Summary
    click.echo("\n" + "=" * 50)
    click.echo("✅ Analysis Complete!")
    click.echo(f"\nSummary:")
    click.echo(f"  • Total flows: {flow_count:,}")
    click.echo(f"  • TOR flows: {tor_flow_count:,}")
    click.echo(f"  • Correlations: {correlation_count:,}")
    click.echo(f"  • High confidence: {len(high_conf)}")
    click.echo(f"\n📊 Launch dashboard: streamlit run src/web/app.py")
    click.echo(f"📄 View report: open {report_path}")


if __name__ == '__main__':
    main()
