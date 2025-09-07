from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class InterviewLink(Base):
    """Interview link model for candidate access"""
    __tablename__ = "interview_links"

    id = Column(Integer, primary_key=True, index=True)
    unique_token = Column(String(255), unique=True, index=True, nullable=False)
    candidate_name = Column(String(255), nullable=True)
    candidate_email = Column(String(255), nullable=True)
    candidate_phone = Column(String(50), nullable=True)
    
    # Link metadata
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Interview session data
    interview_session_id = Column(String(255), nullable=True)  # For WebSocket session
    interview_started_at = Column(DateTime(timezone=True), nullable=True)
    interview_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional candidate info
    candidate_resume_path = Column(String(500), nullable=True)
    candidate_notes = Column(Text, nullable=True)
    
    # Foreign keys
    vacancy_id = Column(Integer, ForeignKey("vacancies.id"), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    vacancy = relationship("Vacancy", back_populates="interview_links")
    created_by = relationship("User", back_populates="created_interview_links")

    def __repr__(self):
        return f"<InterviewLink(id={self.id}, token='{self.unique_token[:10]}...', vacancy_id={self.vacancy_id})>"
