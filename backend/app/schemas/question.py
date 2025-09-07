from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class QuestionBase(BaseModel):
    text: str
    category: str = "general"
    difficulty: int = 3
    expected_duration: int = 120
    question_type: str = "open"
    expected_keywords: Optional[List[str]] = []
    scoring_rubric: Optional[Dict[str, Any]] = {}
    max_score: float = 10.0


class QuestionCreate(QuestionBase):
    """Schema for creating a new question"""
    interview_id: uuid.UUID
    order_in_interview: Optional[int] = None
    is_adaptive: bool = False
    generated_by_ai: bool = False
    generation_prompt: Optional[str] = None
    generation_context: Optional[Dict[str, Any]] = {}

    @field_validator('difficulty')
    def validate_difficulty(cls, v):
        if not 1 <= v <= 5:
            raise ValueError('difficulty must be between 1 and 5')
        return v

    @field_validator('category')
    def validate_category(cls, v):
        valid_categories = ['technical', 'behavioral', 'cultural', 'general', 'coding']
        if v not in valid_categories:
            raise ValueError(f'category must be one of {valid_categories}')
        return v


class QuestionUpdate(BaseModel):
    """Schema for updating question"""
    text: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[int] = None
    expected_duration: Optional[int] = None
    question_type: Optional[str] = None
    expected_keywords: Optional[List[str]] = None
    scoring_rubric: Optional[Dict[str, Any]] = None
    max_score: Optional[float] = None
    tts_audio_url: Optional[str] = None
    audio_duration: Optional[int] = None
    asked_at: Optional[datetime] = None


class QuestionResponse(QuestionBase):
    """Schema for question response"""
    id: uuid.UUID
    interview_id: uuid.UUID
    order_in_interview: Optional[int]
    is_adaptive: bool
    question_type: str
    generated_by_ai: bool
    generation_prompt: Optional[str]
    generation_context: Dict[str, Any]
    tts_audio_url: Optional[str]
    audio_duration: Optional[int]
    asked_at: Optional[datetime]
    extra_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionWithResponse(QuestionResponse):
    """Schema for question with its response"""
    response: Optional['ResponseResponse'] = None


class GeneratedQuestion(BaseModel):
    """Schema for AI-generated question"""
    text: str
    category: str
    difficulty: int
    expected_duration: int
    expected_keywords: List[str]
    scoring_rubric: Dict[str, Any]
    generation_reasoning: str
    confidence_score: float


# Import here to avoid circular imports
from app.schemas.response import ResponseResponse
QuestionWithResponse.model_rebuild()