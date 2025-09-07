from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from app.core.states import InterviewState


class InterviewBase(BaseModel):
    position: str
    interview_type: str = "technical"
    scheduled_at: datetime
    max_questions: int = 5
    estimated_duration: int = 3600
    interview_plan: Optional[Dict[str, Any]] = {}


class InterviewCreate(InterviewBase):
    """Schema for creating a new interview"""
    candidate_id: uuid.UUID
    interviewer_id: Optional[str] = None

    @field_validator('interview_type')
    def validate_interview_type(cls, v):
        valid_types = ['technical', 'behavioral', 'cultural', 'general']
        if v not in valid_types:
            raise ValueError(f'interview_type must be one of {valid_types}')
        return v


class InterviewUpdate(BaseModel):
    """Schema for updating interview"""
    position: Optional[str] = None
    interview_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[str] = None
    current_state: Optional[str] = None
    max_questions: Optional[int] = None
    estimated_duration: Optional[int] = None
    interview_plan: Optional[Dict[str, Any]] = None
    total_score: Optional[float] = None
    overall_feedback: Optional[str] = None
    recommendation: Optional[str] = None
    notes: Optional[str] = None


class InterviewResponse(InterviewBase):
    """Schema for interview response"""
    id: uuid.UUID
    candidate_id: uuid.UUID
    interviewer_id: Optional[str]
    status: str
    current_state: str
    timeline: List[Dict[str, Any]]
    context: Dict[str, Any]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    total_score: float
    overall_feedback: Optional[str]
    recommendation: Optional[str]
    extra_data: Dict[str, Any]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewListResponse(BaseModel):
    """Schema for interview list response"""
    interviews: List[InterviewResponse]
    total: int
    page: int
    page_size: int


class InterviewSummary(BaseModel):
    """Schema for interview summary"""
    id: uuid.UUID
    candidate_name: str
    position: str
    status: str
    current_state: str
    scheduled_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    total_score: float
    questions_asked: int
    max_questions: int
    recommendation: Optional[str]


class InterviewStats(BaseModel):
    """Schema for interview statistics"""
    total_interviews: int
    completed_interviews: int
    in_progress_interviews: int
    scheduled_interviews: int
    average_score: float
    average_duration_minutes: float