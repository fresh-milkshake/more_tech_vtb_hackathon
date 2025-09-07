from sqlalchemy import Column, String, DateTime, JSON, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    
    # Professional Information
    resume_text = Column(Text)
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    
    # Skills and Experience
    skills = Column(JSON)  # List of skills
    experience_years = Column(String(20))
    current_position = Column(String(200))
    current_company = Column(String(200))
    
    # Application Information
    applied_position = Column(String(200))
    application_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="applied")  # applied, screening, interviewing, hired, rejected
    
    # Additional Data
    extra_data = Column(JSON)  # Additional candidate information
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    interviews = relationship("Interview", back_populates="candidate")
    resumes = relationship("Resume", back_populates="candidate")