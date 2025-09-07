from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_text: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = []
    experience_years: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    applied_position: Optional[str] = None
    notes: Optional[str] = None


class CandidateCreate(CandidateBase):
    """Schema for creating a new candidate"""
    pass

    @field_validator('skills')
    def validate_skills(cls, v):
        if v is None:
            return []
        return v


class CandidateUpdate(BaseModel):
    """Schema for updating candidate information"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    resume_text: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[str] = None
    current_position: Optional[str] = None
    current_company: Optional[str] = None
    applied_position: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class CandidateResponse(CandidateBase):
    """Schema for candidate response"""
    id: uuid.UUID
    status: str
    application_date: datetime
    extra_data: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateListResponse(BaseModel):
    """Schema for candidate list response"""
    candidates: List[CandidateResponse]
    total: int
    page: int
    page_size: int