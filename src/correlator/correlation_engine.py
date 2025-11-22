"""
Correlation engine for identifying TOR entry/exit flow patterns.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import networkx as nx

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from src.db.models import Flow, TorNode, Correlation, DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CorrelationEngine:
    """Correlate flows to identify TOR usage patterns."""
    
    def __init__(self, db_manager: DatabaseManager, time_window_seconds: int = 10):
        """
        Initialize correlation engine.
        
        Args:
            db_manager: Database manager instance
            time_window_seconds: Time window for correlation (default: 10s)
        """
        self.db_manager = db_manager
        self.time_window = timedelta(seconds=time_window_seconds)
        self.correlation_graph = nx.Graph()
    
    def correlate_flows(self, min_correlation_weight: float = 0.3) -> int:
        """
        Correlate all flows to identify TOR entry/exit patterns.
        
        Args:
            min_correlation_weight: Minimum correlation weight to persist
        
        Returns:
            Number of correlations found
        """
        session = self.db_manager.get_session()
        correlation_count = 0
        
        try:
            # Get all TOR-related flows
            tor_flows = session.query(Flow).filter(
                or_(
                    Flow.possible_tor_handshake == True,
                    Flow.relay_comm == True,
                    Flow.directory_fetch == True,
                    Flow.obfsproxy_candidate == True
                )
            ).order_by(Flow.ts_start).all()
            
            logger.info(f"Correlating {len(tor_flows)} TOR-related flows")
            
            # Get internal IP ranges (simplified: assume 10.x, 192.168.x, 172.16-31.x)
            internal_ips = self._get_internal_ips(session)
            
            # Build correlation graph
            for i, flow1 in enumerate(tor_flows):
                # Only correlate flows from internal IPs
                if not self._is_internal_ip(flow1.src_ip, internal_ips):
                    continue
                
                # Find potential correlated flows within time window
                for flow2 in tor_flows[i+1:]:
                    if not self._is_internal_ip(flow2.src_ip, internal_ips):
                        continue
                    
                    # Check time window
                    time_diff = abs((flow2.ts_start - flow1.ts_start).total_seconds())
                    if time_diff > self.time_window.total_seconds():
                        break  # Flows are sorted by time
                    
                    # Calculate correlation weight
                    weight, evidence = self._calculate_correlation(
                        flow1, flow2, session
                    )
                    
                    if weight >= min_correlation_weight:
                        # Create correlation record
                        correlation = Correlation(
                            flow_id=flow1.id,
                            correlated_flow_id=flow2.id,
                            correlation_weight=weight,
                            correlation_type=evidence.get('type', 'timing'),
                            evidence=evidence
                        )
                        session.add(correlation)
                        
                        # Add to graph
                        self.correlation_graph.add_edge(
                            flow1.id, flow2.id, weight=weight
                        )
                        
                        correlation_count += 1
            
            session.commit()
            logger.info(f"Created {correlation_count} correlations")
            return correlation_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error correlating flows: {e}")
            raise
        finally:
            session.close()
    
    def _calculate_correlation(
        self, 
        flow1: Flow, 
        flow2: Flow, 
        session: Session
    ) -> Tuple[float, Dict]:
        """
        Calculate correlation weight between two flows.
        
        Args:
            flow1: First flow
            flow2: Second flow
            session: Database session
        
        Returns:
            Tuple of (correlation_weight, evidence_dict)
        """
        weight = 0.0
        evidence = {}
        
        # Timing correlation (0-0.4)
        time_diff = abs((flow2.ts_start - flow1.ts_start).total_seconds())
        if time_diff < 1.0:
            timing_score = 0.4
        elif time_diff < 5.0:
            timing_score = 0.3
        elif time_diff < 10.0:
            timing_score = 0.2
        else:
            timing_score = 0.1
        
        weight += timing_score
        evidence['timing_diff_seconds'] = time_diff
        evidence['timing_score'] = timing_score
        
        # Check for entry/exit pattern
        # Flow1 to guard node, Flow2 to exit/target
        is_entry_exit = self._check_entry_exit_pattern(flow1, flow2, session)
        if is_entry_exit:
            weight += 0.3
            evidence['type'] = 'entry_exit'
            evidence['entry_exit_pattern'] = True
        
        # Packet size similarity (0-0.2)
        if flow1.pkt_count > 0 and flow2.pkt_count > 0:
            avg_size1 = flow1.byte_count / flow1.pkt_count
            avg_size2 = flow2.byte_count / flow2.pkt_count
            
            size_ratio = min(avg_size1, avg_size2) / max(avg_size1, avg_size2)
            size_score = size_ratio * 0.2
            
            weight += size_score
            evidence['size_similarity'] = size_score
        
        # Same source IP (different flows from same host)
        if flow1.src_ip == flow2.src_ip:
            weight += 0.1
            evidence['same_source'] = True
        
        return weight, evidence
    
    def _check_entry_exit_pattern(
        self, 
        flow1: Flow, 
        flow2: Flow, 
        session: Session
    ) -> bool:
        """
        Check if flows match TOR entry/exit pattern.
        
        Args:
            flow1: First flow
            flow2: Second flow
            session: Database session
        
        Returns:
            True if pattern matches
        """
        # Get TOR nodes
        tor_node1 = session.query(TorNode).filter_by(
            ip_address=flow1.dst_ip
        ).first()
        
        tor_node2 = session.query(TorNode).filter_by(
            ip_address=flow2.dst_ip
        ).first()
        
        # Pattern 1: Flow1 to Guard, Flow2 to Exit
        if tor_node1 and tor_node1.flags:
            if 'Guard' in tor_node1.flags:
                if tor_node2 and 'Exit' in tor_node2.flags:
                    return True
        
        # Pattern 2: Flow1 to any relay, Flow2 to non-TOR (exit traffic)
        if tor_node1 and not tor_node2:
            return True
        
        return False
    
    def _get_internal_ips(self, session: Session) -> Set[str]:
        """
        Get set of internal IP addresses from flows.
        
        Args:
            session: Database session
        
        Returns:
            Set of internal IP addresses
        """
        internal_ips = set()
        
        # Get all unique source IPs
        flows = session.query(Flow.src_ip).distinct().all()
        
        for (src_ip,) in flows:
            if self._is_internal_ip(src_ip):
                internal_ips.add(src_ip)
        
        return internal_ips
    
    def _is_internal_ip(
        self, 
        ip: str, 
        known_internal: Optional[Set[str]] = None
    ) -> bool:
        """
        Check if IP is internal/private.
        
        Args:
            ip: IP address string
            known_internal: Optional set of known internal IPs
        
        Returns:
            True if IP is internal
        """
        if known_internal and ip in known_internal:
            return True
        
        # Check common private ranges
        if ip.startswith('10.'):
            return True
        if ip.startswith('192.168.'):
            return True
        if ip.startswith('172.'):
            # Check 172.16.0.0 - 172.31.255.255
            parts = ip.split('.')
            if len(parts) >= 2:
                second_octet = int(parts[1])
                if 16 <= second_octet <= 31:
                    return True
        
        return False
    
    def get_correlation_graph(self) -> nx.Graph:
        """
        Get the correlation graph.
        
        Returns:
            NetworkX graph of correlations
        """
        return self.correlation_graph
    
    def find_suspicious_chains(self, min_chain_length: int = 2) -> List[List[int]]:
        """
        Find chains of correlated flows (potential TOR circuits).
        
        Args:
            min_chain_length: Minimum chain length
        
        Returns:
            List of flow ID chains
        """
        chains = []
        
        # Find connected components
        for component in nx.connected_components(self.correlation_graph):
            if len(component) >= min_chain_length:
                chains.append(list(component))
        
        return chains
    
    def get_flow_correlations(self, flow_id: int) -> List[Correlation]:
        """
        Get all correlations for a specific flow.
        
        Args:
            flow_id: Flow ID
        
        Returns:
            List of Correlation objects
        """
        session = self.db_manager.get_session()
        try:
            correlations = session.query(Correlation).filter(
                or_(
                    Correlation.flow_id == flow_id,
                    Correlation.correlated_flow_id == flow_id
                )
            ).all()
            return correlations
        finally:
            session.close()


if __name__ == '__main__':
    import click
    
    @click.command()
    @click.option('--db', '-d', default='tor_analysis.db',
                  help='Database path')
    @click.option('--time-window', '-t', default=10, type=int,
                  help='Time window in seconds for correlation')
    @click.option('--min-weight', '-w', default=0.3, type=float,
                  help='Minimum correlation weight')
    def main(db: str, time_window: int, min_weight: float):
        """Run correlation analysis on flows."""
        db_manager = DatabaseManager(f"sqlite:///{db}")
        
        engine = CorrelationEngine(db_manager, time_window_seconds=time_window)
        correlation_count = engine.correlate_flows(min_correlation_weight=min_weight)
        
        click.echo(f"✓ Created {correlation_count} correlations")
        
        # Find suspicious chains
        chains = engine.find_suspicious_chains()
        click.echo(f"✓ Found {len(chains)} suspicious flow chains")
    
    main()
