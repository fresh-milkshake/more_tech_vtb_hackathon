from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging
from datetime import datetime

from app.core.state_machine import InterviewStateMachine
from app.core.states import InterviewEvent
from app.schemas.websocket import (
    WebSocketMessage, StateUpdateMessage, ErrorMessage, 
    TriggerMessage, PlanDecisionMessage, NextStageMessage,
    ResponseReceivedMessage, AudioChunkMessage, AdminActionMessage
)
from app.services.realtime_pipeline import RealtimePipelineService

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and state machines"""
    
    def __init__(self):
        # Store active connections: interview_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # Store state machines: interview_id -> InterviewStateMachine
        self.state_machines: Dict[str, InterviewStateMachine] = {}
        
        # Services for state machines (will be injected)
        self.services: Dict[str, Any] = {}
        
        # Real-time pipeline service (will be initialized when services are set)
        self.pipeline_service: Optional[RealtimePipelineService] = None
        
        logger.info("WebSocket manager initialized")
    
    def set_services(self, services: Dict[str, Any]):
        """Set external services for state machines"""
        self.services = services
        
        # Initialize real-time pipeline service
        self.pipeline_service = RealtimePipelineService(services)
        
        logger.info(f"Services set: {list(services.keys())}")
        logger.info("Real-time pipeline service initialized")
    
    async def connect(self, websocket: WebSocket, interview_id: str):
        """Handle new WebSocket connection"""
        try:
            await websocket.accept()
            logger.info(f"WebSocket connection accepted for interview {interview_id}")
            
            # Add connection to active connections
            if interview_id not in self.active_connections:
                self.active_connections[interview_id] = []
                
                # Create new state machine for this interview
                self.state_machines[interview_id] = InterviewStateMachine(
                    interview_id, self, self.services
                )
                logger.info(f"Created state machine for interview {interview_id}")
            
            self.active_connections[interview_id].append(websocket)
            
            # Send connection status
            await self._send_connection_status(interview_id)
            
            # Start the interview state machine
            await self.state_machines[interview_id].handle_event(
                InterviewEvent.START_INTERVIEW,
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "candidate_id": f"demo_candidate_{interview_id}",
                    "interviewer_id": "demo_interviewer"
                }
            )
            
            # Start real-time pipeline
            if self.pipeline_service:
                pipeline_context = {
                    "interview_id": interview_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "position": "Software Developer",  # Can be extracted from context
                    "questions_asked": 0
                }
                await self.pipeline_service.start_pipeline(interview_id, pipeline_context)
                logger.info(f"Started real-time pipeline for interview {interview_id}")
            
            # Listen for messages
            await self._listen_for_messages(websocket, interview_id)
            
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for interview {interview_id}")
            await self.disconnect(websocket, interview_id)
        except Exception as e:
            logger.error(f"WebSocket connection error for interview {interview_id}: {str(e)}")
            await self.disconnect(websocket, interview_id)
    
    async def disconnect(self, websocket: WebSocket, interview_id: str):
        """Handle WebSocket disconnection"""
        try:
            if interview_id in self.active_connections:
                if websocket in self.active_connections[interview_id]:
                    self.active_connections[interview_id].remove(websocket)
                
                # Clean up if no more connections
                if not self.active_connections[interview_id]:
                    del self.active_connections[interview_id]
                    
                    # Clean up state machine
                    if interview_id in self.state_machines:
                        del self.state_machines[interview_id]
                    
                    # Stop real-time pipeline
                    if self.pipeline_service:
                        await self.pipeline_service.stop_pipeline(interview_id)
                        logger.info(f"Stopped real-time pipeline for interview {interview_id}")
                    
                    logger.info(f"Cleaned up resources for interview {interview_id}")
                else:
                    # Update connection status for remaining connections
                    await self._send_connection_status(interview_id)
                    
        except Exception as e:
            logger.error(f"Error during disconnect for interview {interview_id}: {str(e)}")
    
    async def send_message(self, interview_id: str, message: dict):
        """Send message to all connections for an interview"""
        if interview_id not in self.active_connections:
            logger.warning(f"No active connections for interview {interview_id}")
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections[interview_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Failed to send message to connection: {str(e)}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            await self.disconnect(connection, interview_id)
    
    async def _listen_for_messages(self, websocket: WebSocket, interview_id: str):
        """Listen for messages from WebSocket"""
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                await self._handle_message(interview_id, message)
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected during message listening for interview {interview_id}")
            raise
        except Exception as e:
            logger.error(f"Error listening for messages on interview {interview_id}: {str(e)}")
            await self.send_message(interview_id, {
                "type": "error",
                "message": f"Message processing error: {str(e)}"
            })
    
    async def _handle_message(self, interview_id: str, message: dict):
        """Handle incoming WebSocket messages from frontend"""
        try:
            message_type = message.get("type")
            logger.debug(f"Received message type '{message_type}' for interview {interview_id}")
            
            if interview_id not in self.state_machines:
                logger.warning(f"No state machine found for interview {interview_id}")
                return
            
            state_machine = self.state_machines[interview_id]
            
            # Handle different message types and trigger state transitions
            if message_type == "introduction_complete":
                await state_machine.handle_event(InterviewEvent.INTRODUCTION_COMPLETE)
                
            elif message_type == "context_loaded":
                await state_machine.handle_event(InterviewEvent.CONTEXT_LOADED)
                
            elif message_type == "question_presented":
                await state_machine.handle_event(InterviewEvent.QUESTION_GENERATED)
                
            elif message_type == "response_received":
                # Candidate provided response
                response_data = {
                    "response_text": message.get("text", ""),
                    "audio_data": message.get("audio_data"),
                    "question_id": message.get("question_id", ""),
                    "question_text": message.get("question_text", "")
                }
                await state_machine.handle_event(
                    InterviewEvent.SPEECH_RECOGNIZED, 
                    response_data
                )
                
            elif message_type == "response_timeout":
                # No response received within timeout
                await state_machine.handle_event(InterviewEvent.NO_SPEECH_DETECTED)
                
            elif message_type == "analysis_acknowledged":
                # Frontend acknowledged the analysis
                await state_machine.handle_event(InterviewEvent.RESPONSE_ANALYZED)
                
            elif message_type == "timeline_updated":
                # Timeline update complete
                await state_machine.handle_event(InterviewEvent.TIMELINE_UPDATED)
                
            elif message_type == "plan_decision_made":
                # Frontend made plan decision
                decision = message.get("decision", "continue")
                if decision == "update_plan":
                    await state_machine.handle_event(InterviewEvent.PLAN_CHANGE_REQUIRED)
                elif decision == "end":
                    await state_machine.handle_event(InterviewEvent.END_INTERVIEW)
                else:
                    await state_machine.handle_event(InterviewEvent.PLAN_CONTINUE)
                    
            elif message_type == "next_stage_determined":
                # Frontend determined next stage action
                action = message.get("action", "continue")
                if action == "end":
                    await state_machine.handle_event(InterviewEvent.END_INTERVIEW)
                else:
                    await state_machine.handle_event(InterviewEvent.CONTINUE_INTERVIEW)
                    
            elif message_type == "farewell_complete":
                await state_machine.handle_event(InterviewEvent.FAREWELL_COMPLETE)
                
            elif message_type == "audio_chunk":
                # Handle real-time audio streaming for STT
                audio_data = message.get("audio_data")
                if audio_data:
                    # Decode base64 audio data
                    import base64
                    try:
                        audio_bytes = base64.b64decode(audio_data)
                        await self._handle_audio_chunk(state_machine, audio_bytes)
                    except Exception as e:
                        logger.error(f"Error decoding audio data: {str(e)}")
                else:
                    logger.warning("Received audio_chunk message without audio_data")
                
            elif message_type == "admin_action":
                # Handle admin interventions
                await self._handle_admin_action(state_machine, message)
                
            elif message_type == "heartbeat":
                # Respond to heartbeat
                await self.send_message(interview_id, {
                    "type": "heartbeat",
                    "pong": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
            else:
                logger.warning(f"Unknown message type '{message_type}' for interview {interview_id}")
                await self.send_message(interview_id, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })
                
        except Exception as e:
            logger.error(f"Error handling message for interview {interview_id}: {str(e)}")
            await self.send_message(interview_id, {
                "type": "error",
                "message": f"Message handling error: {str(e)}"
            })
    
    async def _handle_audio_chunk(self, state_machine: InterviewStateMachine, audio_data: bytes):
        """Process audio chunk using real-time pipeline"""
        try:
            interview_id = state_machine.interview_id
            
            # Use real-time pipeline if available
            if self.pipeline_service:
                # Define callback for pipeline messages
                async def websocket_callback(message: dict):
                    await self.send_message(interview_id, message)
                
                # Process through pipeline
                result = await self.pipeline_service.process_audio_chunk(
                    interview_id, audio_data, websocket_callback
                )
                
                logger.debug(f"Pipeline processing result: {result.get('status', 'unknown')}")
                
            else:
                # Fallback to original implementation
                from app.core.states import InterviewState
                
                if state_machine.current_state == InterviewState.WAITING_RESPONSE:
                    # Only process audio during response waiting
                    if state_machine.stt_service:
                        transcription = await state_machine.stt_service.transcribe_audio(audio_data)
                        
                        # Send partial transcription to frontend if text detected
                        if transcription.get("text"):
                            await self.send_message(interview_id, {
                                "type": "partial_transcription",
                                "text": transcription["text"],
                                "confidence": transcription.get("confidence", 0.0),
                                "is_final": False,
                                "timestamp": datetime.utcnow().isoformat()
                            })
                        
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
    
    async def _handle_admin_action(self, state_machine: InterviewStateMachine, message: dict):
        """Handle admin actions"""
        try:
            action = message.get("action")
            reason = message.get("reason", "Admin intervention")
            
            if action == "skip_question":
                await state_machine.handle_event(InterviewEvent.NO_SPEECH_DETECTED, {
                    "reason": reason,
                    "admin_action": True
                })
            elif action == "end_interview":
                await state_machine.handle_event(InterviewEvent.END_INTERVIEW, {
                    "reason": reason,
                    "admin_action": True
                })
            elif action == "pause":
                # Implement pause logic
                await self.send_message(state_machine.interview_id, {
                    "type": "interview_paused",
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                })
            elif action == "resume":
                # Implement resume logic
                await self.send_message(state_machine.interview_id, {
                    "type": "interview_resumed", 
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                logger.warning(f"Unknown admin action: {action}")
                
        except Exception as e:
            logger.error(f"Error handling admin action: {str(e)}")
    
    async def _send_connection_status(self, interview_id: str):
        """Send connection status update"""
        if interview_id in self.active_connections:
            connection_count = len(self.active_connections[interview_id])
            await self.send_message(interview_id, {
                "type": "connection_status",
                "status": "connected",
                "client_count": connection_count,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def get_active_interviews(self) -> List[str]:
        """Get list of active interview IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self, interview_id: str) -> int:
        """Get number of connections for an interview"""
        return len(self.active_connections.get(interview_id, []))
    
    def is_interview_active(self, interview_id: str) -> bool:
        """Check if an interview has active connections"""
        return interview_id in self.active_connections and len(self.active_connections[interview_id]) > 0


# Global WebSocket manager instance
websocket_manager = WebSocketManager()