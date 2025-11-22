"""
SQLAlchemy database models for TOR analysis.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, 
    Boolean, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship, sessionmaker, Session, DeclarativeBase
from pathlib import Path

class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Flow(Base):
    """Network flow record."""
    __tablename__ = 'flows'
    
    id = Column(Integer, primary_key=True)
    src_ip = Column(String(45), nullable=False, index=True)
    src_port = Column(Integer, nullable=False)
    dst_ip = Column(String(45), nullable=False, index=True)
    dst_port = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=False)
    ts_start = Column(DateTime, nullable=False, index=True)
    ts_end = Column(DateTime)
    pkt_count = Column(Integer, default=0)
    byte_count = Column(Integer, default=0)
    payload_sample = Column(Text)  # Hex/base64 encoded
    
    # TOR-specific flags
    possible_tor_handshake = Column(Boolean, default=False)
    relay_comm = Column(Boolean, default=False)
    directory_fetch = Column(Boolean, default=False)
    obfsproxy_candidate = Column(Boolean, default=False)
    
    # Analysis results
    confidence_score = Column(Float, default=0.0)
    confidence_category = Column(String(20))  # Low, Medium, High, Critical
    
    # Relationships
    alerts = relationship("Alert", back_populates="flow", cascade="all, delete-orphan")
    correlations = relationship("Correlation", foreign_keys="Correlation.flow_id", 
                               back_populates="flow", cascade="all, delete-orphan")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Flow {self.src_ip}:{self.src_port} -> {self.dst_ip}:{self.dst_port}>"


class TorNode(Base):
    """TOR relay node information."""
    __tablename__ = 'tor_nodes'
    
    id = Column(Integer, primary_key=True)
    ip_address = Column(String(45), nullable=False, unique=True, index=True)
    port = Column(Integer, nullable=False)
    fingerprint = Column(String(40), unique=True)
    nickname = Column(String(100))
    flags = Column(JSON)  # Guard, Exit, Fast, Stable, etc.
    country_code = Column(String(2))
    asn = Column(String(20))
    bandwidth = Column(Integer)
    last_seen = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TorNode {self.ip_address}:{self.port} ({self.nickname})>"


class Alert(Base):
    """Security alert for suspicious flows."""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    flow_id = Column(Integer, ForeignKey('flows.id'), nullable=False)
    severity = Column(String(20), nullable=False)  # Low, Medium, High, Critical
    alert_type = Column(String(50), nullable=False)
    description = Column(Text)
    evidence = Column(JSON)  # Structured evidence data
    
    flow = relationship("Flow", back_populates="alerts")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Alert {self.severity} - {self.alert_type}>"


class Correlation(Base):
    """Flow correlation records."""
    __tablename__ = 'correlations'
    
    id = Column(Integer, primary_key=True)
    flow_id = Column(Integer, ForeignKey('flows.id'), nullable=False)
    correlated_flow_id = Column(Integer, ForeignKey('flows.id'), nullable=False)
    correlation_weight = Column(Float, nullable=False)
    correlation_type = Column(String(50))  # entry_exit, timing, payload_similarity
    evidence = Column(JSON)
    
    flow = relationship("Flow", foreign_keys=[flow_id], back_populates="correlations")
    correlated_flow = relationship("Flow", foreign_keys=[correlated_flow_id])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Correlation {self.flow_id} <-> {self.correlated_flow_id} (weight: {self.correlation_weight})>"


class Report(Base):
    """Forensic report metadata."""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    report_type = Column(String(50))  # forensic, summary, detailed
    file_path = Column(String(500))
    summary = Column(Text)
    
    # Report statistics
    total_flows = Column(Integer, default=0)
    suspect_flows = Column(Integer, default=0)
    critical_alerts = Column(Integer, default=0)
    
    report_metadata = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Report {self.title}>"


class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, db_url: str = "sqlite:///tor_analysis.db"):
        """
        Initialize database manager.
        
        Args:
            db_url: SQLAlchemy database URL
        """
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()
    
    def reset_database(self):
        """Reset database (drop and recreate all tables)."""
        self.drop_tables()
        self.create_tables()


def init_database(db_path: Optional[Path] = None) -> DatabaseManager:
    """
    Initialize database with default or custom path.
    
    Args:
        db_path: Optional custom database path
    
    Returns:
        DatabaseManager instance
    """
    if db_path:
        db_url = f"sqlite:///{db_path}"
    else:
        db_url = "sqlite:///tor_analysis.db"
    
    db_manager = DatabaseManager(db_url)
    db_manager.create_tables()
    
    return db_manager
