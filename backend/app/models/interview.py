from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    interviewer_id = Column(String(255))  # For now, just store as string
    
    # Interview metadata
    position = Column(String(255), nullable=False)
    interview_type = Column(String(50), default="technical")  # technical, behavioral, cultural
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, cancelled
    
    # State machine data
    current_state = Column(String(50), default="START")
    timeline = Column(JSON, default=list)  # Timeline of events and transitions
    context = Column(JSON, default=dict)  # Interview context data
    
    # Timestamps
    scheduled_at = Column(DateTime, nullable=False)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Interview configuration
    interview_plan = Column(JSON)  # Planned questions and stages
    max_questions = Column(Integer, default=5)
    estimated_duration = Column(Integer, default=3600)  # seconds
    
    # Results
    total_score = Column(Float, default=0.0)
    overall_feedback = Column(Text)
    recommendation = Column(String(50))  # hire, reject, maybe
    
    # Additional data
    extra_data = Column(JSON, default=dict)
    notes = Column(Text)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    questions = relationship("Question", back_populates="interview", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="interview", cascade="all, delete-orphan")