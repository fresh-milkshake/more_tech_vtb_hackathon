import asyncio
import io
import logging
from typing import Dict, Any, Optional, AsyncGenerator
import base64
import json
from datetime import datetime

try:
    from elevenlabs import ElevenLabs
    import pydub
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class ElevenLabsService:
    """
    Real-time audio processing service using ElevenLabs API.
    
    Provides text-to-speech synthesis with streaming capabilities,
    voice cloning, and real-time audio processing for interview scenarios.
    """
    
    def __init__(self):
        """
        Initialize ElevenLabs service with default voice and model settings.
        
        Sets up the ElevenLabs client if API key is available and loads
        optimal voice settings for real-time processing.
        """
        self.client = None
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
        self.model_id = "eleven_multilingual_v2"
        self.chunk_size = 1024
        self.sample_rate = 16000
        
        if ELEVENLABS_AVAILABLE and settings.ELEVENLABS_API_KEY:
            try:
                self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
                logger.info("ElevenLabs client initialized successfully")
                self._load_voice_settings()
            except Exception as e:
                logger.error(f"Failed to initialize ElevenLabs client: {str(e)}")
                self.client = None
        else:
            logger.warning("ElevenLabs not available or API key not set")
    
    def _load_voice_settings(self):
        """
        Load optimal voice settings for real-time processing.
        
        Configures voice parameters for the new ElevenLabs API (v2.x)
        to ensure high-quality, natural-sounding speech synthesis.
        """
        try:
            self.voice_settings = {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        except Exception as e:
            logger.warning(f"Could not load voice settings: {e}")
            self.voice_settings = None
    
    async def transcribe_audio_stream(self, audio_chunk: bytes) -> Dict[str, Any]:
        """
        Transcribe audio chunk to text using ElevenLabs Speech-to-Text
        """
        if not self.client:
            return await self._mock_transcription(audio_chunk)
        
        try:
            # Convert audio chunk to proper format
            audio_data = await self._process_audio_chunk(audio_chunk)
            
            if not audio_data:
                return {"text": "", "confidence": 0.0, "is_final": False}
            
            # Use ElevenLabs STT API
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._transcribe_sync, audio_data
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in ElevenLabs transcription: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "is_final": False,
                "error": str(e)
            }
    
    def _transcribe_sync(self, audio_data: bytes) -> Dict[str, Any]:
        """Synchronous transcription for thread executor"""
        try:
            # Use new ElevenLabs STT API (v2.x) with correct parameters
            response = self.client.speech_to_text.convert(
                file=audio_data,  # Correct parameter name
                model_id="scribe_v1"  # Valid model name from API error
            )
            
            # Extract transcription results from new API response
            text = ""
            confidence = 0.8
            
            if hasattr(response, 'text'):
                text = response.text
            elif hasattr(response, 'chunks') and response.chunks:
                # Handle chunked response
                text = " ".join([chunk.text for chunk in response.chunks if hasattr(chunk, 'text')])
            else:
                # Try to convert response to string
                text = str(response) if response else ""
            
            if hasattr(response, 'confidence'):
                confidence = response.confidence
            elif hasattr(response, 'chunks') and response.chunks:
                # Average confidence from chunks
                confidences = [chunk.confidence for chunk in response.chunks if hasattr(chunk, 'confidence')]
                confidence = sum(confidences) / len(confidences) if confidences else 0.8
            
            return {
                "text": text.strip() if text else "",
                "confidence": float(confidence),
                "is_final": True,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "elevenlabs_v2"
            }
            
        except Exception as e:
            logger.error(f"ElevenLabs STT error: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "is_final": False,
                "error": str(e)
            }
    
    async def generate_speech_stream(self, text: str, voice_id: Optional[str] = None) -> AsyncGenerator[bytes, None]:
        """
        Generate speech audio stream from text using ElevenLabs TTS
        """
        if not self.client:
            async for chunk in self._mock_tts_stream(text):
                yield chunk
            return
        
        try:
            voice = voice_id or self.voice_id
            
            # Generate speech using ElevenLabs streaming
            audio_generator = await asyncio.get_event_loop().run_in_executor(
                None, self._generate_speech_sync, text, voice
            )
            
            for chunk in audio_generator:
                yield chunk
                
        except Exception as e:
            logger.error(f"Error in ElevenLabs TTS: {str(e)}")
            # Fallback to mock on error
            async for chunk in self._mock_tts_stream(text):
                yield chunk
    
    def _generate_speech_sync(self, text: str, voice_id: str):
        """Synchronous speech generation for thread executor"""
        try:
            # Use new ElevenLabs TTS API (v2.x)
            audio_stream = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id=self.model_id,
                voice_settings=self.voice_settings
            )
            
            # Stream the audio data
            if hasattr(audio_stream, '__iter__'):
                # If it's iterable (streaming response)
                for chunk in audio_stream:
                    yield chunk
            else:
                # If it's a direct response, yield as single chunk
                yield audio_stream
                
        except Exception as e:
            logger.error(f"ElevenLabs TTS sync error: {str(e)}")
            raise
    
    async def _process_audio_chunk(self, audio_chunk: bytes) -> Optional[bytes]:
        """Process and validate audio chunk for ElevenLabs"""
        try:
            # Check minimum chunk size
            if len(audio_chunk) < 1000:  # Too small to process
                return None
            
            # Convert to proper format if needed using pydub
            if ELEVENLABS_AVAILABLE:
                try:
                    # Try to load as audio and convert to MP3
                    audio = pydub.AudioSegment.from_raw(
                        io.BytesIO(audio_chunk),
                        sample_width=2,  # 16-bit
                        frame_rate=self.sample_rate,
                        channels=1  # Mono
                    )
                    
                    # Export to MP3 format for ElevenLabs
                    output_buffer = io.BytesIO()
                    audio.export(output_buffer, format="mp3")
                    return output_buffer.getvalue()
                    
                except Exception as e:
                    logger.debug(f"Could not process audio chunk: {e}")
                    # Return original chunk if processing fails
                    return audio_chunk
            
            return audio_chunk
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            return None
    
    async def _mock_transcription(self, audio_chunk: bytes) -> Dict[str, Any]:
        """Mock transcription for development/testing"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        chunk_size = len(audio_chunk)
        
        # Simulate realistic transcription based on chunk size
        if chunk_size < 2000:
            text = ""
            confidence = 0.0
        elif chunk_size < 8000:
            text = "да"
            confidence = 0.7
        elif chunk_size < 15000:
            text = "У меня есть опыт программирования"
            confidence = 0.85
        else:
            text = "У меня есть несколько лет опыта работы с Python и веб-разработкой"
            confidence = 0.9
        
        return {
            "text": text,
            "confidence": confidence,
            "is_final": True,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "mock",
            "chunk_size": chunk_size
        }
    
    async def _mock_tts_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """Mock TTS streaming for development"""
        # Simulate streaming by yielding chunks
        words = text.split()
        chunk_delay = 0.1  # 100ms per chunk
        
        for i in range(0, len(words), 3):  # Process 3 words per chunk
            chunk_text = " ".join(words[i:i+3])
            
            # Generate mock audio data (just bytes representing the text)
            mock_audio = f"MOCK_AUDIO_CHUNK: {chunk_text}".encode('utf-8')
            mock_audio += b'\x00' * (1024 - len(mock_audio))  # Pad to 1KB
            
            yield mock_audio
            await asyncio.sleep(chunk_delay)
    
    async def get_available_voices(self) -> list:
        """Get available voices from ElevenLabs"""
        if not self.client:
            return self._mock_voices()
        
        try:
            # Use new ElevenLabs voices API (v2.x)
            voices_response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.client.voices.get_all()
            )
            
            # Handle different response types from new API
            voices = voices_response.voices if hasattr(voices_response, 'voices') else voices_response
            
            return [
                {
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', 'generated'),
                    "description": getattr(voice, 'description', ''),
                    "language": getattr(voice, 'language', 'en'),
                }
                for voice in voices
            ]
            
        except Exception as e:
            logger.error(f"Error fetching voices: {str(e)}")
            return self._mock_voices()
    
    def _mock_voices(self) -> list:
        """Mock voice list for development"""
        return [
            {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "name": "Rachel",
                "category": "generated",
                "description": "Young American Female",
                "language": "en"
            },
            {
                "voice_id": "29vD33N1CtxCmqQRPOHJ",
                "name": "Drew",
                "category": "generated", 
                "description": "Young American Male",
                "language": "en"
            }
        ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Check ElevenLabs service health"""
        try:
            if not self.client:
                return {
                    "status": "unavailable",
                    "error": "ElevenLabs client not initialized"
                }
            
            # Test with a simple request
            voices = await self.get_available_voices()
            
            return {
                "status": "healthy",
                "available_voices": len(voices),
                "voice_id": self.voice_id,
                "model_id": self.model_id,
                "api_available": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def is_available(self) -> bool:
        """Check if ElevenLabs service is available"""
        return self.client is not None

    def set_voice(self, voice_id: str):
        """Set the voice for TTS generation"""
        self.voice_id = voice_id
        logger.info(f"Voice set to: {voice_id}")

    def get_current_voice(self) -> str:
        """Get current voice ID"""
        return self.voice_id
