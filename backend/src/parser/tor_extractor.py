"""
TOR traffic extraction and detection using heuristics and Stem.
"""

import base64
import json
from typing import List, Dict, Optional, Set
from pathlib import Path
import struct

from sqlalchemy.orm import Session
from stem.descriptor.remote import DescriptorDownloader
from stem.descriptor import parse_file

from src.db.models import Flow, TorNode, DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TorExtractor:
    """Extract and identify TOR-related traffic patterns."""
    
    # Known TOR ports
    TOR_PORTS = {9001, 9030, 9050, 9051, 9150}
    
    # TLS handshake patterns
    TLS_CLIENT_HELLO = b'\x16\x03'  # TLS handshake, version 3.x
    
    # TOR-specific patterns (simplified heuristics)
    TOR_HANDSHAKE_PATTERNS = [
        b'\x00\x00\x00',  # TOR cell header pattern
        b'\x03\x00',      # Version 3 handshake
    ]
    
    def __init__(self, db_manager: DatabaseManager, tor_nodes: Optional[List[Dict]] = None):
        """
        Initialize TOR extractor.
        
        Args:
            db_manager: Database manager instance
            tor_nodes: Optional list of TOR node dictionaries
        """
        self.db_manager = db_manager
        self.tor_node_ips: Set[str] = set()
        
        if tor_nodes:
            self._load_tor_nodes(tor_nodes)
    
    def _load_tor_nodes(self, tor_nodes: List[Dict]):
        """
        Load TOR nodes into database and cache.
        
        Args:
            tor_nodes: List of TOR node dictionaries
        """
        session = self.db_manager.get_session()
        try:
            for node_data in tor_nodes:
                # Check if node already exists
                existing = session.query(TorNode).filter_by(
                    ip_address=node_data['ip_address']
                ).first()
                
                if not existing:
                    node = TorNode(
                        ip_address=node_data['ip_address'],
                        port=node_data.get('port', 9001),
                        fingerprint=node_data.get('fingerprint'),
                        nickname=node_data.get('nickname'),
                        flags=node_data.get('flags', []),
                        country_code=node_data.get('country_code'),
                        asn=node_data.get('asn'),
                        bandwidth=node_data.get('bandwidth')
                    )
                    session.add(node)
                    self.tor_node_ips.add(node_data['ip_address'])
            
            session.commit()
            logger.info(f"Loaded {len(tor_nodes)} TOR nodes")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error loading TOR nodes: {e}")
            raise
        finally:
            session.close()
    
    def load_tor_nodes_from_file(self, file_path: Path):
        """
        Load TOR nodes from JSON file.
        
        Args:
            file_path: Path to JSON file containing TOR nodes
        """
        with open(file_path, 'r') as f:
            tor_nodes = json.load(f)
        
        self._load_tor_nodes(tor_nodes)
    
    def analyze_flows(self, batch_size: int = 100) -> int:
        """
        Analyze all flows in database for TOR indicators.
        
        Args:
            batch_size: Number of flows to process per batch
        
        Returns:
            Number of flows marked as TOR-related
        """
        session = self.db_manager.get_session()
        tor_flow_count = 0
        
        try:
            # Get total flow count
            total_flows = session.query(Flow).count()
            logger.info(f"Analyzing {total_flows} flows for TOR indicators")
            
            # Process in batches
            offset = 0
            while offset < total_flows:
                flows = session.query(Flow).offset(offset).limit(batch_size).all()
                
                for flow in flows:
                    if self._analyze_flow(flow):
                        tor_flow_count += 1
                
                session.commit()
                offset += batch_size
            
            logger.info(f"Identified {tor_flow_count} TOR-related flows")
            return tor_flow_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error analyzing flows: {e}")
            raise
        finally:
            session.close()
    
    def _analyze_flow(self, flow: Flow) -> bool:
        """
        Analyze a single flow for TOR indicators.
        
        Args:
            flow: Flow object to analyze
        
        Returns:
            True if flow is TOR-related
        """
        is_tor = False
        
        # Check if destination is a known TOR node
        if flow.dst_ip in self.tor_node_ips:
            flow.relay_comm = True
            is_tor = True
        
        # Check for TOR ports
        if flow.dst_port in self.TOR_PORTS:
            flow.relay_comm = True
            is_tor = True
        
        # Check for directory port (9030)
        if flow.dst_port == 9030:
            flow.directory_fetch = True
            is_tor = True
        
        # Analyze payload if available
        if flow.payload_sample:
            try:
                payload = base64.b64decode(flow.payload_sample)
                
                # Check for TLS handshake
                if payload.startswith(self.TLS_CLIENT_HELLO):
                    # Check for TOR-specific patterns
                    for pattern in self.TOR_HANDSHAKE_PATTERNS:
                        if pattern in payload:
                            flow.possible_tor_handshake = True
                            is_tor = True
                            break
                
                # Check for obfsproxy patterns (simplified)
                if self._check_obfsproxy_patterns(payload):
                    flow.obfsproxy_candidate = True
                    is_tor = True
                    
            except Exception as e:
                logger.debug(f"Error decoding payload for flow {flow.id}: {e}")
        
        return is_tor
    
    def _check_obfsproxy_patterns(self, payload: bytes) -> bool:
        """
        Check for obfsproxy/pluggable transport patterns.
        
        Args:
            payload: Raw payload bytes
        
        Returns:
            True if obfsproxy patterns detected
        """
        # Simplified heuristic: high entropy, no clear protocol markers
        if len(payload) < 20:
            return False
        
        # Check for lack of common protocol markers
        common_markers = [
            b'HTTP/', b'GET ', b'POST ', b'SSH-', b'220 ', b'CONNECT'
        ]
        
        has_marker = any(marker in payload[:100] for marker in common_markers)
        
        # If no common markers and reasonable size, might be obfuscated
        if not has_marker and len(payload) > 100:
            # Simple entropy check (very basic)
            unique_bytes = len(set(payload[:100]))
            if unique_bytes > 50:  # High byte diversity
                return True
        
        return False
    
    def get_tor_nodes_by_flag(self, flag: str) -> List[TorNode]:
        """
        Get TOR nodes with specific flag.
        
        Args:
            flag: Flag to filter by (e.g., 'Guard', 'Exit')
        
        Returns:
            List of TorNode objects
        """
        session = self.db_manager.get_session()
        try:
            nodes = session.query(TorNode).all()
            filtered = [
                node for node in nodes 
                if node.flags and flag in node.flags
            ]
            return filtered
        finally:
            session.close()


