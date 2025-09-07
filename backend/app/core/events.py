from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.states import InterviewEvent


class EventData(BaseModel):
    """Base class for event data"""
    timestamp: datetime = datetime.utcnow()
    source: str = "system"
    metadata: Optional[Dict[str, Any]] = None


class StartInterviewEvent(EventData):
    """Event data for starting interview"""
    candidate_id: str
    interviewer_id: str
    interview_plan: Optional[Dict[str, Any]] = None


class SpeechRecognizedEvent(EventData):
    """Event data for recognized speech"""
    response_text: str
    audio_data: Optional[bytes] = None
    question_id: Optional[str] = None
    question_text: Optional[str] = None
    confidence: float = 0.0


class ResponseAnalyzedEvent(EventData):
    """Event data for analyzed response"""
    question_id: str
    response_id: str
    score: float
    feedback: str
    analysis_results: Dict[str, Any]


class PlanDecisionEvent(EventData):
    """Event data for plan decision"""
    decision: str  # "continue", "update_plan", "end"
    reason: Optional[str] = None


class TimelineUpdateEvent(EventData):
    """Event data for timeline update"""
    question_id: str
    response_data: Dict[str, Any]
    score: float
    timeline_entry: Dict[str, Any]


class InterviewEventFactory:
    """Factory for creating interview events"""
    
    @staticmethod
    def create_event(event_type: InterviewEvent, data: Dict[str, Any]) -> EventData:
        """Create appropriate event data based on event type"""
        if event_type == InterviewEvent.START_INTERVIEW:
            return StartInterviewEvent(**data)
        elif event_type == InterviewEvent.SPEECH_RECOGNIZED:
            return SpeechRecognizedEvent(**data)
        elif event_type == InterviewEvent.RESPONSE_ANALYZED:
            return ResponseAnalyzedEvent(**data)
        elif event_type == InterviewEvent.TIMELINE_UPDATED:
            return TimelineUpdateEvent(**data)
        else:
            return EventData(**data)