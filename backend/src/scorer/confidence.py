"""
Confidence scoring for suspicious flows.
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

from sqlalchemy.orm import Session
from sqlalchemy import or_

from src.db.models import Flow, Correlation, TorNode, DatabaseManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ScoreComponents:
    """Individual components of confidence score."""
    tor_node_match: float = 0.0
    timing_correlation: float = 0.0
    payload_similarity: float = 0.0
    unusual_patterns: float = 0.0
    total: float = 0.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'tor_node_match': self.tor_node_match,
            'timing_correlation': self.timing_correlation,
            'payload_similarity': self.payload_similarity,
            'unusual_patterns': self.unusual_patterns,
            'total': self.total
        }


class ConfidenceScorer:
    """Calculate confidence scores for suspicious flows."""
    
    # Score weights (total = 100)
    WEIGHTS = {
        'tor_node_match': 40,
        'timing_correlation': 30,
        'payload_similarity': 20,
        'unusual_patterns': 10
    }
    
    # Confidence categories
    CATEGORIES = {
        'Low': (0, 30),
        'Medium': (30, 60),
        'High': (60, 85),
        'Critical': (85, 100)
    }
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize confidence scorer.
        
        Args:
            db_manager: Database manager instance
        """
        self.db_manager = db_manager
    
    def score_all_flows(self) -> int:
        """
        Score all flows in database.
        
        Returns:
            Number of flows scored
        """
        session = self.db_manager.get_session()
        scored_count = 0
        
        try:
            # Get all flows
            flows = session.query(Flow).all()
            logger.info(f"Scoring {len(flows)} flows")
            
            for flow in flows:
                score_components = self._calculate_score(flow, session)
                
                # Update flow with score
                flow.confidence_score = score_components.total
                flow.confidence_category = self._get_category(score_components.total)
                
                scored_count += 1
            
            session.commit()
            logger.info(f"Scored {scored_count} flows")
            return scored_count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error scoring flows: {e}")
            raise
        finally:
            session.close()
    
    def score_flow(self, flow_id: int) -> Tuple[float, ScoreComponents]:
        """
        Score a specific flow.
        
        Args:
            flow_id: Flow ID
        
        Returns:
            Tuple of (total_score, score_components)
        """
        session = self.db_manager.get_session()
        try:
            flow = session.query(Flow).filter_by(id=flow_id).first()
            if not flow:
                raise ValueError(f"Flow {flow_id} not found")
            
            score_components = self._calculate_score(flow, session)
            return score_components.total, score_components
            
        finally:
            session.close()
    
    def _calculate_score(self, flow: Flow, session: Session) -> ScoreComponents:
        """
        Calculate confidence score components for a flow.
        
        Args:
            flow: Flow object
            session: Database session
        
        Returns:
            ScoreComponents object
        """
        components = ScoreComponents()
        
        # 1. TOR node match score (0-40 points)
        components.tor_node_match = self._score_tor_node_match(flow, session)
        
        # 2. Timing correlation score (0-30 points)
        components.timing_correlation = self._score_timing_correlation(flow, session)
        
        # 3. Payload similarity score (0-20 points)
        components.payload_similarity = self._score_payload_patterns(flow)
        
        # 4. Unusual patterns score (0-10 points)
        components.unusual_patterns = self._score_unusual_patterns(flow)
        
        # Calculate total
        components.total = (
            components.tor_node_match +
            components.timing_correlation +
            components.payload_similarity +
            components.unusual_patterns
        )
        
        # Clamp to 0-100
        components.total = max(0.0, min(100.0, components.total))
        
        return components
    
    def _score_tor_node_match(self, flow: Flow, session: Session) -> float:
        """
        Score based on TOR node matching.
        
        Args:
            flow: Flow object
            session: Database session
        
        Returns:
            Score (0-40)
        """
        score = 0.0
        max_score = self.WEIGHTS['tor_node_match']
        
        # Check if destination is known TOR node
        tor_node = session.query(TorNode).filter_by(
            ip_address=flow.dst_ip
        ).first()
        
        if tor_node:
            # Base score for TOR node match
            score += max_score * 0.5
            
            # Bonus for specific node types
            if tor_node.flags:
                if 'Guard' in tor_node.flags:
                    score += max_score * 0.2
                if 'Exit' in tor_node.flags:
                    score += max_score * 0.2
                if 'Fast' in tor_node.flags:
                    score += max_score * 0.1
        
        # Check for TOR-specific flags
        if flow.relay_comm:
            score += max_score * 0.3
        if flow.directory_fetch:
            score += max_score * 0.2
        if flow.possible_tor_handshake:
            score += max_score * 0.3
        if flow.obfsproxy_candidate:
            score += max_score * 0.4
        
        return min(score, max_score)
    
    def _score_timing_correlation(self, flow: Flow, session: Session) -> float:
        """
        Score based on timing correlations with other flows.
        
        Args:
            flow: Flow object
            session: Database session
        
        Returns:
            Score (0-30)
        """
        score = 0.0
        max_score = self.WEIGHTS['timing_correlation']
        
        # Get correlations for this flow
        correlations = session.query(Correlation).filter(
            or_(
                Correlation.flow_id == flow.id,
                Correlation.correlated_flow_id == flow.id
            )
        ).all()
        
        if not correlations:
            return 0.0
        
        # Score based on number and strength of correlations
        total_weight = sum(c.correlation_weight for c in correlations)
        correlation_count = len(correlations)
        
        # More correlations = higher score
        if correlation_count >= 5:
            count_score = max_score * 0.5
        elif correlation_count >= 3:
            count_score = max_score * 0.3
        elif correlation_count >= 1:
            count_score = max_score * 0.2
        else:
            count_score = 0.0
        
        # Higher average weight = higher score
        avg_weight = total_weight / correlation_count if correlation_count > 0 else 0
        weight_score = avg_weight * max_score * 0.5
        
        score = count_score + weight_score
        
        return min(score, max_score)
    
    def _score_payload_patterns(self, flow: Flow) -> float:
        """
        Score based on payload patterns.
        
        Args:
            flow: Flow object
        
        Returns:
            Score (0-20)
        """
        score = 0.0
        max_score = self.WEIGHTS['payload_similarity']
        
        if not flow.payload_sample:
            return 0.0
        
        # TLS handshake detected
        if flow.possible_tor_handshake:
            score += max_score * 0.6
        
        # Obfsproxy candidate (high entropy)
        if flow.obfsproxy_candidate:
            score += max_score * 0.8
        
        # Large payload (potential data transfer)
        if flow.byte_count > 10000:
            score += max_score * 0.2
        
        return min(score, max_score)
    
    def _score_unusual_patterns(self, flow: Flow) -> float:
        """
        Score based on unusual patterns.
        
        Args:
            flow: Flow object
        
        Returns:
            Score (0-10)
        """
        score = 0.0
        max_score = self.WEIGHTS['unusual_patterns']
        
        # Unusual port combinations
        if flow.dst_port in {9001, 9030, 9050, 9051, 9150}:
            score += max_score * 0.5
        
        # High packet count (sustained connection)
        if flow.pkt_count > 100:
            score += max_score * 0.3
        
        # Long duration connection
        if flow.ts_end and flow.ts_start:
            duration = (flow.ts_end - flow.ts_start).total_seconds()
            if duration > 60:  # More than 1 minute
                score += max_score * 0.2
        
        return min(score, max_score)
    
    def _get_category(self, score: float) -> str:
        """
        Get confidence category from score.
        
        Args:
            score: Confidence score (0-100)
        
        Returns:
            Category name
        """
        for category, (min_score, max_score) in self.CATEGORIES.items():
            if min_score <= score < max_score:
                return category
        
        return 'Critical'  # >= 85
    
    def get_high_confidence_flows(self, min_score: float = 60.0) -> List[Flow]:
        """
        Get flows with high confidence scores.
        
        Args:
            min_score: Minimum confidence score
        
        Returns:
            List of Flow objects
        """
        session = self.db_manager.get_session()
        try:
            flows = session.query(Flow).filter(
                Flow.confidence_score >= min_score
            ).order_by(Flow.confidence_score.desc()).all()
            
            return flows
        finally:
            session.close()


if __name__ == '__main__':
    import click
    
    @click.command()
    @click.option('--db', '-d', default='tor_analysis.db',
                  help='Database path')
    @click.option('--flow-id', '-f', type=int,
                  help='Score specific flow ID')
    def main(db: str, flow_id: int):
        """Score flows for TOR confidence."""
        db_manager = DatabaseManager(f"sqlite:///{db}")
        scorer = ConfidenceScorer(db_manager)
        
        if flow_id:
            score, components = scorer.score_flow(flow_id)
            click.echo(f"Flow {flow_id} score: {score:.2f}")
            click.echo(f"Components: {components.to_dict()}")
        else:
            scored_count = scorer.score_all_flows()
            click.echo(f"✓ Scored {scored_count} flows")
            
            # Show high confidence flows
            high_conf = scorer.get_high_confidence_flows(min_score=60.0)
            click.echo(f"✓ Found {len(high_conf)} high-confidence flows")
    
    main()
