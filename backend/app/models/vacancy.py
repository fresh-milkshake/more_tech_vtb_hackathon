from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Vacancy(Base):
    """
    Vacancy model for job positions and employment opportunities.
    
    Represents job vacancies with detailed information including requirements,
    responsibilities, company details, and document processing status.
    """
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    responsibilities = Column(Text, nullable=True)
    company_name = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    salary_range = Column(String(100), nullable=True)
    employment_type = Column(String(50), nullable=True)  # full-time, part-time, contract, etc.
    experience_level = Column(String(50), nullable=True)  # junior, middle, senior, etc.
    
    original_document_path = Column(String(500), nullable=True)
    processed_document_path = Column(String(500), nullable=True)
    document_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    created_by = relationship("User", back_populates="vacancies")
    interview_links = relationship("InterviewLink", back_populates="vacancy", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vacancy(id={self.id}, title='{self.title}', company='{self.company_name}')>"
