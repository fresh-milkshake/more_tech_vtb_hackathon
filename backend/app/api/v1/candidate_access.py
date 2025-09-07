from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models.interview_link import InterviewLink
from app.models.vacancy import Vacancy
from app.schemas.interview_link import (
    InterviewLinkPublic, CandidateAccessRequest, CandidateSessionResponse
)

router = APIRouter(prefix="/candidate", tags=["candidate-access"])


def get_interview_link_by_token(token: str, db: Session) -> Optional[InterviewLink]:
    """Get interview link by token"""
    return db.query(InterviewLink).filter(InterviewLink.unique_token == token).first()


def validate_interview_link(link: InterviewLink) -> bool:
    """Validate if interview link is still valid"""
    if not link.is_active:
        return False
    
    if link.is_used:
        return False
    
    if datetime.utcnow() > link.expires_at:
        return False
    
    return True


@router.get("/access/{token}", response_model=InterviewLinkPublic)
async def get_candidate_access_info(
    token: str,
    db: Session = Depends(get_db)
):
    """Get candidate access information by token"""
    link = get_interview_link_by_token(token, db)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview link not found"
        )
    
    # Check if link is valid
    is_expired = datetime.utcnow() > link.expires_at
    is_valid = link.is_active and not link.is_used and not is_expired
    
    # Get vacancy information
    vacancy = db.query(Vacancy).filter(Vacancy.id == link.vacancy_id).first()
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vacancy not found"
        )
    
    return InterviewLinkPublic(
        unique_token=link.unique_token,
        vacancy_title=vacancy.title,
        company_name=vacancy.company_name,
        expires_at=link.expires_at,
        is_used=link.is_used
    )


@router.post("/access/{token}/register", response_model=CandidateSessionResponse)
async def register_candidate_access(
    token: str,
    candidate_data: CandidateAccessRequest,
    db: Session = Depends(get_db)
):
    """Register candidate access and create session"""
    link = get_interview_link_by_token(token, db)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview link not found"
        )
    
    # Validate link
    if not validate_interview_link(link):
        if not link.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview link is inactive"
            )
        elif link.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview link has already been used"
            )
        elif datetime.utcnow() > link.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Interview link has expired"
            )
    
    # Update candidate information
    link.candidate_name = candidate_data.candidate_name
    link.candidate_email = candidate_data.candidate_email
    link.candidate_phone = candidate_data.candidate_phone
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    link.interview_session_id = session_id
    link.interview_started_at = datetime.utcnow()
    
    # Mark as used
    link.is_used = True
    
    db.commit()
    
    # Get vacancy information
    vacancy = db.query(Vacancy).filter(Vacancy.id == link.vacancy_id).first()
    
    return CandidateSessionResponse(
        session_id=session_id,
        vacancy_title=vacancy.title,
        company_name=vacancy.company_name,
        interview_link_id=link.id,
        expires_at=link.expires_at,
        is_expired=False
    )


@router.post("/access/{token}/upload-resume")
async def upload_candidate_resume(
    token: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload candidate resume"""
    link = get_interview_link_by_token(token, db)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview link not found"
        )
    
    # Validate link
    if not validate_interview_link(link):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Interview link is not valid"
        )
    
    # Validate file type
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported. Allowed: PDF, DOC, DOCX, TXT"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = "uploads/candidates"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file"
        )
    
    # Update link with resume path
    link.candidate_resume_path = file_path
    db.commit()
    
    return {
        "message": "Resume uploaded successfully",
        "file_path": file_path
    }


@router.get("/session/{session_id}/status")
async def get_session_status(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get candidate session status"""
    link = db.query(InterviewLink).filter(
        InterviewLink.interview_session_id == session_id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if session is still valid
    is_expired = datetime.utcnow() > link.expires_at
    
    return {
        "session_id": session_id,
        "is_active": link.is_active and not is_expired,
        "is_expired": is_expired,
        "interview_started_at": link.interview_started_at,
        "interview_completed_at": link.interview_completed_at,
        "candidate_name": link.candidate_name,
        "candidate_email": link.candidate_email,
        "expires_at": link.expires_at
    }


@router.post("/session/{session_id}/complete")
async def complete_interview_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Mark interview session as completed"""
    link = db.query(InterviewLink).filter(
        InterviewLink.interview_session_id == session_id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if session is still valid
    if datetime.utcnow() > link.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session has expired"
        )
    
    # Mark as completed
    link.interview_completed_at = datetime.utcnow()
    db.commit()
    
    return {
        "message": "Interview session completed successfully",
        "completed_at": link.interview_completed_at
    }


@router.get("/session/{session_id}/vacancy-info")
async def get_vacancy_info_for_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get vacancy information for candidate session"""
    link = db.query(InterviewLink).filter(
        InterviewLink.interview_session_id == session_id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get vacancy information
    vacancy = db.query(Vacancy).filter(Vacancy.id == link.vacancy_id).first()
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated vacancy not found"
        )
    
    return {
        "vacancy_id": vacancy.id,
        "title": vacancy.title,
        "description": vacancy.description,
        "requirements": vacancy.requirements,
        "responsibilities": vacancy.responsibilities,
        "company_name": vacancy.company_name,
        "location": vacancy.location,
        "employment_type": vacancy.employment_type,
        "experience_level": vacancy.experience_level
    }
