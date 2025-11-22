"""
Unit tests for PCAP ingestion module.
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile

from scapy.all import IP, TCP, Raw, wrpcap

from src.db.models import DatabaseManager, Flow
from src.collector.pcap_ingest import PcapIngestor, FlowKey, FlowRecord


@pytest.fixture
def db_manager():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = Path(tmp.name)
    
    db_manager = DatabaseManager(f"sqlite:///{db_path}")
    db_manager.create_tables()
    
    yield db_manager
    
    # Cleanup
    db_path.unlink()


@pytest.fixture
def sample_pcap():
    """Create sample PCAP file for testing."""
    from scapy.all import Ether, IP, TCP, UDP
    
    packets = []
    
    # Create some TCP packets
    for i in range(10):
        pkt = Ether() / IP(src="192.168.1.100", dst="185.220.101.1") / \
              TCP(sport=50000+i, dport=9001) / Raw(load=b"TOR handshake data")
        packets.append(pkt)
    
    # Create some UDP packets
    for i in range(5):
        pkt = Ether() / IP(src="192.168.1.101", dst="8.8.8.8") / \
              UDP(sport=60000+i, dport=53) / Raw(load=b"DNS query")
        packets.append(pkt)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.pcap', delete=False) as tmp:
        pcap_path = Path(tmp.name)
    
    wrpcap(str(pcap_path), packets)
    
    yield pcap_path
    
    # Cleanup
    pcap_path.unlink()


def test_flow_key_equality():
    """Test FlowKey equality and hashing."""
    key1 = FlowKey("192.168.1.1", 5000, "10.0.0.1", 80, "TCP")
    key2 = FlowKey("192.168.1.1", 5000, "10.0.0.1", 80, "TCP")
    key3 = FlowKey("192.168.1.2", 5000, "10.0.0.1", 80, "TCP")
    
    assert key1 == key2
    assert key1 != key3
    assert hash(key1) == hash(key2)


def test_flow_record_update():
    """Test FlowRecord update functionality."""
    key = FlowKey("192.168.1.1", 5000, "10.0.0.1", 80, "TCP")
    record = FlowRecord(key, 1000.0)
    
    assert record.pkt_count == 0
    assert record.byte_count == 0
    
    record.update(1001.0, b"test payload", 100)
    
    assert record.pkt_count == 1
    assert record.byte_count == 100
    assert record.payload_sample == b"test payload"


def test_pcap_ingestion(db_manager, sample_pcap):
    """Test PCAP file ingestion."""
    ingestor = PcapIngestor(db_manager, batch_size=10)
    flow_count = ingestor.ingest_pcap(sample_pcap, streaming=False)
    
    assert flow_count > 0
    
    # Verify flows in database
    session = db_manager.get_session()
    try:
        flows = session.query(Flow).all()
        assert len(flows) > 0
        
        # Check flow properties
        for flow in flows:
            assert flow.src_ip is not None
            assert flow.dst_ip is not None
            assert flow.protocol in ['TCP', 'UDP']
            assert flow.pkt_count > 0
            assert flow.byte_count > 0
    finally:
        session.close()


def test_flow_to_model_conversion():
    """Test conversion of FlowRecord to Flow model."""
    key = FlowKey("192.168.1.1", 5000, "10.0.0.1", 80, "TCP")
    record = FlowRecord(key, 1000.0)
    record.update(1001.0, b"test", 100)
    
    flow_model = record.to_flow_model()
    
    assert flow_model.src_ip == "192.168.1.1"
    assert flow_model.src_port == 5000
    assert flow_model.dst_ip == "10.0.0.1"
    assert flow_model.dst_port == 80
    assert flow_model.protocol == "TCP"
    assert flow_model.pkt_count == 1
    assert flow_model.byte_count == 100
    assert flow_model.payload_sample is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
