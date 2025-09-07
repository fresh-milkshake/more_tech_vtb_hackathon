from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.user import User
from app.models.vacancy import Vacancy
from app.schemas.vacancy import (
    VacancyCreate, VacancyUpdate, VacancyResponse, VacancyListResponse,
    DocumentUploadResponse, DocumentProcessingStatus
)

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("/", response_model=VacancyListResponse)
async def get_vacancies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of vacancies for current user"""
    query = db.query(Vacancy).filter(Vacancy.created_by_user_id == current_user.id)
    
    # Apply filters
    if search:
        query = query.filter(
            Vacancy.title.ilike(f"%{search}%") |
            Vacancy.company_name.ilike(f"%{search}%") |
            Vacancy.description.ilike(f"%{search}%")
        )
    
    if is_active is not None:
        query = query.filter(Vacancy.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    vacancies = query.offset(offset).limit(per_page).all()
    
    # Add interview links count
    vacancy_responses = []
    for vacancy in vacancies:
        vacancy_dict = VacancyResponse.from_orm(vacancy).dict()
        vacancy_dict["interview_links_count"] = len(vacancy.interview_links)
        vacancy_responses.append(VacancyResponse(**vacancy_dict))
    
    total_pages = (total + per_page - 1) // per_page
    
    return VacancyListResponse(
        vacancies=vacancy_responses,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.post("/", response_model=VacancyResponse, status_code=status.HTTP_201_CREATED)
async def create_vacancy(
    vacancy_data: VacancyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new vacancy"""
    vacancy = Vacancy(
        **vacancy_data.dict(),
        created_by_user_id=current_user.id
    )
    
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    
    return VacancyResponse.from_orm(vacancy)


@router.get("/{vacancy_id}", response_model=VacancyResponse)
async def get_vacancy(
    vacancy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific vacancy"""
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.created_by_user_id == current_user.id
    ).first()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    vacancy_dict = VacancyResponse.from_orm(vacancy).dict()
    vacancy_dict["interview_links_count"] = len(vacancy.interview_links)
    
    return VacancyResponse(**vacancy_dict)


@router.put("/{vacancy_id}", response_model=VacancyResponse)
async def update_vacancy(
    vacancy_id: int,
    vacancy_update: VacancyUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a vacancy"""
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.created_by_user_id == current_user.id
    ).first()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    # Update fields
    update_data = vacancy_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vacancy, field, value)
    
    db.commit()
    db.refresh(vacancy)
    
    vacancy_dict = VacancyResponse.from_orm(vacancy).dict()
    vacancy_dict["interview_links_count"] = len(vacancy.interview_links)
    
    return VacancyResponse(**vacancy_dict)


@router.delete("/{vacancy_id}")
async def delete_vacancy(
    vacancy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a vacancy"""
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.created_by_user_id == current_user.id
    ).first()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    # Delete associated files if they exist
    if vacancy.original_document_path and os.path.exists(vacancy.original_document_path):
        try:
            os.remove(vacancy.original_document_path)
        except OSError:
            pass  # Ignore file deletion errors
    
    if vacancy.processed_document_path and os.path.exists(vacancy.processed_document_path):
        try:
            os.remove(vacancy.processed_document_path)
        except OSError:
            pass  # Ignore file deletion errors
    
    db.delete(vacancy)
    db.commit()
    
    return {"message": "Vacancy deleted successfully"}


@router.post("/{vacancy_id}/upload-document", response_model=DocumentUploadResponse)
async def upload_vacancy_document(
    vacancy_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a document for vacancy processing"""
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
    
    # Validate file type
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not supported. Allowed: PDF, DOC, DOCX, TXT"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = "uploads/vacancies"
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
    
    # Update vacancy with document path
    vacancy.original_document_path = file_path
    vacancy.document_status = "pending"
    db.commit()
    
    # TODO: Here you would trigger document processing
    # For now, we'll just simulate it
    # In a real implementation, you might:
    # 1. Send to a queue for processing
    # 2. Call an external service
    # 3. Process the document directly
    
    return DocumentUploadResponse(
        message="Document uploaded successfully",
        vacancy_id=vacancy.id,
        document_path=file_path,
        status="pending"
    )


@router.get("/{vacancy_id}/document-status", response_model=DocumentProcessingStatus)
async def get_document_processing_status(
    vacancy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get document processing status"""
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.created_by_user_id == current_user.id
    ).first()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    return DocumentProcessingStatus(
        vacancy_id=vacancy.id,
        status=vacancy.document_status,
        message=f"Document status: {vacancy.document_status}",
        processed_document_path=vacancy.processed_document_path
    )


@router.post("/{vacancy_id}/process-document")
async def process_document(
    vacancy_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger document processing (placeholder)"""
    vacancy = db.query(Vacancy).filter(
        Vacancy.id == vacancy_id,
        Vacancy.created_by_user_id == current_user.id
    ).first()
    
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found"
        )
    
    if not vacancy.original_document_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No document uploaded for this vacancy"
        )
    
    # Update status to processing
    vacancy.document_status = "processing"
    db.commit()
    
    # TODO: Implement actual document processing
    # This is a placeholder - in real implementation you would:
    # 1. Extract text from document
    # 2. Parse job requirements and responsibilities
    # 3. Generate structured data
    # 4. Update vacancy fields
    
    # Simulate processing completion
    vacancy.document_status = "completed"
    vacancy.processed_document_path = vacancy.original_document_path  # Placeholder
    db.commit()
    
    return {
        "message": "Document processing completed",
        "vacancy_id": vacancy.id,
        "status": "completed"
    }