def download_tor_consensus(output_path: Path) -> int:
    """
    Download current TOR consensus and save as JSON.
    
    Args:
        output_path: Path to save JSON file
    
    Returns:
        Number of nodes downloaded
    """
    logger.info("Downloading TOR consensus...")
    
    try:
        downloader = DescriptorDownloader()
        consensus = downloader.get_consensus()
        
        nodes = []
        for desc in consensus.run():
            node = {
                'ip_address': desc.address,
                'port': desc.or_port,
                'fingerprint': desc.fingerprint,
                'nickname': desc.nickname,
                'flags': desc.flags if hasattr(desc, 'flags') else [],
                'bandwidth': getattr(desc, 'bandwidth', 0)
            }
            nodes.append(node)
        
        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(nodes, f, indent=2)
        
        logger.info(f"Downloaded {len(nodes)} TOR nodes to {output_path}")
        return len(nodes)
        
    except Exception as e:
        logger.error(f"Error downloading TOR consensus: {e}")
        raise


if __name__ == '__main__':
    # Example usage
    import click
    
    @click.command()
    @click.option('--download', is_flag=True, help='Download TOR consensus')
    @click.option('--output', '-o', default='data/tor_node_list.json',
                  help='Output path for TOR node list')
    @click.option('--db', '-d', default='tor_analysis.db',
                  help='Database path')
    @click.option('--analyze', is_flag=True, help='Analyze flows in database')
    def main(download: bool, output: str, db: str, analyze: bool):
        """TOR extraction utility."""
        db_manager = DatabaseManager(f"sqlite:///{db}")
        
        if download:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            download_tor_consensus(output_path)
        
        if analyze:
            # Load TOR nodes
            tor_nodes_path = Path(output)
            if tor_nodes_path.exists():
                extractor = TorExtractor(db_manager)
                extractor.load_tor_nodes_from_file(tor_nodes_path)
                tor_count = extractor.analyze_flows()
                click.echo(f"✓ Identified {tor_count} TOR-related flows")
            else:
                click.echo(f"Error: TOR node list not found at {output}")
    
    main()
