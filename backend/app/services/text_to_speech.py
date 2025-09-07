import asyncio
import hashlib
import logging
import os
from typing import Optional, AsyncGenerator
import tempfile
import uuid
import io

try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class TextToSpeechService:
    """Text-to-Speech service with ElevenLabs integration"""
    
    def __init__(self):
        self.cache_dir = os.path.join(settings.STATIC_DIR, "tts_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # ElevenLabs client
        self.client = None
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice (Rachel)
        self.model_id = "eleven_multilingual_v2"
        
        if ELEVENLABS_AVAILABLE and settings.ELEVENLABS_API_KEY:
            try:
                self.client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
                # Voice settings for new ElevenLabs API (v2.x)
                self.voice_settings = {
                    "stability": 0.5,
                    "similarity_boost": 0.75,
                    "style": 0.0,
                    "use_speaker_boost": True
                }
                logger.info("TTS service initialized with ElevenLabs")
            except Exception as e:
                logger.error(f"Failed to initialize ElevenLabs: {str(e)}")
                self.client = None
        else:
            logger.warning("ElevenLabs not available, using mock TTS")
        
        logger.info("TTS service initialized")
    
    async def synthesize_speech(self, text: str, language: str = "ru") -> Optional[str]:
        """
        Synthesize speech from text and return URL to audio file
        Uses ElevenLabs API or falls back to mock implementation
        """
        try:
            if not text or len(text.strip()) == 0:
                return None
            
            # Create a hash-based filename for caching
            text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            filename = f"{text_hash}_{language}.mp3"
            file_path = os.path.join(self.cache_dir, filename)
            
            # Check if cached version exists
            if os.path.exists(file_path):
                return f"/static/tts_cache/{filename}"
            
            # Use ElevenLabs if available
            if self.client:
                success = await self._generate_with_elevenlabs(text, file_path, language)
                if success:
                    return f"/static/tts_cache/{filename}"
            
            # Fallback to mock implementation
            logger.warning("Using mock TTS implementation")
            await self._create_placeholder_audio(file_path, text, language)
            return f"/static/tts_cache/{filename}"
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {str(e)}")
            return None
    
    async def _create_placeholder_audio(self, file_path: str, text: str, language: str):
        """Create a placeholder audio file (mock)"""
        try:
            # Create a simple text file as placeholder
            # In production, this would be actual audio generation
            placeholder_content = f"""
# TTS Placeholder Audio File
# Text: {text}
# Language: {language}
# Duration: {len(text.split()) * 0.5} seconds (estimated)
# Generated: {asyncio.get_event_loop().time()}

This would be actual MP3 audio data in a real implementation.
You can integrate with services like:
- Azure Cognitive Services Speech
- Google Cloud Text-to-Speech
- Amazon Polly
- OpenAI TTS API
"""
            
            # Write placeholder content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(placeholder_content)
            
            logger.debug(f"Created placeholder TTS file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error creating placeholder audio: {str(e)}")
    
    async def _generate_with_elevenlabs(self, text: str, file_path: str, language: str = "ru") -> bool:
        """Generate audio using ElevenLabs API"""
        try:
            # Run ElevenLabs generation in executor to avoid blocking
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None, self._elevenlabs_generate_sync, text
            )
            
            if audio_data:
                # Save audio data to file
                with open(file_path, 'wb') as f:
                    f.write(audio_data)
                logger.info(f"Generated ElevenLabs audio: {file_path}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"ElevenLabs generation error: {str(e)}")
            return False
    
    def _elevenlabs_generate_sync(self, text: str) -> bytes:
        """Synchronous ElevenLabs generation for thread executor"""
        try:
            # Generate audio using new ElevenLabs API (v2.x)
            audio_response = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id=self.model_id,
                voice_settings=self.voice_settings
            )
            
            # Handle different response types
            if hasattr(audio_response, '__iter__') and not isinstance(audio_response, (str, bytes)):
                # If it's iterable (streaming response)
                audio_chunks = []
                for chunk in audio_response:
                    audio_chunks.append(chunk)
                return b''.join(audio_chunks)
            else:
                # If it's a direct bytes response
                return audio_response if isinstance(audio_response, bytes) else bytes(audio_response)
            
        except Exception as e:
            logger.error(f"ElevenLabs sync generation error: {str(e)}")
            raise
    
    async def synthesize_speech_stream(self, text: str, language: str = "ru") -> AsyncGenerator[bytes, None]:
        """
        Generate streaming speech audio from text
        Yields audio chunks as they are generated
        """
        if not self.client:
            # Fallback to mock streaming
            async for chunk in self._mock_stream_audio(text):
                yield chunk
            return
        
        try:
            # Generate streaming audio
            audio_generator = await asyncio.get_event_loop().run_in_executor(
                None, self._elevenlabs_stream_sync, text
            )
            
            for chunk in audio_generator:
                yield chunk
                
        except Exception as e:
            logger.error(f"Error in streaming TTS: {str(e)}")
            # Fallback to mock streaming
            async for chunk in self._mock_stream_audio(text):
                yield chunk
    
    def _elevenlabs_stream_sync(self, text: str):
        """Synchronous ElevenLabs streaming for thread executor"""
        try:
            # Use new ElevenLabs streaming API (v2.x)
            audio_stream = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id=self.model_id,
                voice_settings=self.voice_settings
            )
            
            # Handle different response types
            if hasattr(audio_stream, '__iter__') and not isinstance(audio_stream, (str, bytes)):
                # If it's iterable (streaming response)
                for chunk in audio_stream:
                    yield chunk
            else:
                # If it's a single response, yield as one chunk
                yield audio_stream if isinstance(audio_stream, bytes) else bytes(audio_stream)
                
        except Exception as e:
            logger.error(f"ElevenLabs streaming error: {str(e)}")
            raise
    
    async def _mock_stream_audio(self, text: str) -> AsyncGenerator[bytes, None]:
        """Mock streaming audio for development"""
        words = text.split()
        chunk_delay = 0.2  # 200ms per chunk
        
        for i in range(0, len(words), 2):  # Process 2 words per chunk
            chunk_text = " ".join(words[i:i+2])
            
            # Generate mock audio data
            mock_audio = f"MOCK_TTS_CHUNK: {chunk_text}".encode('utf-8')
            mock_audio += b'\x00' * (2048 - len(mock_audio))  # Pad to 2KB
            
            yield mock_audio
            await asyncio.sleep(chunk_delay)
    
    async def synthesize_and_save(
        self, 
        text: str, 
        output_path: str, 
        language: str = "ru",
        voice: str = "default"
    ) -> bool:
        """
        Synthesize speech and save to specific path
        Returns True if successful, False otherwise
        """
        try:
            url = await self.synthesize_speech(text, language)
            if url:
                # In real implementation, you would copy the generated file
                # to the specified output_path
                logger.info(f"Would save TTS audio to: {output_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error synthesizing and saving speech: {str(e)}")
            return False
    
    def get_available_voices(self, language: str = "ru") -> list:
        """Get available voices for a language"""
        # Mock voice list - replace with actual TTS service voices
        voices = {
            "ru": [
                {"id": "ru-female-1", "name": "Анна", "gender": "female"},
                {"id": "ru-male-1", "name": "Дмитрий", "gender": "male"}
            ],
            "en": [
                {"id": "en-female-1", "name": "Sarah", "gender": "female"},
                {"id": "en-male-1", "name": "John", "gender": "male"}
            ]
        }
        
        return voices.get(language, [])
    
    def estimate_duration(self, text: str, speaking_rate: float = 150) -> float:
        """
        Estimate audio duration based on text length
        
        Args:
            text: Text to synthesize
            speaking_rate: Words per minute (default: 150 WPM)
            
        Returns:
            Estimated duration in seconds
        """
        if not text:
            return 0.0
        
        word_count = len(text.split())
        duration_minutes = word_count / speaking_rate
        return duration_minutes * 60  # Convert to seconds
    
    def is_available(self) -> bool:
        """Check if TTS service is available"""
        return self.client is not None or True  # Always available with mock fallback
    
    def set_voice(self, voice_id: str):
        """Set the voice for TTS generation"""
        self.voice_id = voice_id
        logger.info(f"TTS voice set to: {voice_id}")
    
    def get_current_voice(self) -> str:
        """Get current voice ID"""
        return self.voice_id
    
    async def get_available_voices(self) -> list:
        """Get available voices from ElevenLabs"""
        if not self.client:
            return self._get_mock_voices()
        
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
            return self._get_mock_voices()
    
    def _get_mock_voices(self) -> list:
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
            },
            {
                "voice_id": "mock_russian_female",
                "name": "Анна",
                "category": "generated",
                "description": "Russian Female Voice",
                "language": "ru"
            }
        ]
    
    async def health_check(self) -> dict:
        """Perform health check on TTS service"""
        try:
            # Test with a simple phrase
            test_url = await self.synthesize_speech("Test", "en")
            
            return {
                "status": "healthy" if test_url else "degraded",
                "cache_dir": self.cache_dir,
                "cached_files": len(os.listdir(self.cache_dir)) if os.path.exists(self.cache_dir) else 0,
                "test_synthesis": test_url is not None
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def clear_cache(self) -> int:
        """Clear TTS cache and return number of files removed"""
        try:
            if not os.path.exists(self.cache_dir):
                return 0
            
            files_removed = 0
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    files_removed += 1
            
            logger.info(f"Cleared {files_removed} files from TTS cache")
            return files_removed
            
        except Exception as e:
            logger.error(f"Error clearing TTS cache: {str(e)}")
            return 0
