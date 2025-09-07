from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import logging
import uvicorn

from app.config import settings
from app.database import engine, Base
from app.api.v1.router import router as api_router
from app.api.websocket import websocket_manager
from app.services.speech_to_text import SpeechToTextService
from app.services.ai_analysis import AIAnalysisService
from app.services.text_to_speech import TextToSpeechService
from app.services.scoring import ScoringService
from app.services.elevenlabs_service import ElevenLabsService

def configure_logging():
    """Configure application logging with appropriate level and format."""
    logging.basicConfig(
        level=logging.INFO if not settings.DEBUG else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

configure_logging()

logger = logging.getLogger(__name__)

def create_fastapi_app():
    """Create and configure FastAPI application instance."""
    return FastAPI(
        title=settings.APP_NAME,
        description="AI-powered interview system with state machine",
        version=settings.VERSION,
        debug=settings.DEBUG
    )

app = create_fastapi_app()

def configure_middleware():
    """Configure CORS and compression middleware for the application."""
    # Currently using development CORS settings - allow all origins
    # In production, should use specific allowed origins from settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development mode
        allow_credentials=False,  # Must be False when allow_origins=["*"]
        allow_methods=["*"],
        allow_headers=["*"],
    )

configure_middleware()

def configure_compression_and_routes():
    """Configure compression middleware and mount static files and API routes."""
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.include_router(api_router)

configure_compression_and_routes()


@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting HR Avatar Backend...")
    
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    logger.info("Initializing services...")
    try:
        elevenlabs_service = ElevenLabsService()
        if elevenlabs_service.is_available():
            logger.info("✅ ElevenLabs service is available")
        else:
            logger.warning("⚠️ ElevenLabs service is not available")
    except Exception as e:
        logger.error(f"❌ Error initializing ElevenLabs service: {e}")
    
    try:
        tts_service = TextToSpeechService()
        if tts_service.is_available():
            logger.info("✅ Text-to-Speech service is available")
        else:
            logger.warning("⚠️ Text-to-Speech service is not available")
    except Exception as e:
        logger.error(f"❌ Error initializing TTS service: {e}")
    
    logger.info("HR Avatar Backend started successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down HR Avatar Backend...")
    
    active_interviews = websocket_manager.get_active_interviews()
    logger.info(f"Cleaning up {len(active_interviews)} active interviews")
    for interview_id in active_interviews:
        await websocket_manager.disconnect(interview_id)


@app.websocket("/ws/{interview_id}")
async def websocket_endpoint(websocket: WebSocket, interview_id: str):
    """WebSocket endpoint for real-time interview communication."""
    logger.info(f"New WebSocket connection for interview: {interview_id}")
    await websocket_manager.connect(websocket, interview_id)


@app.get("/")
async def root():
    """Root endpoint providing API information and available endpoints."""
    return {
        "message": "HR Avatar Backend API",
        "version": settings.VERSION,
        "docs_url": "/docs" if settings.DEBUG else None,
        "health_check": "/api/v1/health",
        "websocket_example": "/ws/interview_id",
        "demo_page": "/demo"
    }


@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Demo page for WebSocket real-time functionality testing."""
    try:
        with open("static/demo.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Demo page not found</h1><p>Please ensure static/demo.html exists</p>",
            status_code=404
        )
@app.exception_handler(WebSocketDisconnect)
async def websocket_disconnect_handler(request, exc):
    """Handle WebSocket disconnections gracefully."""
    logger.info("WebSocket disconnected")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors with appropriate response based on debug mode."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    if settings.DEBUG:
        return {
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    else:
        return {
            "error": "Internal server error"
        }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
