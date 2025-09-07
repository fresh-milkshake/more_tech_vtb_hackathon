from sqlalchemy import Column, String, DateTime, JSON, Text, Boolean, LargeBinary, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # File Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(String(50))  # File size in bytes as string
    file_path = Column(String(500))  # Path where file is stored
    
    # Processing Status
    status = Column(String(50), default="uploaded")  # uploaded, processing, processed, failed
    processing_started_at = Column(DateTime)
    processing_completed_at = Column(DateTime)
    
    # Extracted Content
    raw_text = Column(Text)  # Raw extracted text from resume
    
    # Analysis Results
    analysis_result = Column(JSON)  # Complete analysis result
    parsed_data = Column(JSON)  # Structured parsed data
    skills_extracted = Column(JSON)  # List of extracted skills
    experience_summary = Column(Text)  # Summary of experience
    education_summary = Column(Text)  # Summary of education
    
    # AI Analysis
    ai_analysis = Column(JSON)  # AI-generated analysis and insights
    match_scores = Column(JSON)  # Scores for different positions/criteria
    recommendations = Column(Text)  # AI recommendations
    
    # Error Handling
    error_message = Column(Text)  # Error message if processing failed
    retry_count = Column(String(10), default="0")
    
    # Metadata
    upload_source = Column(String(100), default="hr_upload")  # hr_upload, candidate_upload, api, etc.
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Candidate Association (optional)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="resumes")
    uploaded_by = relationship("User")

    def __repr__(self):
        return f"<Resume(id={self.id}, filename={self.filename}, status={self.status})>"
