from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ResumeBase(BaseModel):
    """Base schema for resume"""
    filename: str
    original_filename: str
    content_type: str
    candidate_id: Optional[uuid.UUID] = None
    upload_source: str = "hr_upload"


class ResumeCreate(ResumeBase):
    """Schema for creating a new resume"""
    pass


class ResumeUpdate(BaseModel):
    """Schema for updating resume information"""
    candidate_id: Optional[uuid.UUID] = None
    status: Optional[str] = None
    analysis_result: Optional[Dict[str, Any]] = None
    parsed_data: Optional[Dict[str, Any]] = None
    skills_extracted: Optional[List[str]] = None
    experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    match_scores: Optional[Dict[str, Any]] = None
    recommendations: Optional[str] = None
    error_message: Optional[str] = None


class ResumeResponse(ResumeBase):
    """Schema for resume response"""
    id: uuid.UUID
    file_size: Optional[str] = None
    file_path: Optional[str] = None
    status: str
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    raw_text: Optional[str] = None
    analysis_result: Optional[Dict[str, Any]] = None
    parsed_data: Optional[Dict[str, Any]] = None
    skills_extracted: Optional[List[str]] = None
    experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    match_scores: Optional[Dict[str, Any]] = None
    recommendations: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: str
    uploaded_by_user_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    """Schema for resume list response"""
    resumes: List[ResumeResponse]
    total: int
    page: int
    page_size: int


class ResumeProcessingStatus(BaseModel):
    """Schema for resume processing status"""
    id: uuid.UUID
    filename: str
    status: str
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None


class ResumeAnalysisResponse(BaseModel):
    """Schema for resume analysis response"""
    id: uuid.UUID
    filename: str
    status: str
    analysis_result: Optional[Dict[str, Any]] = None
    parsed_data: Optional[Dict[str, Any]] = None
    skills_extracted: Optional[List[str]] = None
    experience_summary: Optional[str] = None
    education_summary: Optional[str] = None
    ai_analysis: Optional[Dict[str, Any]] = None
    match_scores: Optional[Dict[str, Any]] = None
    recommendations: Optional[str] = None
    processing_completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResumeBulkUploadResponse(BaseModel):
    """Schema for bulk resume upload response"""
    successful_uploads: List[ResumeResponse]
    failed_uploads: List[Dict[str, str]]  # filename and error message
    total_processed: int
    total_successful: int
    total_failed: int


class ResumeSearchRequest(BaseModel):
    """Schema for resume search request"""
    query: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years_min: Optional[int] = None
    experience_years_max: Optional[int] = None
    position: Optional[str] = None
    status: Optional[str] = None
    candidate_id: Optional[uuid.UUID] = None
    uploaded_after: Optional[datetime] = None
    uploaded_before: Optional[datetime] = None


class ResumeMatchingRequest(BaseModel):
    """Schema for resume position matching request"""
    position_title: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []
    experience_level: Optional[str] = None  # junior, middle, senior
    min_experience_years: Optional[int] = None
    job_description: Optional[str] = None
    
    @field_validator('required_skills')
    def validate_required_skills(cls, v):
        if not v or len(v) == 0:
            raise ValueError('At least one required skill must be specified')
        return v


class ResumeMatchResult(BaseModel):
    """Schema for resume matching result"""
    resume_id: uuid.UUID
    filename: str
    candidate_id: Optional[uuid.UUID] = None
    match_score: float  # 0.0 to 1.0
    skills_match: Dict[str, Any]  # matched skills analysis
    experience_match: Dict[str, Any]  # experience analysis
    overall_fit: str  # excellent, good, fair, poor
    recommendations: str
    missing_skills: List[str]
    matching_skills: List[str]


class ResumeMatchingResponse(BaseModel):
    """Schema for resume matching response"""
    position_title: str
    total_resumes_analyzed: int
    matches: List[ResumeMatchResult]
    search_criteria: Dict[str, Any]
