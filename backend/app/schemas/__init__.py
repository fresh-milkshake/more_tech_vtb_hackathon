# Import all schemas
from .candidate import CandidateCreate, CandidateResponse, CandidateUpdate
from .interview import InterviewCreate, InterviewResponse, InterviewUpdate
from .question import QuestionCreate, QuestionResponse, QuestionUpdate
from .response import ResponseCreate, ResponseResponse, ResponseUpdate
from .websocket import WebSocketMessage
from .auth import (
    UserBase, UserCreate, UserLogin, UserResponse, Token, TokenData,
    PasswordChange, UserUpdate
)
from .vacancy import (
    VacancyBase, VacancyCreate, VacancyUpdate, VacancyResponse,
    VacancyWithLinks, VacancyListResponse, DocumentUploadResponse,
    DocumentProcessingStatus
)
from .interview_link import (
    InterviewLinkBase, InterviewLinkCreate, InterviewLinkUpdate,
    InterviewLinkResponse, InterviewLinkPublic, InterviewLinkListResponse,
    CandidateAccessRequest, CandidateSessionResponse, InterviewLinkStats
)
from .resume import (
    ResumeCreate, ResumeUpdate, ResumeResponse, ResumeListResponse,
    ResumeProcessingStatus, ResumeAnalysisResponse, ResumeBulkUploadResponse,
    ResumeSearchRequest, ResumeMatchingRequest, ResumeMatchingResponse, ResumeMatchResult
)

__all__ = [
    "CandidateCreate",
    "CandidateResponse", 
    "CandidateUpdate",
    "InterviewCreate",
    "InterviewResponse",
    "InterviewUpdate",
    "QuestionCreate",
    "QuestionResponse",
    "QuestionUpdate",
    "ResponseCreate",
    "ResponseResponse",
    "ResponseUpdate",
    "WebSocketMessage",
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "PasswordChange",
    "UserUpdate",
    "VacancyBase",
    "VacancyCreate",
    "VacancyUpdate",
    "VacancyResponse",
    "VacancyWithLinks",
    "VacancyListResponse",
    "DocumentUploadResponse",
    "DocumentProcessingStatus",
    "InterviewLinkBase",
    "InterviewLinkCreate",
    "InterviewLinkUpdate",
    "InterviewLinkResponse",
    "InterviewLinkPublic",
    "InterviewLinkListResponse",
    "CandidateAccessRequest",
    "CandidateSessionResponse",
    "InterviewLinkStats",
    "ResumeCreate",
    "ResumeUpdate",
    "ResumeResponse",
    "ResumeListResponse",
    "ResumeProcessingStatus",
    "ResumeAnalysisResponse",
    "ResumeBulkUploadResponse",
    "ResumeSearchRequest",
    "ResumeMatchingRequest",
    "ResumeMatchingResponse",
    "ResumeMatchResult"
]
