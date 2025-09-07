from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Response(Base):
    __tablename__ = "responses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    
    # Response content
    transcript = Column(Text)  # Full transcript of the response
    audio_url = Column(String(500))  # URL to stored audio file
    audio_duration = Column(Integer)  # Duration in seconds
    
    # Speech-to-Text data
    stt_confidence = Column(Float)  # STT confidence score (0-1)
    stt_segments = Column(JSON)  # Detailed STT segments with timestamps
    language_detected = Column(String(10), default="en")
    
    # Analysis results
    score = Column(Float, default=0.0)  # Final score (0-10)
    feedback = Column(Text)  # AI-generated feedback
    analysis_results = Column(JSON)  # Detailed AI analysis results
    
    # Detailed scoring
    technical_accuracy = Column(Float, default=0.0)
    communication_clarity = Column(Float, default=0.0)
    relevance = Column(Float, default=0.0)
    completeness = Column(Float, default=0.0)
    
    # Content analysis
    keywords_matched = Column(JSON)  # Keywords found in response
    sentiment = Column(String(20))  # positive, neutral, negative
    confidence_level = Column(String(20))  # high, medium, low
    
    # Response metadata
    word_count = Column(Integer, default=0)
    speaking_rate = Column(Float)  # Words per minute
    pause_analysis = Column(JSON)  # Analysis of pauses and hesitations
    
    # Status
    is_complete = Column(Boolean, default=False)
    is_analyzed = Column(Boolean, default=False)
    analysis_version = Column(String(20), default="1.0")  # Version of analysis algorithm
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    analyzed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data
    extra_data = Column(JSON, default=dict)
    flags = Column(JSON, default=list)  # Any flags or alerts for manual review
    
    # Relationships
    interview = relationship("Interview", back_populates="responses")
    question = relationship("Question", back_populates="response")