"""
Unit tests for confidence scoring module.
"""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime, timedelta

from src.db.models import DatabaseManager, Flow, TorNode, Correlation
from src.scorer.confidence import ConfidenceScorer, ScoreComponents


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
def sample_flows(db_manager):
    """Create sample flows for testing."""
    session = db_manager.get_session()
    
    try:
        # Create TOR node
        tor_node = TorNode(
            ip_address="185.220.101.1",
            port=9001,
            fingerprint="ABC123",
            nickname="TestRelay",
            flags=["Guard", "Fast", "Stable"]
        )
        session.add(tor_node)
        
        # Create flows
        flow1 = Flow(
            src_ip="192.168.1.100",
            src_port=50000,
            dst_ip="185.220.101.1",
            dst_port=9001,
            protocol="TCP",
            ts_start=datetime.now(),
            ts_end=datetime.now() + timedelta(seconds=10),
            pkt_count=100,
            byte_count=10000,
            possible_tor_handshake=True,
            relay_comm=True
        )
        
        flow2 = Flow(
            src_ip="192.168.1.101",
            src_port=50001,
            dst_ip="8.8.8.8",
            dst_port=443,
            protocol="TCP",
            ts_start=datetime.now() + timedelta(seconds=2),
            ts_end=datetime.now() + timedelta(seconds=12),
            pkt_count=50,
            byte_count=5000
        )
        
        session.add(flow1)
        session.add(flow2)
        session.commit()
        
        return [flow1.id, flow2.id]
        
    finally:
        session.close()


def test_score_components_to_dict():
    """Test ScoreComponents to_dict conversion."""
    components = ScoreComponents(
        tor_node_match=30.0,
        timing_correlation=20.0,
        payload_similarity=15.0,
        unusual_patterns=5.0,
        total=70.0
    )
    
    result = components.to_dict()
    
    assert result['tor_node_match'] == 30.0
    assert result['timing_correlation'] == 20.0
    assert result['total'] == 70.0


def test_confidence_scorer_initialization(db_manager):
    """Test ConfidenceScorer initialization."""
    scorer = ConfidenceScorer(db_manager)
    
    assert scorer.db_manager is not None
    assert scorer.WEIGHTS['tor_node_match'] == 40
    assert scorer.WEIGHTS['timing_correlation'] == 30


def test_score_flow(db_manager, sample_flows):
    """Test scoring a single flow."""
    scorer = ConfidenceScorer(db_manager)
    
    flow_id = sample_flows[0]
    score, components = scorer.score_flow(flow_id)
    
    assert 0 <= score <= 100
    assert components.tor_node_match > 0  # Should match TOR node
    assert components.total == score


def test_score_all_flows(db_manager, sample_flows):
    """Test scoring all flows."""
    scorer = ConfidenceScorer(db_manager)
    
    scored_count = scorer.score_all_flows()
    
    assert scored_count == len(sample_flows)
    
    # Verify scores in database
    session = db_manager.get_session()
    try:
        flows = session.query(Flow).all()
        for flow in flows:
            assert flow.confidence_score >= 0
            assert flow.confidence_category in ['Low', 'Medium', 'High', 'Critical']
    finally:
        session.close()


def test_get_category():
    """Test confidence category assignment."""
    scorer = ConfidenceScorer(None)
    
    assert scorer._get_category(10.0) == 'Low'
    assert scorer._get_category(45.0) == 'Medium'
    assert scorer._get_category(70.0) == 'High'
    assert scorer._get_category(90.0) == 'Critical'


def test_get_high_confidence_flows(db_manager, sample_flows):
    """Test retrieving high confidence flows."""
    scorer = ConfidenceScorer(db_manager)
    scorer.score_all_flows()
    
    high_conf_flows = scorer.get_high_confidence_flows(min_score=0.0)
    
    assert len(high_conf_flows) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
