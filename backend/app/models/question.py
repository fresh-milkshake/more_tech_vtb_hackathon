from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Question(Base):
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interview_id = Column(UUID(as_uuid=True), ForeignKey("interviews.id"), nullable=False)
    
    # Question content
    text = Column(Text, nullable=False)
    category = Column(String(100))  # technical, behavioral, cultural, general
    difficulty = Column(Integer, default=3)  # 1-5 scale
    expected_duration = Column(Integer, default=120)  # seconds
    
    # Question metadata
    order_in_interview = Column(Integer)
    is_adaptive = Column(Boolean, default=False)  # Generated based on previous responses
    question_type = Column(String(50), default="open")  # open, multiple_choice, coding
    
    # AI Generation metadata
    generated_by_ai = Column(Boolean, default=False)
    generation_prompt = Column(Text)  # The prompt used to generate this question
    generation_context = Column(JSON)  # Context used for generation
    
    # Scoring criteria
    expected_keywords = Column(JSON)  # Keywords to look for in responses
    scoring_rubric = Column(JSON)  # Detailed scoring criteria
    max_score = Column(Float, default=10.0)
    
    # Audio data
    tts_audio_url = Column(String(500))  # URL to TTS audio file
    audio_duration = Column(Integer)  # Duration in seconds
    
    # Timestamps
    asked_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional data
    extra_data = Column(JSON, default=dict)
    
    # Relationships
    interview = relationship("Interview", back_populates="questions")
    response = relationship("Response", back_populates="question", uselist=False)