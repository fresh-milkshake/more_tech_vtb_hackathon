import asyncio
import io
import logging
import numpy as np
from typing import Dict, Any, Optional
import tempfile
import os

try:
    import whisper
    import librosa
    import soundfile as sf
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """Speech-to-Text service using OpenAI Whisper"""
    
    def __init__(self):
        self.model = None
        self.model_name = settings.WHISPER_MODEL
        self.confidence_threshold = 0.7
        
        if WHISPER_AVAILABLE:
            try:
                self._load_model()
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {str(e)}")
                self.model = None
        else:
            logger.warning("Whisper not available. Install with: pip install openai-whisper")
    
    def _load_model(self):
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise
    
    async def transcribe_audio(self, audio_data: bytes, language: str = "ru") -> Dict[str, Any]:
        """Transcribe audio data to text"""
        if not WHISPER_AVAILABLE or not self.model:
            # Fallback for when Whisper is not available
            return await self._mock_transcription(audio_data)
        
        try:
            # Process audio in background thread to avoid blocking
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._transcribe_sync, audio_data, language
            )
            return result
            
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "segments": [],
                "error": str(e)
            }
    
    def _transcribe_sync(self, audio_data: bytes, language: str = "ru") -> Dict[str, Any]:
        """Synchronous transcription for executor"""
        try:
            # Convert bytes to temporary audio file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                
                try:
                    # Write audio data to temporary file
                    temp_file.write(audio_data)
                    temp_file.flush()
                    
                    # Load audio with librosa
                    audio_array, sample_rate = librosa.load(
                        temp_path, 
                        sr=settings.AUDIO_SAMPLE_RATE,
                        mono=True
                    )
                    
                    # Transcribe with Whisper
                    result = self.model.transcribe(
                        audio_array,
                        language=language,
                        task="transcribe",
                        verbose=False
                    )
                    
                    # Calculate confidence from segments
                    confidence = self._calculate_confidence(result)
                    
                    return {
                        "text": result["text"].strip(),
                        "confidence": confidence,
                        "language": result.get("language", language),
                        "segments": result.get("segments", []),
                        "duration": len(audio_array) / sample_rate
                    }
                    
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                        
        except Exception as e:
            logger.error(f"Sync transcription error: {str(e)}")
            raise
    
    def _calculate_confidence(self, whisper_result: Dict) -> float:
        """Calculate average confidence from Whisper segments"""
        segments = whisper_result.get("segments", [])
        if not segments:
            return 0.0
        
        # Whisper provides avg_logprob, convert to confidence score
        confidences = []
        for segment in segments:
            # Convert log probability to confidence (approximate)
            log_prob = segment.get("avg_logprob", -1.0)
            confidence = max(0.0, min(1.0, np.exp(log_prob)))
            confidences.append(confidence)
        
        return float(np.mean(confidences)) if confidences else 0.0
    
    async def _mock_transcription(self, audio_data: bytes) -> Dict[str, Any]:
        """Mock transcription for development/testing"""
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Mock response based on audio data length
        data_length = len(audio_data)
        
        if data_length < 1000:
            text = ""
            confidence = 0.0
        elif data_length < 5000:
            text = "Yes"
            confidence = 0.8
        elif data_length < 10000:
            text = "I have experience with Python and web development."
            confidence = 0.85
        else:
            text = "I have several years of experience working with Python, particularly in web development using frameworks like Django and FastAPI. I've also worked with databases and API development."
            confidence = 0.9
        
        return {
            "text": text,
            "confidence": confidence,
            "language": "en",
            "segments": [
                {
                    "start": 0.0,
                    "end": 2.0,
                    "text": text,
                    "avg_logprob": -0.2
                }
            ] if text else [],
            "duration": 2.0,
            "mock": True
        }
    
    async def transcribe_file(self, file_path: str, language: str = "ru") -> Dict[str, Any]:
        """Transcribe audio file"""
        try:
            with open(file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            return await self.transcribe_audio(audio_data, language)
            
        except Exception as e:
            logger.error(f"Error transcribing file {file_path}: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if STT service is available"""
        return WHISPER_AVAILABLE and self.model is not None