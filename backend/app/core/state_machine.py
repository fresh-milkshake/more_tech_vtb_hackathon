from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import asyncio
import uuid

from app.core.states import InterviewState, InterviewEvent
from app.core.events import EventData, InterviewEventFactory
from app.core.transitions import StateTransitions


class InterviewStateMachine:
    """Main state machine for managing interview flow"""
    
    def __init__(self, interview_id: str, websocket_manager, services: Dict[str, Any]):
        self.interview_id = interview_id
        self.current_state = InterviewState.START
        self.context: Dict[str, Any] = {}
        self.timeline: List[Dict[str, Any]] = []
        self.websocket_manager = websocket_manager
        
        # External services
        self.services = services
        self.stt_service = services.get("stt")
        self.ai_service = services.get("ai")
        self.tts_service = services.get("tts")
        
        # State management
        self.transitions = StateTransitions()
        self.current_question = None
        self.response_timeout_task = None
        
    async def handle_event(self, event: InterviewEvent, data: Optional[Dict[str, Any]] = None) -> bool:
        """Process events and trigger state transitions"""
        try:
            # Validate transition
            if not self.transitions.is_valid_transition(self.current_state, event):
                await self._send_error(f"Invalid transition: {event} from {self.current_state}")
                return False
            
            # Create event data
            event_data = InterviewEventFactory.create_event(event, data or {})
            
            # Get next state
            previous_state = self.current_state
            next_state = self.transitions.get_next_state(self.current_state, event)
            
            # Execute transition
            await self._transition_to_state(next_state, event_data)
            
            # Log transition
            self._log_transition(previous_state, next_state, event, event_data)
            
            return True
            
        except Exception as e:
            await self._send_error(f"State machine error: {str(e)}")
            return False
    
    async def _transition_to_state(self, new_state: InterviewState, event_data: EventData):
        """Execute state transition and associated actions"""
        self.current_state = new_state
        
        # Execute state-specific actions and get data for frontend
        state_data = await self._execute_state_actions(event_data)
        
        # Send current state with data to frontend
        await self._send_state_to_frontend(state_data)
    
    async def _execute_state_actions(self, event_data: EventData) -> Dict[str, Any]:
        """Execute actions for current state and return data for frontend"""
        actions = {
            InterviewState.START: self._handle_start,
            InterviewState.INTRODUCTION: self._handle_introduction,
            InterviewState.LOADING_CONTEXT: self._handle_loading_context,
            InterviewState.PLAN_DECISION: self._handle_plan_decision,
            InterviewState.UPDATING_PLAN: self._handle_updating_plan,
            InterviewState.NEXT_STAGE: self._handle_next_stage,
            InterviewState.ASKING_QUESTION: self._handle_asking_question,
            InterviewState.WAITING_RESPONSE: self._handle_waiting_response,
            InterviewState.ANALYZING: self._handle_analyzing,
            InterviewState.SKIPPING_QUESTION: self._handle_skipping_question,
            InterviewState.UPDATING_TIMELINE: self._handle_updating_timeline,
            InterviewState.ENDING: self._handle_ending,
            InterviewState.FAREWELL: self._handle_farewell,
            InterviewState.COMPLETE: self._handle_complete,
        }
        
        action = actions.get(self.current_state)
        if action:
            return await action(event_data)
        return {}
    
    async def _send_state_to_frontend(self, state_data: Dict[str, Any]):
        """Send current state and data to frontend via WebSocket"""
        message = {
            "type": "state_update",
            "state": self.current_state.value,
            "timestamp": datetime.utcnow().isoformat(),
            "data": state_data
        }
        await self.websocket_manager.send_message(self.interview_id, message)
    
    async def _send_error(self, error_message: str):
        """Send error message to frontend"""
        message = {
            "type": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "message": error_message,
            "state": self.current_state.value
        }
        await self.websocket_manager.send_message(self.interview_id, message)
    
    def _log_transition(self, from_state: InterviewState, to_state: InterviewState, 
                       event: InterviewEvent, event_data: EventData):
        """Log state transition"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "from_state": from_state.value,
            "to_state": to_state.value,
            "event": event.value,
            "event_data": event_data.dict() if hasattr(event_data, 'dict') else str(event_data)
        }
        self.timeline.append(log_entry)
    
    # State action handlers
    async def _handle_start(self, event_data: EventData) -> Dict[str, Any]:
        """Handle interview start"""
        return {
            "message": "Interview starting...",
            "next_action": "introduction",
            "waiting_for": "automatic_transition"
        }
    
    async def _handle_introduction(self, event_data: EventData) -> Dict[str, Any]:
        """Generate AI introduction and send to frontend"""
        if not self.ai_service:
            intro_text = "Welcome to your interview. Let's begin!"
        else:
            intro_text = await self.ai_service.generate_introduction(self.context)
        
        audio_url = None
        if self.tts_service:
            audio_url = await self.tts_service.synthesize_speech(intro_text)
        
        return {
            "type": "ai_speech",
            "text": intro_text,
            "audio_url": audio_url,
            "waiting_for": "introduction_complete"
        }
    
    async def _handle_loading_context(self, event_data: EventData) -> Dict[str, Any]:
        """Load interview context"""
        # Simulate loading context
        await asyncio.sleep(1)  # Simulate processing time
        
        # Load basic context
        self.context.update({
            "interview_id": self.interview_id,
            "start_time": datetime.utcnow().isoformat(),
            "candidate_id": getattr(event_data, 'candidate_id', 'unknown'),
            "position": "Software Developer",
            "questions_asked": 0,
            "total_score": 0.0
        })
        
        return {
            "message": "Loading interview context...",
            "progress": 100,
            "context": self.context,
            "waiting_for": "context_loaded"
        }
    
    async def _handle_plan_decision(self, event_data: EventData) -> Dict[str, Any]:
        """Handle plan decision logic"""
        # Simple logic: continue if we haven't asked many questions yet
        questions_asked = self.context.get("questions_asked", 0)
        max_questions = 5
        
        if questions_asked >= max_questions:
            suggested_action = "end"
        else:
            suggested_action = "continue"
        
        return {
            "type": "plan_decision",
            "questions_asked": questions_asked,
            "max_questions": max_questions,
            "suggested_action": suggested_action,
            "waiting_for": "plan_decision_made"
        }
    
    async def _handle_updating_plan(self, event_data: EventData) -> Dict[str, Any]:
        """Handle plan update"""
        # Simulate plan update
        await asyncio.sleep(0.5)
        
        return {
            "message": "Updating interview plan...",
            "progress": 100,
            "waiting_for": "plan_updated"
        }
    
    async def _handle_next_stage(self, event_data: EventData) -> Dict[str, Any]:
        """Determine next stage action"""
        questions_asked = self.context.get("questions_asked", 0)
        
        if questions_asked >= 5:
            next_action = "end"
        else:
            next_action = "continue"
        
        return {
            "type": "next_stage_decision",
            "action": next_action,
            "waiting_for": "next_stage_determined"
        }
    
    async def _handle_asking_question(self, event_data: EventData) -> Dict[str, Any]:
        """Generate and present question to candidate"""
        if not self.ai_service:
            # Default question
            question_data = {
                "id": str(uuid.uuid4()),
                "text": "Can you tell me about your programming experience?",
                "category": "general",
                "expected_duration": 120
            }
        else:
            question_data = await self.ai_service.generate_question(
                self.context, self.timeline
            )
        
        self.current_question = question_data
        
        # Generate TTS for question
        audio_url = None
        if self.tts_service:
            audio_url = await self.tts_service.synthesize_speech(question_data["text"])
        
        return {
            "type": "question",
            "question_id": question_data["id"],
            "text": question_data["text"],
            "audio_url": audio_url,
            "category": question_data.get("category", "general"),
            "expected_duration": question_data.get("expected_duration", 120),
            "waiting_for": "question_presented"
        }
    
    async def _handle_waiting_response(self, event_data: EventData) -> Dict[str, Any]:
        """Wait for candidate response"""
        # Start timeout timer
        self._start_response_timeout()
        
        return {
            "type": "waiting_response",
            "timeout_seconds": 60,
            "recording_active": True,
            "waiting_for": "response_received"
        }
    
    async def _handle_analyzing(self, event_data: EventData) -> Dict[str, Any]:
        """Analyze candidate response"""
        # Cancel timeout if active
        self._cancel_response_timeout()
        
        response_text = getattr(event_data, 'response_text', '')
        if not response_text:
            return {"error": "No response to analyze"}
        
        # Analyze response
        if not self.ai_service:
            # Default analysis
            analysis = {
                "score": 7.5,
                "feedback": "Good response with relevant details.",
                "strengths": ["Clear communication"],
                "areas_for_improvement": ["Could provide more specific examples"]
            }
        else:
            question_text = self.current_question.get("text", "") if self.current_question else ""
            analysis = await self.ai_service.analyze_response(
                question_text, response_text, self.context
            )
        
        return {
            "type": "analysis_complete",
            "score": analysis["score"],
            "feedback": analysis["feedback"],
            "analysis": analysis,
            "waiting_for": "analysis_acknowledged"
        }
    
    async def _handle_skipping_question(self, event_data: EventData) -> Dict[str, Any]:
        """Handle skipped question"""
        self._cancel_response_timeout()
        
        return {
            "type": "question_skipped",
            "reason": "No response received within timeout",
            "score": 0.0,
            "waiting_for": "automatic_transition"
        }
    
    async def _handle_updating_timeline(self, event_data: EventData) -> Dict[str, Any]:
        """Update timeline with results"""
        # Update context
        self.context["questions_asked"] = self.context.get("questions_asked", 0) + 1
        
        # Add to timeline
        timeline_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "question": self.current_question,
            "response": getattr(event_data, 'response_text', ''),
            "score": getattr(event_data, 'score', 0.0)
        }
        self.timeline.append(timeline_entry)
        
        return {
            "type": "timeline_updated",
            "timeline_entry": timeline_entry,
            "total_questions": self.context["questions_asked"],
            "waiting_for": "timeline_updated"
        }
    
    async def _handle_ending(self, event_data: EventData) -> Dict[str, Any]:
        """Handle interview ending"""
        return {
            "message": "Ending interview...",
            "waiting_for": "automatic_transition"
        }
    
    async def _handle_farewell(self, event_data: EventData) -> Dict[str, Any]:
        """Generate farewell message"""
        if not self.ai_service:
            farewell_text = "Thank you for your time. The interview is now complete."
        else:
            farewell_text = await self.ai_service.generate_farewell(self.context)
        
        audio_url = None
        if self.tts_service:
            audio_url = await self.tts_service.synthesize_speech(farewell_text)
        
        return {
            "type": "ai_speech",
            "text": farewell_text,
            "audio_url": audio_url,
            "waiting_for": "farewell_complete"
        }
    
    async def _handle_complete(self, event_data: EventData) -> Dict[str, Any]:
        """Handle interview completion"""
        return {
            "type": "interview_complete",
            "message": "Interview completed successfully",
            "timeline": self.timeline,
            "total_score": self._calculate_total_score()
        }
    
    def _start_response_timeout(self):
        """Start response timeout timer"""
        async def timeout_handler():
            await asyncio.sleep(60)  # 60 second timeout
            await self.handle_event(InterviewEvent.QUESTION_TIMEOUT)
        
        self.response_timeout_task = asyncio.create_task(timeout_handler())
    
    def _cancel_response_timeout(self):
        """Cancel response timeout timer"""
        if self.response_timeout_task and not self.response_timeout_task.done():
            self.response_timeout_task.cancel()
    
    def _calculate_total_score(self) -> float:
        """Calculate total interview score"""
        scores = []
        for entry in self.timeline:
            if isinstance(entry, dict) and 'score' in entry:
                scores.append(entry['score'])
        
        return sum(scores) / len(scores) if scores else 0.0