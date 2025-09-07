from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class InterviewLinkBase(BaseModel):
    """Base interview link schema"""
    candidate_name: Optional[str] = Field(None, max_length=255)
    candidate_email: Optional[EmailStr] = None
    candidate_phone: Optional[str] = Field(None, max_length=50)
    candidate_notes: Optional[str] = None


class InterviewLinkCreate(InterviewLinkBase):
    """Schema for creating an interview link"""
    expires_hours: int = Field(default=6, ge=1, le=168)  # 1 hour to 1 week


class InterviewLinkUpdate(BaseModel):
    """Schema for updating an interview link"""
    candidate_name: Optional[str] = Field(None, max_length=255)
    candidate_email: Optional[EmailStr] = None
    candidate_phone: Optional[str] = Field(None, max_length=50)
    candidate_notes: Optional[str] = None
    is_active: Optional[bool] = None


class InterviewLinkResponse(InterviewLinkBase):
    """Schema for interview link response"""
    id: int
    unique_token: str
    expires_at: datetime
    is_used: bool
    is_active: bool
    interview_session_id: Optional[str] = None
    interview_started_at: Optional[datetime] = None
    interview_completed_at: Optional[datetime] = None
    candidate_resume_path: Optional[str] = None
    vacancy_id: int
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewLinkPublic(BaseModel):
    """Schema for public interview link (for candidates)"""
    unique_token: str
    vacancy_title: str
    company_name: Optional[str] = None
    expires_at: datetime
    is_used: bool


class InterviewLinkListResponse(BaseModel):
    """Schema for interview link list response"""
    links: list[InterviewLinkResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class CandidateAccessRequest(BaseModel):
    """Schema for candidate access request"""
    candidate_name: str = Field(..., min_length=1, max_length=255)
    candidate_email: EmailStr
    candidate_phone: Optional[str] = Field(None, max_length=50)


class CandidateSessionResponse(BaseModel):
    """Schema for candidate session response"""
    session_id: str
    vacancy_title: str
    company_name: Optional[str] = None
    interview_link_id: int
    expires_at: datetime
    is_expired: bool


class InterviewLinkStats(BaseModel):
    """Schema for interview link statistics"""
    total_links: int
    active_links: int
    used_links: int
    expired_links: int
    links_by_status: dict[str, int]
