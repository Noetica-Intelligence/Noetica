from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, JSON, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

# Association table for User <-> Saved Discoveries
user_saved_discoveries = Table(
    'user_saved_discoveries',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('discovery_id', String, ForeignKey('discoveries.id'))
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Preferences
    interests = Column(JSON, default=list)        # list of strings
    expertise_level = Column(String, default="Intermediate")
    reading_time = Column(Integer, default=15)    # in minutes
    notification_settings = Column(JSON, default=dict)
    
    # Relationships
    saved_discoveries = relationship("Discovery", secondary=user_saved_discoveries)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Discovery(Base):
    """Primary entity for discoveries."""
    __tablename__ = "discoveries"

    id = Column(String, primary_key=True, index=True) # e.g. clustering UUID
    title = Column(String, index=True, nullable=False)
    abstract = Column(String)
    primary_domain = Column(String, index=True)
    
    first_seen_date = Column(DateTime(timezone=True), server_default=func.now())
    last_seen_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Significance metrics
    significance_score = Column(Float, default=0.0)
    trend_score = Column(Float, default=0.0)
    momentum_score = Column(Float, default=0.0)
    forecast_probability = Column(Float, default=0.0) # V3 Noetica Forecasting Engine
    
    # Discovery Lifecycle Engine V2
    status = Column(String, default="Emerging") # Emerging, Growing, Breakthrough, Established, Foundational, Declining, Archived
    
    source_urls = Column(JSON, default=list)
    authors = Column(JSON, default=list)
    
class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"
    
    node_id = Column(String, primary_key=True, index=True)
    node_name = Column(String, unique=True, index=True)
    node_type = Column(String) # Technology, Field, Concept, Dataset, etc.
    field = Column(String)
    subfield = Column(String)

class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"
    
    edge_id = Column(String, primary_key=True, index=True)
    source_node = Column(String, ForeignKey('knowledge_nodes.node_id'))
    target_node = Column(String, ForeignKey('knowledge_nodes.node_id'))
    relationship_type = Column(String) # influences, enabled_by, depends_on, etc.
    weight = Column(Float, default=1.0)
    
    # Self-referential relationships
    source = relationship("KnowledgeNode", foreign_keys=[source_node])
    target = relationship("KnowledgeNode", foreign_keys=[target_node])
