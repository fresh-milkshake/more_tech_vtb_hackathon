from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import secrets
import string
from datetime import datetime, timedelta

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.models.vacancy import Vacancy
from app.models.interview_link import InterviewLink
from app.schemas.interview_link import (
    InterviewLinkCreate, InterviewLinkUpdate, InterviewLinkResponse,
    InterviewLinkListResponse, InterviewLinkStats
)

router = APIRouter(prefix="/interview-links", tags=["interview-links"])


def generate_unique_token() -> str:
    """Generate a unique token for interview link"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


@router.get("/", response_model=InterviewLinkListResponse)
async def get_interview_links(
    vacancy_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of interview links for current user"""
    query = db.query(InterviewLink).filter(InterviewLink.created_by_user_id == current_user.id)
    
    # Filter by vacancy if specified
    if vacancy_id:
        query = query.filter(InterviewLink.vacancy_id == vacancy_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    links = query.offset(offset).limit(per_page).all()
    
    total_pages = (total + per_page - 1) // per_page
    
    return InterviewLinkListResponse(
        links=[InterviewLinkResponse.from_orm(link) for link in links],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/", response_model=InterviewLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_interview_link(
    vacancy_id: int,
    link_data: InterviewLinkCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new interview link for a vacancy"""
    # Check if vacancy exists and belongs to user
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.created_by_user_id == current_user.id
    ).first()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    # Generate unique token
    unique_token = generate_unique_token()
    
    # Check if token is unique (very unlikely collision, but just in case)
    while db.query(InterviewLink).filter(InterviewLink.unique_token == unique_token).first():
        unique_token = generate_unique_token()
    
    # Calculate expiration time
    expires_at = datetime.utcnow() + timedelta(hours=link_data.expires_hours)
    
    # Create interview link
    interview_link = InterviewLink(
        unique_token=unique_token,
        candidate_name=link_data.candidate_name,
        candidate_email=link_data.candidate_email,
        candidate_phone=link_data.candidate_phone,
        candidate_notes=link_data.candidate_notes,
        expires_at=expires_at,
        vacancy_id=vacancy_id,
        created_by_user_id=current_user.id
    )
    
    db.add(interview_link)
    db.commit()
    db.refresh(interview_link)
    
    return InterviewLinkResponse.from_orm(interview_link)


@router.get("/{link_id}", response_model=InterviewLinkResponse)
async def get_interview_link(
    link_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific interview link"""
    link = db.query(InterviewLink).filter(
        InterviewLink.id == link_id,
        InterviewLink.created_by_user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview link not found"
        )
    
    return InterviewLinkResponse.from_orm(link)


@router.put("/{link_id}", response_model=InterviewLinkResponse)
async def update_interview_link(
    link_id: int,
    link_update: InterviewLinkUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an interview link"""
    link = db.query(InterviewLink).filter(
        InterviewLink.id == link_id,
        InterviewLink.created_by_user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview link not found"
        )
    
    # Don't allow updates if link is already used
    if link.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update used interview link"
        )
    
    # Update fields
    update_data = link_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(link, field, value)
    
    db.commit()
    db.refresh(link)
    
    return InterviewLinkResponse.from_orm(link)


@router.delete("/{link_id}")
async def delete_interview_link(
    link_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an interview link"""
    link = db.query(InterviewLink).filter(
        InterviewLink.id == link_id,
        InterviewLink.created_by_user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview link not found"
        )
    
    # Don't allow deletion if link is already used
    if link.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete used interview link"
        )
    
    db.delete(link)
    db.commit()
    
    return {"message": "Interview link deleted successfully"}


@router.get("/{link_id}/stats", response_model=InterviewLinkStats)
async def get_interview_link_stats(
    link_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a specific interview link"""
    link = db.query(InterviewLink).filter(
        InterviewLink.id == link_id,
        InterviewLink.created_by_user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview link not found"
        )
    
    # For a single link, stats are simple
    is_expired = datetime.utcnow() > link.expires_at
    
    return InterviewLinkStats(
        total_links=1,
        active_links=1 if link.is_active and not is_expired else 0,
        used_links=1 if link.is_used else 0,
        expired_links=1 if is_expired else 0,
        links_by_status={
            "active": 1 if link.is_active and not is_expired else 0,
            "used": 1 if link.is_used else 0,
            "expired": 1 if is_expired else 0,
            "inactive": 1 if not link.is_active else 0
        }
    )


@router.get("/vacancy/{vacancy_id}/stats", response_model=InterviewLinkStats)
async def get_vacancy_interview_links_stats(
    vacancy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get statistics for all interview links of a vacancy"""
    # Check if vacancy exists and belongs to user
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.created_by_user_id == current_user.id
    ).first()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    # Get all links for this vacancy
    links = db.query(InterviewLink).filter(InterviewLink.vacancy_id == vacancy_id).all()
    
    now = datetime.utcnow()
    total_links = len(links)
    active_links = 0
    used_links = 0
    expired_links = 0
    links_by_status = {
        "active": 0,
        "used": 0,
        "expired": 0,
        "inactive": 0
    }
    
    for link in links:
        is_expired = now > link.expires_at
        
        if link.is_used:
            used_links += 1
            links_by_status["used"] += 1
        elif is_expired:
            expired_links += 1
            links_by_status["expired"] += 1
        elif link.is_active:
            active_links += 1
            links_by_status["active"] += 1
        else:
            links_by_status["inactive"] += 1
    
    return InterviewLinkStats(
        total_links=total_links,
        active_links=active_links,
        used_links=used_links,
        expired_links=expired_links,
        links_by_status=links_by_status
    )


@router.post("/{link_id}/regenerate")
async def regenerate_interview_link(
    link_id: int,
    expires_hours: int = Query(6, ge=1, le=168),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Regenerate an interview link (create new token and expiration)"""
    link = db.query(InterviewLink).filter(
        InterviewLink.id == link_id,
        InterviewLink.created_by_user_id == current_user.id
    ).first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview link not found"
        )
    
    # Don't allow regeneration if link is already used
    if link.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot regenerate used interview link"
        )
    
    # Generate new token
    new_token = generate_unique_token()
    while db.query(InterviewLink).filter(InterviewLink.unique_token == new_token).first():
        new_token = generate_unique_token()
    
    # Update token and expiration
    link.unique_token = new_token
    link.expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
    link.is_used = False  # Reset usage status
    
    db.commit()
    db.refresh(link)
    
    return {
        "message": "Interview link regenerated successfully",
        "new_token": new_token,
        "expires_at": link.expires_at
    }
