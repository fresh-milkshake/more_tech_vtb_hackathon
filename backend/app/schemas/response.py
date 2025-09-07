from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class ResponseBase(BaseModel):
    transcript: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration: Optional[int] = None
    stt_confidence: Optional[float] = None
    language_detected: str = "en"


class ResponseCreate(ResponseBase):
    """Schema for creating a new response"""
    interview_id: uuid.UUID
    question_id: uuid.UUID
    audio_data: Optional[bytes] = None  # Raw audio data for processing


class ResponseUpdate(BaseModel):
    """Schema for updating response"""
    transcript: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration: Optional[int] = None
    stt_confidence: Optional[float] = None
    stt_segments: Optional[List[Dict[str, Any]]] = None
    language_detected: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    analysis_results: Optional[Dict[str, Any]] = None
    technical_accuracy: Optional[float] = None
    communication_clarity: Optional[float] = None
    relevance: Optional[float] = None
    completeness: Optional[float] = None
    keywords_matched: Optional[List[str]] = None
    sentiment: Optional[str] = None
    confidence_level: Optional[str] = None
    word_count: Optional[int] = None
    speaking_rate: Optional[float] = None
    pause_analysis: Optional[Dict[str, Any]] = None
    is_complete: Optional[bool] = None
    is_analyzed: Optional[bool] = None
    completed_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None


class ResponseResponse(ResponseBase):
    """Schema for response response"""
    id: uuid.UUID
    interview_id: uuid.UUID
    question_id: uuid.UUID
    score: float
    feedback: Optional[str]
    analysis_results: Dict[str, Any]
    technical_accuracy: float
    communication_clarity: float
    relevance: float
    completeness: float
    keywords_matched: List[str]
    sentiment: Optional[str]
    confidence_level: Optional[str]
    word_count: int
    speaking_rate: Optional[float]
    pause_analysis: Dict[str, Any]
    is_complete: bool
    is_analyzed: bool
    analysis_version: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    analyzed_at: Optional[datetime]
    extra_data: Dict[str, Any]
    flags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResponseAnalysis(BaseModel):
    """Schema for response analysis results"""
    score: float
    feedback: str
    strengths: List[str]
    areas_for_improvement: List[str]
    technical_accuracy: float
    communication_clarity: float
    relevance: float
    completeness: float
    keywords_matched: List[str]
    sentiment: str
    confidence_level: str
    detailed_analysis: Dict[str, Any]
    recommendations: List[str]


class AudioTranscription(BaseModel):
    """Schema for audio transcription results"""
    text: str
    confidence: float
    language: str
    segments: List[Dict[str, Any]]
    word_count: int
    duration: float
    speaking_rate: float


class ResponseStats(BaseModel):
    """Schema for response statistics"""
    total_responses: int
    average_score: float
    average_duration: float
    average_word_count: int
    sentiment_distribution: Dict[str, int]
    common_keywords: List[Dict[str, Any]]