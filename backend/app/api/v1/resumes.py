from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import asyncio
import os

from app.database import get_db
from app.dependencies import get_current_user
from app.schemas.resume import (
    ResumeCreate, ResumeUpdate, ResumeResponse, ResumeListResponse,
    ResumeProcessingStatus, ResumeAnalysisResponse, ResumeBulkUploadResponse,
    ResumeSearchRequest, ResumeMatchingRequest, ResumeMatchingResponse, ResumeMatchResult
)
from app.models.resume import Resume
from app.models.user import User
from app.services.resume_processor import ResumeProcessor, ResumeProcessingError

router = APIRouter(prefix="/resumes", tags=["resumes"])

# Initialize resume processor
resume_processor = ResumeProcessor()


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    candidate_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a new resume for processing.
    
    The resume will be processed in the background and its status can be checked
    using the /resumes/{resume_id}/status endpoint.
    """
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file
        resume_processor.validate_file(file.content_type, len(file_content), file.filename)
        
        # Save file to disk
        file_path = await resume_processor.save_uploaded_file(file_content, file.filename)
        
        # Create resume record
        resume_data = {
            "filename": os.path.basename(file_path),
            "original_filename": file.filename,
            "content_type": file.content_type,
            "file_size": str(len(file_content)),
            "file_path": file_path,
            "candidate_id": candidate_id,
            "uploaded_by_user_id": current_user.id,
            "upload_source": "hr_upload"
        }
        
        resume = Resume(**resume_data)
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Start background processing
        background_tasks.add_task(process_resume_background, resume.id, db)
        
        return resume
        
    except ResumeProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )


async def process_resume_background(resume_id: uuid.UUID, db: Session):
    """Background task to process resume"""
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            await resume_processor.process_resume(resume, db)
    except Exception as e:
        # Log error but don't raise - this is a background task
        print(f"Background processing failed for resume {resume_id}: {str(e)}")


@router.post("/bulk-upload", response_model=ResumeBulkUploadResponse)
async def bulk_upload_resumes(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload multiple resumes for processing.
    
    All resumes will be processed in the background.
    """
    
    successful_uploads = []
    failed_uploads = []
    
    for file in files:
        try:
            # Read file content
            file_content = await file.read()
            
            # Validate file
            resume_processor.validate_file(file.content_type, len(file_content), file.filename)
            
            # Save file to disk
            file_path = await resume_processor.save_uploaded_file(file_content, file.filename)
            
            # Create resume record
            resume_data = {
                "filename": os.path.basename(file_path),
                "original_filename": file.filename,
                "content_type": file.content_type,
                "file_size": str(len(file_content)),
                "file_path": file_path,
                "uploaded_by_user_id": current_user.id,
                "upload_source": "hr_bulk_upload"
            }
            
            resume = Resume(**resume_data)
            db.add(resume)
            db.commit()
            db.refresh(resume)
            
            successful_uploads.append(resume)
            
            # Start background processing
            background_tasks.add_task(process_resume_background, resume.id, db)
            
        except Exception as e:
            failed_uploads.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return ResumeBulkUploadResponse(
        successful_uploads=successful_uploads,
        failed_uploads=failed_uploads,
        total_processed=len(files),
        total_successful=len(successful_uploads),
        total_failed=len(failed_uploads)
    )


