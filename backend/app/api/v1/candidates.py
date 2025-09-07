from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.candidate import (
    CandidateCreate, CandidateUpdate, CandidateResponse, CandidateListResponse
)
from app.models.candidate import Candidate

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/", response_model=CandidateResponse)
async def create_candidate(
    candidate: CandidateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new candidate"""
    
    # Check if candidate with email already exists
    existing_candidate = db.query(Candidate).filter(Candidate.email == candidate.email).first()
    if existing_candidate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate with this email already exists"
        )
    
    # Create candidate
    db_candidate = Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    
    return db_candidate


@router.get("/", response_model=CandidateListResponse)
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    position: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List candidates with optional filtering and search"""
    
    query = db.query(Candidate)
    
    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Candidate.first_name.ilike(search_filter)) |
            (Candidate.last_name.ilike(search_filter)) |
            (Candidate.email.ilike(search_filter)) |
            (Candidate.current_position.ilike(search_filter))
        )
    
    # Apply status filter
    if status:
        query = query.filter(Candidate.status == status)
    
    # Apply position filter
    if position:
        query = query.filter(Candidate.applied_position.ilike(f"%{position}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    candidates = query.offset(skip).limit(limit).all()
    
    return CandidateListResponse(
        candidates=candidates,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get candidate details"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: uuid.UUID,
    candidate_update: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update candidate information"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Check if email is being updated and doesn't conflict
    if candidate_update.email and candidate_update.email != candidate.email:
        existing = db.query(Candidate).filter(
            Candidate.email == candidate_update.email,
            Candidate.id != candidate_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists for another candidate"
            )
    
    # Update fields
    update_data = candidate_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(candidate, field, value)
    
    db.commit()
    db.refresh(candidate)
    
    return candidate


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete candidate"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Check if candidate has interviews
    if candidate.interviews:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete candidate with existing interviews"
        )
    
    db.delete(candidate)
    db.commit()
    
    return {"message": "Candidate deleted successfully"}


@router.post("/{candidate_id}/upload-resume")
async def upload_resume(
    candidate_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload and parse resume file"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Validate file type
    allowed_types = ["application/pdf", "text/plain", "application/msword"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF, TXT, and DOC files are allowed"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # For now, just store as text (in production, you'd use a document parser)
        if file.content_type == "text/plain":
            resume_text = content.decode('utf-8')
        else:
            # For PDF/DOC files, you would use libraries like PyPDF2, python-docx, etc.
            resume_text = f"Resume file uploaded: {file.filename} ({len(content)} bytes)"
        
        # Update candidate with resume text
        candidate.resume_text = resume_text
        db.commit()
        
        return {
            "message": "Resume uploaded successfully",
            "filename": file.filename,
            "size_bytes": len(content),
            "content_type": file.content_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume file: {str(e)}"
        )


@router.get("/{candidate_id}/interviews")
async def get_candidate_interviews(
    candidate_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all interviews for a candidate"""
    
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    interviews = []
    for interview in candidate.interviews:
        interviews.append({
            "id": interview.id,
            "position": interview.position,
            "status": interview.status,
            "scheduled_at": interview.scheduled_at,
            "started_at": interview.started_at,
            "ended_at": interview.ended_at,
            "total_score": interview.total_score,
            "recommendation": interview.recommendation
        })
    
    return {
        "candidate_id": candidate_id,
        "candidate_name": f"{candidate.first_name} {candidate.last_name}",
        "interviews": interviews,
        "total_interviews": len(interviews)
    }


@router.get("/stats/overview")
async def get_candidate_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get candidate statistics"""
    
    from sqlalchemy import func
    
    # Total candidates
    total_candidates = db.query(Candidate).count()
    
    # Candidates by status
    status_counts = db.query(
        Candidate.status,
        func.count(Candidate.id).label('count')
    ).group_by(Candidate.status).all()
    
    status_distribution = {status: count for status, count in status_counts}
    
    # Candidates by applied position
    position_counts = db.query(
        Candidate.applied_position,
        func.count(Candidate.id).label('count')
    ).filter(
        Candidate.applied_position.isnot(None)
    ).group_by(Candidate.applied_position).limit(10).all()
    
    top_positions = [{"position": pos, "count": count} for pos, count in position_counts]
    
    return {
        "total_candidates": total_candidates,
        "status_distribution": status_distribution,
        "top_applied_positions": top_positions,
        "candidates_with_interviews": db.query(Candidate).join(Candidate.interviews).distinct().count()
    }