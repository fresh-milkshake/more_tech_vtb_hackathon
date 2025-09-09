import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime

from app.config import settings
from app.services.interview_analysis_mock import InterviewAnalysisMock

logger = logging.getLogger(__name__)


class RealtimePipelineService:
    """
    Real-time audio processing pipeline service
    Coordinates: Audio Input -> STT -> Analysis -> TTS -> Audio Output

    IMPORTANT: requires vacancy_path to initialize InterviewAnalysisMock (uses only functions from first file).
    """
    
    def __init__(self, services: Dict[str, Any], vacancy_path: str):
        self.services = services
        self.active_pipelines: Dict[str, Dict] = {}
        self.audio_buffers: Dict[str, bytearray] = {}
        self.processing_locks: Dict[str, asyncio.Lock] = {}
 
        self.mock_analyzer = InterviewAnalysisMock(vacancy_path)
        
        self.min_chunk_size = 2048  # Minimum audio chunk size for processing
        self.max_buffer_size = 32768  # Maximum buffer size before forced processing
        self.silence_threshold = 0.01  # Silence detection threshold
        self.processing_timeout = 30.0  # Max processing time per chunk
        
        logger.info("Real-time pipeline service initialized")
    
    async def start_pipeline(self, interview_id: str, context: Dict[str, Any]) -> bool:
        """Start a new real-time processing pipeline for an interview"""
        try:
            if interview_id in self.active_pipelines:
                logger.warning(f"Pipeline already active for interview {interview_id}")
                return True
            
            self.active_pipelines[interview_id] = {
                "status": "active",
                "context": context,
                "started_at": datetime.utcnow(),
                "stats": {
                    "chunks_processed": 0,
                    "transcriptions": 0,
                    "audio_generated": 0,
                    "errors": 0
                },
                "current_question": context.get("current_question", ""),
                "is_processing": False
            }
            
            self.audio_buffers[interview_id] = bytearray()
            self.processing_locks[interview_id] = asyncio.Lock()
            
            logger.info(f"Started real-time pipeline for interview {interview_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting pipeline for interview {interview_id}: {str(e)}")
            return False
    
    async def stop_pipeline(self, interview_id: str) -> bool:
        """Stop the real-time processing pipeline"""
        try:
            if interview_id not in self.active_pipelines:
                logger.warning(f"No active pipeline for interview {interview_id}")
                return True
            
            self.active_pipelines[interview_id]["status"] = "stopped"
            self.active_pipelines[interview_id]["stopped_at"] = datetime.utcnow()
            
            if interview_id in self.audio_buffers:
                del self.audio_buffers[interview_id]
            
            if interview_id in self.processing_locks:
                del self.processing_locks[interview_id]
            
            logger.info(f"Stopped real-time pipeline for interview {interview_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping pipeline for interview {interview_id}: {str(e)}")
            return False
    
    async def process_audio_chunk(
        self, 
        interview_id: str, 
        audio_chunk: bytes,
        websocket_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Process incoming audio chunk through the real-time pipeline
        Returns processing result and may trigger callbacks
        """
        if interview_id not in self.active_pipelines:
            return {"error": "No active pipeline for this interview"}
        
        pipeline = self.active_pipelines[interview_id]
        
        if pipeline["status"] != "active":
            return {"error": "Pipeline is not active"}
        
        if audio_chunk is None:
            logger.warning(f"Received None audio chunk for interview {interview_id}")
            pipeline["stats"]["errors"] += 1
            return {"error": "Audio chunk is None"}
        
        try:
            async with self.processing_locks[interview_id]:
                return await self._process_chunk_internal(
                    interview_id, audio_chunk, websocket_callback
                )
                
        except Exception as e:
            logger.error(f"Error processing audio chunk for {interview_id}: {str(e)}")
            pipeline["stats"]["errors"] += 1
            return {"error": str(e)}
    
    async def _process_chunk_internal(
        self, 
        interview_id: str, 
        audio_chunk: bytes,
        websocket_callback: Optional[Callable]
    ) -> Dict[str, Any]:
        """Internal audio processing logic"""
        pipeline = self.active_pipelines[interview_id]
        buffer = self.audio_buffers[interview_id]
        
        # Validate audio chunk
        if audio_chunk is None:
            logger.warning(f"Received None audio chunk for interview {interview_id}")
            return {"error": "Audio chunk is None"}
        
        if not isinstance(audio_chunk, (bytes, bytearray)):
            logger.warning(f"Invalid audio chunk type: {type(audio_chunk)} for interview {interview_id}")
            return {"error": f"Invalid audio chunk type: {type(audio_chunk)}"}
        
        if len(audio_chunk) == 0:
            logger.warning(f"Received empty audio chunk for interview {interview_id}")
            return {"status": "empty_chunk", "buffer_size": len(buffer)}
        
        buffer.extend(audio_chunk)
        pipeline["stats"]["chunks_processed"] += 1
        
        if len(buffer) < self.min_chunk_size and len(buffer) < self.max_buffer_size:
            return {"status": "buffering", "buffer_size": len(buffer)}
        
        audio_data = bytes(buffer)
        buffer.clear()
        
        if len(audio_data) < self.min_chunk_size:
            return {"status": "skipped", "reason": "chunk_too_small"}
        
        pipeline["is_processing"] = True
        
        try:
            transcription_result = await self._perform_stt(interview_id, audio_data)
            
            if not transcription_result.get("text"):
                pipeline["is_processing"] = False
                return {
                    "status": "no_speech", 
                    "transcription": transcription_result
                }
            
            if websocket_callback and transcription_result.get("text"):
                await websocket_callback({
                    "type": "transcription_update",
                    "text": transcription_result["text"],
                    "confidence": transcription_result.get("confidence", 0.0),
                    "is_final": True,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            text = transcription_result["text"].strip()
            if len(text.split()) >= 2:
                analysis_result = await self._perform_analysis(interview_id, text)
           
                if websocket_callback and analysis_result:
                    await websocket_callback({
                        "type": "response_analysis",
                        "analysis": analysis_result,
                        "original_text": text,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                ai_response = await self._generate_ai_response(interview_id, text, analysis_result)
                
                if ai_response and ai_response.get("text"):
                    await self._stream_tts_response(
                        interview_id, ai_response["text"], websocket_callback
                    )
            
            pipeline["is_processing"] = False
            pipeline["stats"]["transcriptions"] += 1
            
            return {
                "status": "processed",
                "transcription": transcription_result,
                "text_length": len(text),
                "pipeline_stats": pipeline["stats"]
            }
            
        except Exception as e:
            pipeline["is_processing"] = False
            pipeline["stats"]["errors"] += 1
            logger.error(f"Error in pipeline processing: {str(e)}")
            raise
    
    async def _perform_stt(self, interview_id: str, audio_data: bytes) -> Dict[str, Any]:
        """Perform speech-to-text using available services"""
        try:
            if "elevenlabs" in self.services and self.services["elevenlabs"].is_available():
                result = await self.services["elevenlabs"].transcribe_audio_stream(audio_data)
                if result.get("text"):
                    return result
            
            if "stt" in self.services and self.services["stt"].is_available():
                result = await self.services["stt"].transcribe_audio(audio_data)
                return result
            
            return {
                "text": "",
                "confidence": 0.0,
                "source": "no_service_available"
            }
            
        except Exception as e:
            logger.error(f"STT error for interview {interview_id}: {str(e)}")
            return {"text": "", "confidence": 0.0, "error": str(e)}
    
    async def _perform_analysis(self, interview_id: str, text: str) -> Optional[Dict[str, Any]]:
        """Analyze candidate response using available AI or the InterviewAnalysisMock.analyze_response"""
        try:
            pipeline = self.active_pipelines[interview_id]
            context = pipeline["context"]
            current_question = pipeline.get("current_question", "")
            
            if "ai" in self.services and self.services["ai"].is_available():
                try:
                    analysis = await self.services["ai"].analyze_response(
                        question=current_question,
                        response=text,
                        context=context
                    )
                    if analysis and analysis.get("score") is not None:
                        return analysis
                except Exception as ai_error:
                    logger.warning(f"AI analysis failed, will use mock analyzer: {ai_error}")
            
            analysis = await self.mock_analyzer.analyze_response(
                question=current_question,
                response=text,
                context=context
            )
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis error for interview {interview_id}: {str(e)}")
            return await self._fallback_analysis(text, error=str(e))
    
    async def _generate_ai_response(
        self, 
        interview_id: str, 
        candidate_text: str, 
        analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate AI response/feedback based on analysis"""
        try:
            score = analysis.get("score", 5.0)
            
            if score >= 8.0:
                response_text = "Отличный ответ! Продолжим интервью."
            elif score >= 6.0:
                response_text = "Хороший ответ. Расскажите больше деталей."
            elif score >= 4.0:
                response_text = "Понятно. Можете привести конкретный пример?"
            else:
                response_text = "Спасибо за ответ. Перейдем к следующему вопросу."
            
            return {
                "text": response_text,
                "type": "feedback",
                "based_on_score": score
            }
            
        except Exception as e:
            logger.error(f"AI response generation error: {str(e)}")
            return {
                "text": "Спасибо за ваш ответ.",
                "type": "acknowledgment",
                "error": str(e)
            }
    
    async def _stream_tts_response(
        self, 
        interview_id: str, 
        text: str, 
        websocket_callback: Optional[Callable]
    ):
        """Stream TTS audio response back to client"""
        try:
            if not websocket_callback:
                return
            
            if "tts" in self.services:
                tts_service = self.services["tts"]
                
                await websocket_callback({
                    "type": "audio_start",
                    "text": text,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                chunk_count = 0
                async for audio_chunk in tts_service.synthesize_speech_stream(text):
                    await websocket_callback({
                        "type": "audio_chunk",
                        "data": audio_chunk,
                        "chunk_index": chunk_count,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    chunk_count += 1
                
                await websocket_callback({
                    "type": "audio_end",
                    "total_chunks": chunk_count,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                pipeline = self.active_pipelines[interview_id]
                pipeline["stats"]["audio_generated"] += 1
            
        except Exception as e:
            logger.error(f"TTS streaming error for interview {interview_id}: {str(e)}")
            if websocket_callback:
                await websocket_callback({
                    "type": "audio_error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
    
    async def _fallback_analysis(self, text: str, error: str = None) -> Dict[str, Any]:
        """Fallback analysis when all other methods fail"""
        word_count = len(text.split())
        
        if word_count == 0:
            score = 0.0
        elif word_count < 5:
            score = 4.0
        elif word_count < 15:
            score = 6.5
        else:
            score = 8.0
        
        return {
            "score": score,
            "feedback": f"Базовый анализ: {word_count} слов",
            "strengths": ["Участие в диалоге"] if word_count > 0 else [],
            "areas_for_improvement": ["Системная ошибка анализа"],
            "technical_accuracy": score,
            "communication_clarity": score,
            "relevance": score,
            "completeness": score,
            "keywords_matched": [],
            "sentiment": "neutral",
            "confidence_level": "medium",
            "recommendations": ["Продолжить интервью"],
            "word_count": word_count,
            "fallback": True,
            "error": error
        }
    
    def get_pipeline_status(self, interview_id: str) -> Optional[Dict[str, Any]]:
        """Get current pipeline status"""
        if interview_id not in self.active_pipelines:
            return None
        
        pipeline = self.active_pipelines[interview_id]
        return {
            "status": pipeline["status"],
            "started_at": pipeline["started_at"].isoformat(),
            "stats": pipeline["stats"],
            "is_processing": pipeline["is_processing"],
            "buffer_size": len(self.audio_buffers.get(interview_id, [])),
            "context": pipeline["context"]
        }
    
    def update_context(self, interview_id: str, context_updates: Dict[str, Any]):
        """Update pipeline context (e.g., current question)"""
        if interview_id in self.active_pipelines:
            self.active_pipelines[interview_id]["context"].update(context_updates)
            if "current_question" in context_updates:
                self.active_pipelines[interview_id]["current_question"] = context_updates["current_question"]
    
    def get_active_pipelines(self) -> list:
        """Get list of active pipeline IDs"""
        return [
            interview_id for interview_id, pipeline in self.active_pipelines.items()
            if pipeline["status"] == "active"
        ]