from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class VacancyBase(BaseModel):
    """Base vacancy schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    company_name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    employment_type: Optional[str] = Field(None, max_length=50)
    experience_level: Optional[str] = Field(None, max_length=50)


class VacancyCreate(VacancyBase):
    """Schema for creating a vacancy"""
    pass


class VacancyUpdate(BaseModel):
    """Schema for updating a vacancy"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    company_name: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    salary_range: Optional[str] = Field(None, max_length=100)
    employment_type: Optional[str] = Field(None, max_length=50)
    experience_level: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None


class VacancyResponse(VacancyBase):
    """Schema for vacancy response"""
    id: int
    document_status: str
    is_active: bool
    is_published: bool
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    interview_links_count: Optional[int] = 0

    class Config:
        from_attributes = True


class VacancyWithLinks(VacancyResponse):
    """Schema for vacancy with interview links"""
    interview_links: List['InterviewLinkResponse'] = []


class VacancyListResponse(BaseModel):
    """Schema for vacancy list response"""
    vacancies: List[VacancyResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class DocumentUploadResponse(BaseModel):
    """Schema for document upload response"""
    message: str
    vacancy_id: int
    document_path: str
    status: str


class DocumentProcessingStatus(BaseModel):
    """Schema for document processing status"""
    vacancy_id: int
    status: str  # pending, processing, completed, failed
    message: Optional[str] = None
    processed_document_path: Optional[str] = None
