from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_user, get_optional_current_user
from app.schemas.interview import (
    InterviewCreate, InterviewUpdate, InterviewResponse, 
    InterviewListResponse, InterviewSummary, InterviewStats
)
from app.models.interview import Interview
from app.models.candidate import Candidate
from app.api.websocket import websocket_manager

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/", response_model=InterviewResponse)
async def create_interview(
    interview: InterviewCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new interview session"""
    
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Create interview
    db_interview = Interview(
        candidate_id=interview.candidate_id,
        interviewer_id=interview.interviewer_id or current_user["id"],
        position=interview.position,
        interview_type=interview.interview_type,
        scheduled_at=interview.scheduled_at,
        max_questions=interview.max_questions,
        estimated_duration=interview.estimated_duration,
        interview_plan=interview.interview_plan,
        current_state="START",
        timeline=[],
        context={}
    )
    
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    
    return db_interview


@router.get("/", response_model=InterviewListResponse)
async def list_interviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    position: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List interviews with optional filtering"""
    
    query = db.query(Interview)
    
    # Apply filters
    if status:
        query = query.filter(Interview.status == status)
    if position:
        query = query.filter(Interview.position.ilike(f"%{position}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    interviews = query.offset(skip).limit(limit).all()
    
    return InterviewListResponse(
        interviews=interviews,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get interview details"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    return interview


@router.put("/{interview_id}", response_model=InterviewResponse)
async def update_interview(
    interview_id: uuid.UUID,
    interview_update: InterviewUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update interview information"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Update fields
    update_data = interview_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(interview, field, value)
    
    interview.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(interview)
    
    return interview


@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete interview"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    db.delete(interview)
    db.commit()
    
    return {"message": "Interview deleted successfully"}


@router.post("/{interview_id}/start")
async def start_interview(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Start an interview session"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview.status != "scheduled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start interview with status: {interview.status}"
        )
    
    # Update interview status
    interview.status = "in_progress"
    interview.started_at = datetime.utcnow()
    interview.current_state = "START"
    
    db.commit()
    
    return {
        "message": "Interview started",
        "interview_id": interview_id,
        "websocket_url": f"/ws/{interview_id}",
        "status": interview.status
    }


@router.post("/{interview_id}/end")
async def end_interview(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """End an interview session"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    if interview.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot end interview with status: {interview.status}"
        )
    
    # Update interview status
    interview.status = "completed"
    interview.ended_at = datetime.utcnow()
    interview.current_state = "COMPLETE"
    
    # Calculate final score if not set
    if interview.total_score == 0.0:
        from app.services.scoring import ScoringService
        scoring_service = ScoringService()
        
        # Get responses for scoring
        responses = []
        for response in interview.responses:
            responses.append({
                "score": response.score,
                "category": response.question.category if response.question else "general"
            })
        
        score_data = scoring_service.calculate_interview_score(responses)
        interview.total_score = score_data.get("average_score", 0.0)
    
    db.commit()
    
    return {
        "message": "Interview ended",
        "interview_id": interview_id,
        "total_score": interview.total_score,
        "status": interview.status
    }


@router.get("/{interview_id}/timeline")
async def get_interview_timeline(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get interview timeline and progress"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Calculate timeline statistics
    questions_asked = len([entry for entry in interview.timeline if "question" in entry])
    total_duration = 0
    
    if interview.started_at and interview.ended_at:
        total_duration = (interview.ended_at - interview.started_at).total_seconds()
    elif interview.started_at:
        total_duration = (datetime.utcnow() - interview.started_at).total_seconds()
    
    return {
        "timeline": interview.timeline,
        "current_state": interview.current_state,
        "total_score": interview.total_score,
        "questions_asked": questions_asked,
        "max_questions": interview.max_questions,
        "duration_seconds": int(total_duration),
        "status": interview.status,
        "progress_percentage": min(100, (questions_asked / interview.max_questions) * 100)
    }


@router.get("/{interview_id}/summary", response_model=InterviewSummary)
async def get_interview_summary(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get interview summary"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Get candidate name
    candidate_name = f"{interview.candidate.first_name} {interview.candidate.last_name}"
    questions_asked = len(interview.responses)
    
    return InterviewSummary(
        id=interview.id,
        candidate_name=candidate_name,
        position=interview.position,
        status=interview.status,
        current_state=interview.current_state,
        scheduled_at=interview.scheduled_at,
        started_at=interview.started_at,
        ended_at=interview.ended_at,
        total_score=interview.total_score,
        questions_asked=questions_asked,
        max_questions=interview.max_questions,
        recommendation=interview.recommendation
    )


@router.get("/{interview_id}/status")
async def get_interview_status(
    interview_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_current_user)  # Allow without auth for frontend polling
):
    """Get real-time interview status"""
    
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview not found"
        )
    
    # Check WebSocket connection status
    is_active = websocket_manager.is_interview_active(str(interview_id))
    connection_count = websocket_manager.get_connection_count(str(interview_id))
    
    return {
        "interview_id": interview_id,
        "status": interview.status,
        "current_state": interview.current_state,
        "websocket_active": is_active,
        "connected_clients": connection_count,
        "last_updated": interview.updated_at.isoformat() if interview.updated_at else None
    }


@router.get("/stats/overview", response_model=InterviewStats)
async def get_interview_stats(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get interview statistics"""
    
    from datetime import timedelta
    from sqlalchemy import func
    
    # Date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query interviews in date range
    base_query = db.query(Interview).filter(
        Interview.created_at >= start_date,
        Interview.created_at <= end_date
    )
    
    # Count by status
    total_interviews = base_query.count()
    completed_interviews = base_query.filter(Interview.status == "completed").count()
    in_progress_interviews = base_query.filter(Interview.status == "in_progress").count()
    scheduled_interviews = base_query.filter(Interview.status == "scheduled").count()
    
    # Calculate averages for completed interviews
    completed_query = base_query.filter(
        Interview.status == "completed",
        Interview.total_score > 0
    )
    
    avg_score = 0.0
    avg_duration = 0.0
    
    completed_list = completed_query.all()
    if completed_list:
        scores = [i.total_score for i in completed_list if i.total_score > 0]
        durations = []
        
        for interview in completed_list:
            if interview.started_at and interview.ended_at:
                duration = (interview.ended_at - interview.started_at).total_seconds() / 60
                durations.append(duration)
        
        if scores:
            avg_score = sum(scores) / len(scores)
        if durations:
            avg_duration = sum(durations) / len(durations)
    
    return InterviewStats(
        total_interviews=total_interviews,
        completed_interviews=completed_interviews,
        in_progress_interviews=in_progress_interviews,
        scheduled_interviews=scheduled_interviews,
        average_score=round(avg_score, 2),
        average_duration_minutes=round(avg_duration, 2)
    )