from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Dict, Any, Optional
import logging
import json
import io
from datetime import datetime

from app.services.elevenlabs_service import ElevenLabsService
from app.services.interview_analysis_mock import InterviewAnalysisMock
from app.services.text_to_speech import TextToSpeechService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime", tags=["Real-time Audio"])


# Dependency to get services (this would normally be injected)
async def get_elevenlabs_service() -> ElevenLabsService:
    return ElevenLabsService()

async def get_analysis_service() -> InterviewAnalysisMock:
    return InterviewAnalysisMock()

async def get_tts_service() -> TextToSpeechService:
    return TextToSpeechService()


@router.post("/stt")
async def test_speech_to_text(
    audio_file: UploadFile = File(...),
    language: str = Form("ru"),
    elevenlabs_service: ElevenLabsService = Depends(get_elevenlabs_service)
):
    """Test speech-to-text conversion with uploaded audio file"""
    try:
        if not audio_file.content_type or not audio_file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Process with ElevenLabs or fallback
        result = await elevenlabs_service.transcribe_audio_stream(audio_data)
        
        return {
            "status": "success",
            "transcription": result,
            "file_info": {
                "filename": audio_file.filename,
                "content_type": audio_file.content_type,
                "size_bytes": len(audio_data)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"STT test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.post("/analysis")
async def test_response_analysis(
    text: str = Form(...),
    question: str = Form(""),
    analysis_service: InterviewAnalysisMock = Depends(get_analysis_service)
):
    """Test response analysis with provided text"""
    try:
        if not text or len(text.strip()) < 3:
            raise HTTPException(status_code=400, detail="Text is too short for analysis")
        
        # Perform analysis
        context = {
            "position": "Software Developer",
            "questions_asked": 1,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        analysis_result = await analysis_service.analyze_response(
            question=question,
            response=text,
            context=context
        )
        
        return {
            "status": "success",
            "analysis": analysis_result,
            "input": {
                "text": text,
                "question": question,
                "text_length": len(text),
                "word_count": len(text.split())
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Analysis test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.post("/tts")
async def test_text_to_speech(
    text: str = Form(...),
    language: str = Form("ru"),
    stream: bool = Form(False),
    tts_service: TextToSpeechService = Depends(get_tts_service)
):
    """Test text-to-speech conversion"""
    try:
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 500:
            raise HTTPException(status_code=400, detail="Text is too long (max 500 characters)")
        
        if stream:
            # Return streaming audio
            async def audio_generator():
                chunk_count = 0
                async for audio_chunk in tts_service.synthesize_speech_stream(text, language):
                    yield audio_chunk
                    chunk_count += 1
                
                logger.info(f"Streamed {chunk_count} audio chunks for text: {text[:50]}...")
            
            return StreamingResponse(
                audio_generator(),
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": f"attachment; filename=tts_output.mp3",
                    "X-Text-Input": text[:100],
                    "X-Language": language
                }
            )
        else:
            # Return URL to generated file
            audio_url = await tts_service.synthesize_speech(text, language)
            
            return {
                "status": "success",
                "audio_url": audio_url,
                "input": {
                    "text": text,
                    "language": language,
                    "text_length": len(text),
                    "estimated_duration": tts_service.estimate_duration(text)
                },
                "timestamp": datetime.utcnow().isoformat()
            }

    except Exception as e:
        logger.error(f"TTS test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@router.post("/test-pipeline")
async def test_full_pipeline(
    audio_file: UploadFile = File(...),
    question: str = Form("Расскажите о вашем опыте программирования"),
    elevenlabs_service: ElevenLabsService = Depends(get_elevenlabs_service),
    analysis_service: InterviewAnalysisMock = Depends(get_analysis_service),
    tts_service: TextToSpeechService = Depends(get_tts_service)
):
    """Test the complete real-time pipeline: Audio -> STT -> Analysis -> TTS"""
    try:
        # Step 1: Speech-to-Text
        audio_data = await audio_file.read()
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        transcription = await elevenlabs_service.transcribe_audio_stream(audio_data)
        
        if not transcription.get("text"):
            return {
                "status": "no_speech",
                "message": "No speech detected in audio",
                "transcription": transcription
            }
        
        # Step 2: Analysis
        context = {
            "position": "Software Developer",
            "questions_asked": 1,
            "interview_id": "test_pipeline",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        analysis = await analysis_service.analyze_response(
            question=question,
            response=transcription["text"],
            context=context
        )
        
        # Step 3: Generate AI response based on analysis
        score = analysis.get("score", 5.0)
        if score >= 8.0:
            ai_response = "Отличный ответ! Очень подробно и технически грамотно."
        elif score >= 6.0:
            ai_response = "Хороший ответ. Можете рассказать больше деталей?"
        elif score >= 4.0:
            ai_response = "Понятно. Можете привести конкретный пример из практики?"
        else:
            ai_response = "Спасибо. Давайте перейдем к следующему вопросу."
        
        # Step 4: Text-to-Speech for AI response
        tts_url = await tts_service.synthesize_speech(ai_response, "ru")
        
        return {
            "status": "success",
            "pipeline_result": {
                "step_1_stt": {
                    "transcription": transcription,
                    "detected_text": transcription["text"]
                },
                "step_2_analysis": analysis,
                "step_3_ai_response": {
                    "text": ai_response,
                    "based_on_score": score
                },
                "step_4_tts": {
                    "audio_url": tts_url,
                    "response_text": ai_response
                }
            },
            "input_info": {
                "audio_file": audio_file.filename,
                "audio_size": len(audio_data),
                "question": question
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
        
    except Exception as e:
        logger.error(f"Pipeline test error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for real-time services"""
    try:
        # Test service availability
        elevenlabs_service = ElevenLabsService()
        analysis_service = InterviewAnalysisMock()
        tts_service = TextToSpeechService()
        
        # Get health status
        elevenlabs_health = await elevenlabs_service.health_check()
        tts_health = await tts_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "elevenlabs": elevenlabs_health,
                "analysis_mock": {
                    "status": "healthy",
                    "features": ["response_analysis", "feedback_generation", "scoring"]
                },
                "text_to_speech": tts_health
            },
            "capabilities": {
                "speech_to_text": elevenlabs_service.is_available(),
                "response_analysis": True,
                "text_to_speech": tts_service.is_available(),
                "real_time_pipeline": True
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/voices")
async def get_available_voices(
    elevenlabs_service: ElevenLabsService = Depends(get_elevenlabs_service)
):
    """Get available voices for TTS"""
    try:
        voices = await elevenlabs_service.get_available_voices()
        
        return {
            "status": "success",
            "voices": voices,
            "total_voices": len(voices),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get voices error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voices error: {str(e)}")