from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class TimelineEntry(Base):
    __tablename__ = "timeline_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=False)
    
    # Timeline entry data
    entry_type = Column(String(50), nullable=False)  # state_transition, question_asked, response_received, etc.
    state_from = Column(String(50))  # Previous state
    state_to = Column(String(50))    # New state
    event_type = Column(String(50))  # Event that triggered the transition
    
    # Associated IDs
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="SET NULL"))
    response_id = Column(UUID(as_uuid=True), ForeignKey("responses.id", ondelete="SET NULL"))
    
    # Entry content
    title = Column(String(200))
    description = Column(Text)
    data = Column(JSON)  # Additional data specific to this entry type
    
    # Scoring information
    score_awarded = Column(Float)  # Score for this specific entry
    running_total_score = Column(Float)  # Running total after this entry
    
    # Timing
    duration_seconds = Column(Integer)  # How long this step took
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Status and metadata
    is_milestone = Column(Boolean, default=False)  # Mark important milestones
    flags = Column(JSON, default=list)  # Any flags or notes
    extra_data = Column(JSON, default=dict)
    
    # Relationships
    interview = relationship("Interview")
    question = relationship("Question")
    response = relationship("Response")