@router.get("/", response_model=ResumeListResponse)
async def list_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    candidate_id: Optional[uuid.UUID] = Query(None, description="Filter by candidate ID"),
    search: Optional[str] = Query(None, description="Search in filename or content"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List resumes with optional filtering and search.
    
    Supports filtering by status, candidate ID, and text search.
    """
    
    query = db.query(Resume)
    
    # Apply filters
    if status:
        query = query.filter(Resume.status == status)
    
    if candidate_id:
        query = query.filter(Resume.candidate_id == candidate_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            (Resume.filename.ilike(search_filter)) |
            (Resume.original_filename.ilike(search_filter)) |
            (Resume.raw_text.ilike(search_filter))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order by creation date (newest first)
    resumes = query.order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()
    
    return ResumeListResponse(
        resumes=resumes,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get resume details by ID"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume


@router.get("/{resume_id}/status", response_model=ResumeProcessingStatus)
async def get_resume_status(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get resume processing status"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Calculate progress information
    progress = None
    if resume.status == "processing":
        progress = {
            "stage": "extracting_text",
            "estimated_completion": "1-2 minutes"
        }
    elif resume.status == "processed":
        progress = {
            "stage": "completed",
            "completion_time": resume.processing_completed_at
        }
    elif resume.status == "failed":
        progress = {
            "stage": "failed",
            "retry_count": resume.retry_count
        }
    
    return ResumeProcessingStatus(
        id=resume.id,
        filename=resume.filename,
        status=resume.status,
        processing_started_at=resume.processing_started_at,
        processing_completed_at=resume.processing_completed_at,
        error_message=resume.error_message,
        progress=progress
    )


@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get resume analysis results"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.status != "processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resume analysis not available. Current status: {resume.status}"
        )
    
    return ResumeAnalysisResponse(
        id=resume.id,
        filename=resume.filename,
        status=resume.status,
        analysis_result=resume.analysis_result,
        parsed_data=resume.parsed_data,
        skills_extracted=resume.skills_extracted,
        experience_summary=resume.experience_summary,
        education_summary=resume.education_summary,
        ai_analysis=resume.ai_analysis,
        match_scores=resume.match_scores,
        recommendations=resume.recommendations,
        processing_completed_at=resume.processing_completed_at
    )


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: uuid.UUID,
    resume_update: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update resume information"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Update fields
    update_data = resume_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resume, field, value)
    
    db.commit()
    db.refresh(resume)
    
    return resume


@router.post("/{resume_id}/reprocess")
async def reprocess_resume(
    resume_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reprocess a resume"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    if resume.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resume is currently being processed"
        )
    
    # Reset processing fields
    resume.status = "uploaded"
    resume.processing_started_at = None
    resume.processing_completed_at = None
    resume.error_message = None
    resume.raw_text = None
    resume.analysis_result = None
    resume.parsed_data = None
    resume.skills_extracted = None
    resume.ai_analysis = None
    
    db.commit()
    
    # Start background processing
    background_tasks.add_task(process_resume_background, resume.id, db)
    
    return {"message": "Resume reprocessing started", "resume_id": resume_id}


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a resume"""
    
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file from disk
    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            # Log but don't fail - database record is more important
            print(f"Failed to delete file {resume.file_path}: {str(e)}")
    
    # Delete database record
    db.delete(resume)
    db.commit()
    
    return {"message": "Resume deleted successfully"}


@router.post("/search", response_model=ResumeListResponse)
async def search_resumes(
    search_request: ResumeSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Advanced search for resumes based on various criteria.
    
    Supports searching by skills, experience, position, and other criteria.
    """
    
    query = db.query(Resume).filter(Resume.status == "processed")
    
    # Apply search filters
    if search_request.query:
        search_filter = f"%{search_request.query}%"
        query = query.filter(
            (Resume.raw_text.ilike(search_filter)) |
            (Resume.experience_summary.ilike(search_filter)) |
            (Resume.education_summary.ilike(search_filter))
        )
    
    if search_request.skills:
        # Search for resumes containing any of the specified skills
        for skill in search_request.skills:
            skill_filter = f"%{skill}%"
            query = query.filter(Resume.raw_text.ilike(skill_filter))
    
    if search_request.position:
        position_filter = f"%{search_request.position}%"
        query = query.filter(Resume.raw_text.ilike(position_filter))
    
    if search_request.status:
        query = query.filter(Resume.status == search_request.status)
    
    if search_request.candidate_id:
        query = query.filter(Resume.candidate_id == search_request.candidate_id)
    
    if search_request.uploaded_after:
        query = query.filter(Resume.created_at >= search_request.uploaded_after)
    
    if search_request.uploaded_before:
        query = query.filter(Resume.created_at <= search_request.uploaded_before)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and order by relevance (for now, by creation date)
    resumes = query.order_by(Resume.created_at.desc()).offset(skip).limit(limit).all()
    
    return ResumeListResponse(
        resumes=resumes,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.post("/match-position", response_model=ResumeMatchingResponse)
async def match_resumes_to_position(
    matching_request: ResumeMatchingRequest,
    limit: int = Query(50, ge=1, le=100, description="Maximum number of resumes to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Match processed resumes against position requirements.
    
    Returns resumes ranked by how well they match the position requirements.
    """
    
    # Get processed resumes
    resumes = db.query(Resume).filter(Resume.status == "processed").limit(limit).all()
    
    if not resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No processed resumes found"
        )
    
    # Convert matching request to requirements dict
    position_requirements = {
        "required_skills": matching_request.required_skills,
        "preferred_skills": matching_request.preferred_skills,
        "experience_level": matching_request.experience_level,
        "min_experience_years": matching_request.min_experience_years,
        "job_description": matching_request.job_description
    }
    
    # Match each resume
    matches = []
    for resume in resumes:
        try:
            match_result = await resume_processor.match_resume_to_position(resume, position_requirements)
            
            matches.append(ResumeMatchResult(
                resume_id=match_result["resume_id"],
                filename=resume.filename,
                candidate_id=resume.candidate_id,
                match_score=match_result["match_score"],
                skills_match={
                    "matched_required": match_result["matched_required_skills"],
                    "matched_preferred": match_result["matched_preferred_skills"],
                },
                experience_match={
                    "level": resume.ai_analysis.get("experience_level", "unknown") if resume.ai_analysis else "unknown"
                },
                overall_fit=match_result["fit_level"],
                recommendations=match_result["recommendations"],
                missing_skills=match_result["missing_required_skills"],
                matching_skills=match_result["matched_required_skills"] + match_result["matched_preferred_skills"]
            ))
        except Exception as e:
            # Skip resumes that fail to match
            print(f"Failed to match resume {resume.id}: {str(e)}")
            continue
    
    # Sort matches by score (highest first)
    matches.sort(key=lambda x: x.match_score, reverse=True)
    
    return ResumeMatchingResponse(
        position_title=matching_request.position_title,
        total_resumes_analyzed=len(resumes),
        matches=matches,
        search_criteria={
            "required_skills": matching_request.required_skills,
            "preferred_skills": matching_request.preferred_skills,
            "experience_level": matching_request.experience_level,
            "min_experience_years": matching_request.min_experience_years
        }
    )


@router.get("/stats/overview")
async def get_resume_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get resume statistics and overview"""
    
    from sqlalchemy import func
    
    # Total resumes
    total_resumes = db.query(Resume).count()
    
    # Resumes by status
    status_counts = db.query(
        Resume.status,
        func.count(Resume.id).label('count')
    ).group_by(Resume.status).all()
    
    status_distribution = {status: count for status, count in status_counts}
    
    # Recent uploads (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_uploads = db.query(Resume).filter(Resume.created_at >= week_ago).count()
    
    # Processing statistics
    processed_resumes = db.query(Resume).filter(Resume.status == "processed").count()
    failed_resumes = db.query(Resume).filter(Resume.status == "failed").count()
    
    # Most common skills (from processed resumes)
    processed_resumes_with_skills = db.query(Resume).filter(
        Resume.status == "processed",
        Resume.skills_extracted.isnot(None)
    ).all()
    
    skill_counts = {}
    for resume in processed_resumes_with_skills:
        if resume.skills_extracted:
            for skill in resume.skills_extracted:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
    
    # Top 10 skills
    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_resumes": total_resumes,
        "status_distribution": status_distribution,
        "recent_uploads_7_days": recent_uploads,
        "processing_success_rate": round(processed_resumes / total_resumes * 100, 1) if total_resumes > 0 else 0,
        "failed_processing_count": failed_resumes,
        "top_skills": [{"skill": skill, "count": count} for skill, count in top_skills],
        "resumes_with_candidates": db.query(Resume).filter(Resume.candidate_id.isnot(None)).count()
    }
