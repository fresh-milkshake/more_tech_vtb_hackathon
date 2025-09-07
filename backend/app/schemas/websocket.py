from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
import uuid


class WebSocketMessage(BaseModel):
    """Base WebSocket message schema"""
    type: str
    timestamp: datetime = datetime.utcnow()
    data: Optional[Dict[str, Any]] = {}


class StateUpdateMessage(WebSocketMessage):
    """Message for state updates from backend to frontend"""
    type: str = "state_update"
    state: str
    data: Dict[str, Any]


class ErrorMessage(WebSocketMessage):
    """Error message schema"""
    type: str = "error"
    message: str
    error_code: Optional[str] = None
    state: Optional[str] = None


class AudioChunkMessage(WebSocketMessage):
    """Audio chunk message from frontend"""
    type: str = "audio_chunk"
    audio_data: bytes
    sample_rate: int = 16000
    channels: int = 1
    chunk_id: Optional[str] = None


class TranscriptionMessage(WebSocketMessage):
    """Transcription message to frontend"""
    type: str = "transcription"
    text: str
    confidence: float
    is_final: bool = True
    language: str = "en"


class QuestionMessage(WebSocketMessage):
    """Question message to frontend"""
    type: str = "question"
    question_id: str
    text: str
    category: str
    expected_duration: int
    audio_url: Optional[str] = None
    difficulty: int = 3


class ResponseReceivedMessage(WebSocketMessage):
    """Response received message from frontend"""
    type: str = "response_received"
    text: Optional[str] = None
    audio_data: Optional[bytes] = None
    question_id: str
    question_text: Optional[str] = None


class AnalysisCompleteMessage(WebSocketMessage):
    """Analysis complete message to frontend"""
    type: str = "analysis_complete"
    score: float
    feedback: str
    analysis: Dict[str, Any]
    question_id: str


class TriggerMessage(WebSocketMessage):
    """Frontend trigger messages"""
    type: str
    
    @field_validator('type')
    def validate_trigger_type(cls, v):
        valid_triggers = [
            'introduction_complete',
            'context_loaded',
            'question_presented',
            'response_received',
            'response_timeout',
            'analysis_acknowledged',
            'timeline_updated',
            'plan_decision_made',
            'next_stage_determined',
            'farewell_complete'
        ]
        if v not in valid_triggers:
            raise ValueError(f'type must be one of {valid_triggers}')
        return v


class PlanDecisionMessage(TriggerMessage):
    """Plan decision message from frontend"""
    type: str = "plan_decision_made"
    decision: str  # "continue", "update_plan", "end"
    reason: Optional[str] = None

    @field_validator('decision')
    def validate_decision(cls, v):
        valid_decisions = ['continue', 'update_plan', 'end']
        if v not in valid_decisions:
            raise ValueError(f'decision must be one of {valid_decisions}')
        return v


class NextStageMessage(TriggerMessage):
    """Next stage message from frontend"""
    type: str = "next_stage_determined"
    action: str  # "continue", "end"

    @field_validator('action')
    def validate_action(cls, v):
        valid_actions = ['continue', 'end']
        if v not in valid_actions:
            raise ValueError(f'action must be one of {valid_actions}')
        return v


class AdminActionMessage(WebSocketMessage):
    """Admin action message from frontend"""
    type: str = "admin_action"
    action: str  # "skip_question", "end_interview", "pause", "resume"
    reason: Optional[str] = None
    admin_id: Optional[str] = None


class ConnectionStatusMessage(WebSocketMessage):
    """Connection status message"""
    type: str = "connection_status"
    status: str  # "connected", "disconnected", "reconnecting"
    client_count: int = 1


class HeartbeatMessage(WebSocketMessage):
    """Heartbeat message for connection keep-alive"""
    type: str = "heartbeat"
    ping: str = "ping"


# Union type for all possible WebSocket messages
WebSocketMessageTypes = Union[
    StateUpdateMessage,
    ErrorMessage,
    AudioChunkMessage,
    TranscriptionMessage,
    QuestionMessage,
    ResponseReceivedMessage,
    AnalysisCompleteMessage,
    TriggerMessage,
    PlanDecisionMessage,
    NextStageMessage,
    AdminActionMessage,
    ConnectionStatusMessage,
    HeartbeatMessage
]