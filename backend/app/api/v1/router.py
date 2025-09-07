from fastapi import APIRouter

from app.api.v1 import interviews, candidates, auth, vacancies, interview_links, candidate_access, realtime, resumes

router = APIRouter(prefix="/api/v1")

def configure_api_routes():
    """
    Configure all API endpoint routers.
    
    Includes all available API modules: authentication, vacancies,
    interview links, candidate access, interviews, candidates, resumes, and realtime.
    """
    router.include_router(auth.router)
    router.include_router(vacancies.router)
    router.include_router(interview_links.router)
    router.include_router(candidate_access.router)
    router.include_router(interviews.router)
    router.include_router(candidates.router)
    router.include_router(resumes.router)
    router.include_router(realtime.router)

configure_api_routes()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for API status monitoring.
    
    Returns:
        Dict: API health status and version information
    """
    return {
        "status": "healthy",
        "message": "HR Avatar Backend API is running",
        "version": "1.0.0"
    }


@router.get("/info")
async def api_info():
    """
    API information endpoint providing available endpoints and documentation.
    
    Returns:
        Dict: Complete API information including all available endpoints
    """
    return {
        "name": "HR Avatar Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/v1/health",
            "auth": "/api/v1/auth",
            "vacancies": "/api/v1/vacancies",
            "interview-links": "/api/v1/interview-links",
            "candidate-access": "/api/v1/candidate",
            "interviews": "/api/v1/interviews",
            "candidates": "/api/v1/candidates",
            "resumes": "/api/v1/resumes",
            "realtime": "/api/v1/realtime",
            "websocket": "/ws/{interview_id}",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }