"""
PDF forensic report generator.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from sqlalchemy import func

from src.db.models import Flow, Alert, Correlation, Report, DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ForensicReportGenerator:
    """Generate PDF forensic reports."""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize report generator.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Alert style
        self.styles.add(ParagraphStyle(
            name='Alert',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            leftIndent=20
        ))
    
    def generate_report(
        self,
        output_path: Path,
        title: str = "TOR Network Analysis - Forensic Report",
        include_visualizations: bool = False,
        viz_paths: Optional[List[Path]] = None
    ) -> Path:
        """
        Generate comprehensive forensic report.
        
        Args:
            output_path: Path to save PDF report
            title: Report title
            include_visualizations: Include visualization images
            viz_paths: Paths to visualization images
        
        Returns:
            Path to generated report
        """
        logger.info(f"Generating forensic report", output=str(output_path))
        
        # Create output directory
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Title page
        story.extend(self._build_title_page(title))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._build_executive_summary())
        story.append(Spacer(1, 0.2 * inch))
        
        # Statistics
        story.extend(self._build_statistics())
        story.append(Spacer(1, 0.2 * inch))
        
        # High-confidence flows
        story.extend(self._build_suspect_flows_table())
        story.append(PageBreak())
        
        # Correlations
        story.extend(self._build_correlations_section())
        story.append(Spacer(1, 0.2 * inch))
        
        # Visualizations
        if include_visualizations and viz_paths:
            story.extend(self._build_visualizations_section(viz_paths))
            story.append(PageBreak())
        
        # Recommendations
        story.extend(self._build_recommendations())
        
        # Build PDF
        doc.build(story)
        
        # Save report metadata to database
        self._save_report_metadata(output_path, title)
        
        logger.info(f"Report generated successfully", path=str(output_path))
        return output_path
    
    def _build_title_page(self, title: str) -> List:
        """Build title page content."""
        content = []
        
        content.append(Spacer(1, 2 * inch))
        content.append(Paragraph(title, self.styles['CustomTitle']))
        content.append(Spacer(1, 0.5 * inch))
        
        # Metadata
        metadata_text = f"""
        <para align=center>
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Classification:</b> CONFIDENTIAL<br/>
        <b>Tool:</b> TOR Network Analysis Tool v1.0
        </para>
        """
        content.append(Paragraph(metadata_text, self.styles['Normal']))
        
        return content
    
    def _build_executive_summary(self) -> List:
        """Build executive summary section."""
        content = []
        
        content.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        session = self.db_manager.get_session()
        try:
            # Get statistics
            total_flows = session.query(Flow).count()
            suspect_flows = session.query(Flow).filter(
                Flow.confidence_score >= 30.0
            ).count()
            critical_flows = session.query(Flow).filter(
                Flow.confidence_category == 'Critical'
            ).count()
            
            summary_text = f"""
            This report presents the results of network traffic analysis focused on 
            detecting TOR (The Onion Router) usage patterns. The analysis examined 
            <b>{total_flows:,}</b> network flows and identified <b>{suspect_flows:,}</b> 
            flows with medium or higher confidence of TOR-related activity.
            <br/><br/>
            <b>Key Findings:</b><br/>
            • {critical_flows} flows classified as CRITICAL confidence<br/>
            • Multiple correlated flow patterns detected<br/>
            • Evidence of potential TOR circuit establishment<br/>
            <br/>
            <b>Recommendation:</b> Immediate investigation of high-confidence flows 
            and source hosts is recommended.
            """
            
            content.append(Paragraph(summary_text, self.styles['Normal']))
            
        finally:
            session.close()
        
        return content
    
    def _build_statistics(self) -> List:
        """Build statistics section."""
        content = []
        
        content.append(Paragraph("Analysis Statistics", self.styles['SectionHeader']))
        
        session = self.db_manager.get_session()
        try:
            # Gather statistics
            total_flows = session.query(Flow).count()
            
            stats_by_category = session.query(
                Flow.confidence_category,
                func.count(Flow.id)
            ).group_by(Flow.confidence_category).all()
            
            total_correlations = session.query(Correlation).count()
            
            # Build table
            data = [
                ['Metric', 'Value'],
                ['Total Flows Analyzed', f'{total_flows:,}'],
                ['Total Correlations', f'{total_correlations:,}']
            ]
            
            for category, count in stats_by_category:
                if category:
                    data.append([f'{category} Confidence Flows', f'{count:,}'])
            
            table = Table(data, colWidths=[3.5 * inch, 2 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(table)
            
        finally:
            session.close()
        
        return content
    
    def _build_suspect_flows_table(self) -> List:
        """Build table of high-confidence suspect flows."""
        content = []
        
        content.append(Paragraph("High-Confidence Suspect Flows", 
                                self.styles['SectionHeader']))
        
        session = self.db_manager.get_session()
        try:
            # Get high-confidence flows
            flows = session.query(Flow).filter(
                Flow.confidence_score >= 60.0
            ).order_by(Flow.confidence_score.desc()).limit(20).all()
            
            if not flows:
                content.append(Paragraph(
                    "No high-confidence flows detected.",
                    self.styles['Normal']
                ))
                return content
            
            # Build table
            data = [['Flow ID', 'Source', 'Destination', 'Score', 'Category']]
            
            for flow in flows:
                data.append([
                    str(flow.id),
                    f"{flow.src_ip}:{flow.src_port}",
                    f"{flow.dst_ip}:{flow.dst_port}",
                    f"{flow.confidence_score:.1f}",
                    flow.confidence_category or 'N/A'
                ])
            
            table = Table(data, colWidths=[0.6*inch, 1.8*inch, 1.8*inch, 0.8*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            content.append(table)
            
        finally:
            session.close()
        
        return content
    
    def _build_correlations_section(self) -> List:
        """Build correlations section."""
        content = []
        
        content.append(Paragraph("Flow Correlations", self.styles['SectionHeader']))
        
        session = self.db_manager.get_session()
        try:
            # Get top correlations
            correlations = session.query(Correlation).order_by(
                Correlation.correlation_weight.desc()
            ).limit(10).all()
            
            if not correlations:
                content.append(Paragraph(
                    "No significant correlations detected.",
                    self.styles['Normal']
                ))
                return content
            
            text = """
            The following flow pairs show strong correlation patterns, 
            potentially indicating TOR circuit activity:
            """
            content.append(Paragraph(text, self.styles['Normal']))
            content.append(Spacer(1, 0.1 * inch))
            
            # Build table
            data = [['Flow 1', 'Flow 2', 'Weight', 'Type']]
            
            for corr in correlations:
                data.append([
                    str(corr.flow_id),
                    str(corr.correlated_flow_id),
                    f"{corr.correlation_weight:.2f}",
                    corr.correlation_type or 'N/A'
                ])
            
            table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.2*inch, 1.8*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(table)
            
        finally:
            session.close()
        
        return content
    
    def _build_visualizations_section(self, viz_paths: List[Path]) -> List:
        """Build visualizations section."""
        content = []
        
        content.append(Paragraph("Network Visualizations", 
                                self.styles['SectionHeader']))
        
        for viz_path in viz_paths:
            if viz_path.exists():
                try:
                    img = RLImage(str(viz_path), width=6*inch, height=4*inch)
                    content.append(img)
                    content.append(Spacer(1, 0.2 * inch))
                except Exception as e:
                    logger.warning(f"Could not include visualization: {e}")
        
        return content
    
    def _build_recommendations(self) -> List:
        """Build recommendations section."""
        content = []
        
        content.append(Paragraph("Recommendations", self.styles['SectionHeader']))
        
        session = self.db_manager.get_session()
        try:
            # Get critical flows
            critical_flows = session.query(Flow).filter(
                Flow.confidence_category == 'Critical'
            ).all()
            
            # Get unique source IPs
            source_ips = set(flow.src_ip for flow in critical_flows)
            
            recommendations = f"""
            <b>Immediate Actions:</b><br/>
            1. Investigate the following source hosts for TOR usage:<br/>
            """
            
            for ip in list(source_ips)[:10]:
                recommendations += f"   • {ip}<br/>"
            
            recommendations += """
            <br/>
            2. Review firewall rules to block known TOR relay IPs if policy requires<br/>
            3. Implement DPI (Deep Packet Inspection) for encrypted traffic analysis<br/>
            4. Monitor for obfsproxy and pluggable transport usage<br/>
            <br/>
            <b>Long-term Measures:</b><br/>
            • Deploy continuous network monitoring for TOR indicators<br/>
            • Implement user awareness training on acceptable use policies<br/>
            • Consider network segmentation for sensitive systems<br/>
            <br/>
            <b>Legal Notice:</b><br/>
            All investigation activities must comply with applicable laws and regulations.
            Consult legal counsel before taking action against users.
            """
            
            content.append(Paragraph(recommendations, self.styles['Normal']))
            
        finally:
            session.close()
        
        return content
    
    def _save_report_metadata(self, output_path: Path, title: str):
        """Save report metadata to database."""
        session = self.db_manager.get_session()
        try:
            # Get statistics
            total_flows = session.query(Flow).count()
            suspect_flows = session.query(Flow).filter(
                Flow.confidence_score >= 30.0
            ).count()
            critical_alerts = session.query(Flow).filter(
                Flow.confidence_category == 'Critical'
            ).count()
            
            report = Report(
                title=title,
                report_type='forensic',
                file_path=str(output_path),
                summary=f"Analysis of {total_flows} flows, {suspect_flows} suspects",
                total_flows=total_flows,
                suspect_flows=suspect_flows,
                critical_alerts=critical_alerts
            )
            
            session.add(report)
            session.commit()
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving report metadata: {e}")
        finally:
            session.close()


if __name__ == '__main__':
    import click
    
    @click.command()
    @click.option('--db', '-d', default='tor_analysis.db',
                  help='Database path')
    @click.option('--output', '-o', default='reports/forensic_report.pdf',
                  help='Output PDF path')
    @click.option('--title', '-t', 
                  default='TOR Network Analysis - Forensic Report',
                  help='Report title')
    def main(db: str, output: str, title: str):
        """Generate forensic PDF report."""
        db_manager = DatabaseManager(f"sqlite:///{db}")
        
        generator = ForensicReportGenerator(db_manager)
        output_path = Path(output)
        
        report_path = generator.generate_report(output_path, title=title)
        click.echo(f"✓ Report generated: {report_path}")
    
    main()
