"""
PCAP ingestion and flow normalization using Scapy.
"""

import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Generator
from collections import defaultdict
import click

from scapy.all import rdpcap, PcapReader, IP, IPv6, TCP, UDP, Raw
from scapy.packet import Packet
from tqdm import tqdm

from src.db.models import Flow, DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FlowKey:
    """Unique identifier for a network flow."""
    
    def __init__(self, src_ip: str, src_port: int, dst_ip: str, dst_port: int, proto: str):
        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.proto = proto
    
    def __hash__(self):
        return hash((self.src_ip, self.src_port, self.dst_ip, self.dst_port, self.proto))
    
    def __eq__(self, other):
        return (self.src_ip == other.src_ip and 
                self.src_port == other.src_port and
                self.dst_ip == other.dst_ip and 
                self.dst_port == other.dst_port and
                self.proto == other.proto)


class FlowRecord:
    """Aggregated flow record."""
    
    def __init__(self, key: FlowKey, timestamp: float):
        self.key = key
        self.ts_start = datetime.fromtimestamp(timestamp)
        self.ts_end = datetime.fromtimestamp(timestamp)
        self.pkt_count = 0
        self.byte_count = 0
        self.payload_sample: Optional[bytes] = None
    
    def update(self, timestamp: float, payload: Optional[bytes], pkt_size: int):
        """Update flow with new packet information."""
        self.ts_end = datetime.fromtimestamp(timestamp)
        self.pkt_count += 1
        self.byte_count += pkt_size
        
        # Capture first payload sample (up to 512 bytes)
        if payload and not self.payload_sample:
            self.payload_sample = payload[:512]
    
    def to_flow_model(self) -> Flow:
        """Convert to SQLAlchemy Flow model."""
        payload_encoded = None
        if self.payload_sample:
            payload_encoded = base64.b64encode(self.payload_sample).decode('utf-8')
        
        return Flow(
            src_ip=self.key.src_ip,
            src_port=self.key.src_port,
            dst_ip=self.key.dst_ip,
            dst_port=self.key.dst_port,
            protocol=self.key.proto,
            ts_start=self.ts_start,
            ts_end=self.ts_end,
            pkt_count=self.pkt_count,
            byte_count=self.byte_count,
            payload_sample=payload_encoded
        )


class PcapIngestor:
    """PCAP file ingestion and flow extraction."""
    
    def __init__(self, db_manager: DatabaseManager, batch_size: int = 1000):
        """
        Initialize PCAP ingestor.
        
        Args:
            db_manager: Database manager instance
            batch_size: Number of flows to batch before database insert
        """
        self.db_manager = db_manager
        self.batch_size = batch_size
        self.flows: Dict[FlowKey, FlowRecord] = {}
    
    def process_packet(self, packet: Packet) -> Optional[FlowKey]:
        """
        Process a single packet and update flow records.
        
        Args:
            packet: Scapy packet
        
        Returns:
            FlowKey if packet was processed, None otherwise
        """
        # Extract IP layer
        if IP in packet:
            ip_layer = packet[IP]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
        elif IPv6 in packet:
            ip_layer = packet[IPv6]
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
        else:
            return None
        
        # Extract transport layer
        if TCP in packet:
            transport = packet[TCP]
            proto = "TCP"
            src_port = transport.sport
            dst_port = transport.dport
        elif UDP in packet:
            transport = packet[UDP]
            proto = "UDP"
            src_port = transport.sport
            dst_port = transport.dport
        else:
            return None
        
        # Create flow key
        flow_key = FlowKey(src_ip, src_port, dst_ip, dst_port, proto)
        
        # Extract payload
        payload = None
        if Raw in packet:
            payload = bytes(packet[Raw].load)
        
        # Get packet timestamp and size
        timestamp = float(packet.time)
        pkt_size = len(packet)
        
        # Update or create flow record
        if flow_key not in self.flows:
            self.flows[flow_key] = FlowRecord(flow_key, timestamp)
        
        self.flows[flow_key].update(timestamp, payload, pkt_size)
        
        return flow_key
    
    def ingest_pcap(self, pcap_path: Path, streaming: bool = True) -> int:
        """
        Ingest PCAP file and extract flows.
        
        Args:
            pcap_path: Path to PCAP file
            streaming: Use streaming mode for large files
        
        Returns:
            Number of flows extracted
        """
        logger.info(f"Starting PCAP ingestion", file=str(pcap_path))
        
        self.flows.clear()
        packet_count = 0
        
        try:
            if streaming:
                # Streaming mode for large files
                with PcapReader(str(pcap_path)) as pcap_reader:
                    for packet in tqdm(pcap_reader, desc="Processing packets", unit="pkt"):
                        self.process_packet(packet)
                        packet_count += 1
                        
                        # Periodic batch insert
                        if len(self.flows) >= self.batch_size:
                            self._flush_flows()
            else:
                # Load entire file (for small PCAPs)
                packets = rdpcap(str(pcap_path))
                for packet in tqdm(packets, desc="Processing packets", unit="pkt"):
                    self.process_packet(packet)
                    packet_count += 1
            
            # Final flush
            self._flush_flows()
            
            flow_count = len(self.flows)
            logger.info(f"PCAP ingestion complete", 
                       packets=packet_count, flows=flow_count)
            
            return flow_count
            
        except Exception as e:
            logger.error(f"Error ingesting PCAP: {e}", file=str(pcap_path))
            raise
    
    def _flush_flows(self):
        """Flush accumulated flows to database."""
        if not self.flows:
            return
        
        session = self.db_manager.get_session()
        try:
            flow_models = [flow.to_flow_model() for flow in self.flows.values()]
            session.bulk_save_objects(flow_models)
            session.commit()
            logger.debug(f"Flushed {len(flow_models)} flows to database")
        except Exception as e:
            session.rollback()
            logger.error(f"Error flushing flows: {e}")
            raise
        finally:
            session.close()


@click.command()
@click.option('--file', '-f', 'pcap_file', required=True, type=click.Path(exists=True),
              help='Path to PCAP file')
@click.option('--db', '-d', 'db_path', default='tor_analysis.db',
              help='Database path (default: tor_analysis.db)')
@click.option('--streaming/--no-streaming', default=True,
              help='Use streaming mode for large files')
@click.option('--batch-size', '-b', default=1000, type=int,
              help='Batch size for database inserts')
def main(pcap_file: str, db_path: str, streaming: bool, batch_size: int):
    """
    Ingest PCAP file and extract network flows.
    
    Example:
        python -m src.collector.pcap_ingest --file data/sample.pcap
    """
    from pathlib import Path
    
    # Initialize database
    db_manager = DatabaseManager(f"sqlite:///{db_path}")
    db_manager.create_tables()
    
    # Ingest PCAP
    ingestor = PcapIngestor(db_manager, batch_size=batch_size)
    flow_count = ingestor.ingest_pcap(Path(pcap_file), streaming=streaming)
    
    click.echo(f"✓ Ingested {flow_count} flows from {pcap_file}")


if __name__ == '__main__':
    main()
