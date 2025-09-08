from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import asyncio
import os
import aiofiles
import json
import re
from datetime import datetime

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

resume_processor = ResumeProcessor()

def _get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def validate_file(content_type: str, size: int, filename: str):
    """
    Проверка расширения и размера файла на основе настроек resume_processor.
    Генерирует ResumeProcessingError при нарушении правил.
    """
    ext = _get_extension(filename)
    if ext not in resume_processor.allowed_extensions:
        raise ResumeProcessingError(f"Неподдерживаемое расширение файла: {ext}. Допустимые: {resume_processor.allowed_extensions}")
    if size > resume_processor.max_file_size:
        raise ResumeProcessingError(f"Файл слишком большой: {size} байт. Максимум: {resume_processor.max_file_size} байт.")


async def save_uploaded_file(file_content: bytes, filename: str) -> str:
    """
    Сохранение загруженного файла в директорию resume_processor.upload_dir.
    Возвращает путь к сохранённому файлу.
    """
    os.makedirs(resume_processor.upload_dir, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    file_path = os.path.join(resume_processor.upload_dir, unique_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)
    return file_path


async def process_resume_background(resume_id: uuid.UUID, db: Session):
    """
    Фоновая задача для обработки резюме:
      - помечает резюме как processing
      - парсит документ через resume_processor.parse_document
      - вызывает LLM для извлечения структурированных данных (skills, experience_summary, education_summary, experience_level)
      - сохраняет результаты в поля модели резюме
    """
    try:
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            print(f"Резюме {resume_id} не найдено в БД для обработки.")
            return

        # Пометить начало обработки
        resume.status = "processing"
        resume.processing_started_at = datetime.utcnow()
        resume.error_message = None
        db.commit()
        db.refresh(resume)

        # Парсинг документа в сырой текст (parse_document ожидает путь)
        try:
            if not resume.file_path or not os.path.exists(resume.file_path):
                raise ResumeProcessingError("Файл резюме не найден на диске для парсинга.")

            parsed_text = resume_processor.parse_document(resume.file_path)
            resume.raw_text = parsed_text
        except Exception as e:
            resume.status = "failed"
            resume.error_message = f"Не удалось распарсить документ: {str(e)}"
            resume.processing_completed_at = datetime.utcnow()
            db.commit()
            print(f"Парсинг не удался для резюме {resume_id}: {str(e)}")
            return

        # Вызов LLM для извлечения структурированной информации
        try:
            prompt = f"""
            Ты эксперт по анализу резюме. Получи из следующего текста структурированную JSON-информацию.
            Возвращай только валидный JSON, формат:
            {{
              "skills": ["skill1", "skill2", ...],
              "experience_summary": "краткое резюме опыта",
              "education_summary": "краткое резюме образования",
              "experience_level": "junior|middle|senior|unknown"
            }}
            Текст резюме:
            {parsed_text}
            """

            response = await resume_processor.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            ai_text = response.choices[0].message.content

            json_text = None
            m = re.search(r'(\{[\s\S]*\})', ai_text)
            if m:
                json_text = m.group(1)
            else:
                # Если модель вернула иной формат, пробуем весь текст
                json_text = ai_text

            try:
                ai_parsed = json.loads(json_text)
            except Exception:
                ai_parsed = {
                    "skills": [],
                    "experience_summary": None,
                    "education_summary": None,
                    "experience_level": "unknown",
                    "raw": ai_text
                }

            resume.ai_analysis = ai_parsed
            if isinstance(ai_parsed.get("skills"), list):
                resume.skills_extracted = ai_parsed.get("skills")
            resume.experience_summary = ai_parsed.get("experience_summary") if ai_parsed.get("experience_summary") else None
            resume.education_summary = ai_parsed.get("education_summary") if ai_parsed.get("education_summary") else None

            resume.analysis_result = ai_text

        except Exception as e:
            resume.analysis_result = f"Анализ AI не удался: {str(e)}"
            resume.ai_analysis = {"error": str(e)}
            print(f"Анализ AI не удался для резюме {resume_id}: {str(e)}")

        resume.status = "processed"
        resume.processing_completed_at = datetime.utcnow()
        db.commit()
        db.refresh(resume)

    except Exception as e:
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                resume.status = "failed"
                resume.error_message = str(e)
                resume.processing_completed_at = datetime.utcnow()
                db.commit()
        except Exception:
            pass
        print(f"Фоновая обработка не удалась для резюме {resume_id}: {str(e)}")


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    candidate_id: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузить новое резюме для обработки.
    """
    try:
        file_content = await file.read()

        validate_file(file.content_type, len(file_content), file.filename)

        file_path = await save_uploaded_file(file_content, file.filename)

        resume_data = {
            "filename": os.path.basename(file_path),
            "original_filename": file.filename,
            "content_type": file.content_type,
            "file_size": str(len(file_content)),
            "file_path": file_path,
            "candidate_id": candidate_id,
            "uploaded_by_user_id": current_user.id,
            "upload_source": "hr_upload",
            "status": "uploaded",
            "created_at": datetime.utcnow()
        }

        resume = Resume(**resume_data)
        db.add(resume)
        db.commit()
        db.refresh(resume)

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
            detail=f"Не удалось загрузить резюме: {str(e)}"
        )


@router.post("/bulk-upload", response_model=ResumeBulkUploadResponse)
async def bulk_upload_resumes(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузить несколько резюме для пакетной обработки.
    """
    successful_uploads = []
    failed_uploads = []

    for file in files:
        try:
            file_content = await file.read()

            validate_file(file.content_type, len(file_content), file.filename)

            file_path = await save_uploaded_file(file_content, file.filename)

            resume_data = {
                "filename": os.path.basename(file_path),
                "original_filename": file.filename,
                "content_type": file.content_type,
                "file_size": str(len(file_content)),
                "file_path": file_path,
                "uploaded_by_user_id": current_user.id,
                "upload_source": "hr_bulk_upload",
                "status": "uploaded",
                "created_at": datetime.utcnow()
            }

            resume = Resume(**resume_data)
            db.add(resume)
            db.commit()
            db.refresh(resume)

            successful_uploads.append(resume)

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
    status: Optional[str] = Query(None, description="Фильтр по статусу обработки"),
    candidate_id: Optional[uuid.UUID] = Query(None, description="Фильтр по ID кандидата"),
    search: Optional[str] = Query(None, description="Поиск по имени файла или содержимому"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Список резюме с опциональными фильтрами и поиском.
    """
    query = db.query(Resume)

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

    total = query.count()

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
    """
    Получить детали резюме по ID.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Резюме не найдено"
        )

    return resume


@router.get("/{resume_id}/status", response_model=ResumeProcessingStatus)
async def get_resume_status(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получить статус обработки резюме.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Резюме не найдено"
        )

    # Информация о прогрессе
    progress = None
    if resume.status == "processing":
        progress = {
            "stage": "извлечение_текста",
            "estimated_completion": "1-2 минуты"
        }
    elif resume.status == "processed":
        progress = {
            "stage": "завершено",
            "completion_time": resume.processing_completed_at
        }
    elif resume.status == "failed":
        progress = {
            "stage": "ошибка",
            "retry_count": resume.retry_count if hasattr(resume, "retry_count") else None
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
    """
    Получить результаты анализа резюме.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Резюме не найдено"
        )

    if resume.status != "processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Анализ резюме недоступен. Текущий статус: {resume.status}"
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
        match_scores=resume.match_scores if hasattr(resume, "match_scores") else None,
        recommendations=resume.recommendations if hasattr(resume, "recommendations") else None,
        processing_completed_at=resume.processing_completed_at
    )


@router.put("/{resume_id}", response_model=ResumeResponse)
async def update_resume(
    resume_id: uuid.UUID,
    resume_update: ResumeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить данные резюме.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Резюме не найдено"
        )

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
    """
    Перезапустить обработку резюме.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Резюме не найдено"
        )

    if resume.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Резюме в данный момент обрабатывается"
        )

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

    background_tasks.add_task(process_resume_background, resume.id, db)

    return {"message": "Перезапуск обработки резюме запущен", "resume_id": resume_id}


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить резюме (файл + запись в БД).
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Резюме не найдено"
        )

    if resume.file_path and os.path.exists(resume.file_path):
        try:
            os.remove(resume.file_path)
        except Exception as e:
            print(f"Не удалось удалить файл {resume.file_path}: {str(e)}")

    db.delete(resume)
    db.commit()

    return {"message": "Резюме успешно удалено"}


@router.post("/search", response_model=ResumeListResponse)
async def search_resumes(
    search_request: ResumeSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Расширенный поиск резюме по разным критериям.
    """
    query = db.query(Resume).filter(Resume.status == "processed")
    if search_request.query:
        search_filter = f"%{search_request.query}%"
        query = query.filter(
            (Resume.raw_text.ilike(search_filter)) |
            (Resume.experience_summary.ilike(search_filter)) |
            (Resume.education_summary.ilike(search_filter))
        )

    if search_request.skills:
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

    total = query.count()

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
    limit: int = Query(50, ge=1, le=100, description="Максимальное число резюме для анализа"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Сопоставить обработанные резюме с требованиями вакансии.
    Использует resume_processor.match_resume_vacancy_llm (LLM) для оценки соответствия и объяснения.
    """
    resumes = db.query(Resume).filter(Resume.status == "processed").limit(limit).all()

    if not resumes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Обработанные резюме не найдены"
        )

    vacancy_text = matching_request.job_description or matching_request.position_title or ""
    if matching_request.required_skills:
        vacancy_text += "\nТребуемые навыки: " + ", ".join(matching_request.required_skills)
    if matching_request.preferred_skills:
        vacancy_text += "\nЖелаемые навыки: " + ", ".join(matching_request.preferred_skills)

    temp_vacancy_filename = f"{uuid.uuid4().hex}_vacancy.txt"
    temp_vacancy_path = os.path.join(resume_processor.upload_dir, temp_vacancy_filename)
    os.makedirs(resume_processor.upload_dir, exist_ok=True)
    async with aiofiles.open(temp_vacancy_path, "w", encoding="utf-8") as vf:
        await vf.write(vacancy_text)

    matches = []
    for resume in resumes:
        try:
            llm_response_text = await resume_processor.match_resume_vacancy_llm(resume.file_path, temp_vacancy_path)

            score = 0.0
            score_match = re.search(r'([0-9]{1,3})(?:\s*/\s*100|\s*%)?', llm_response_text)
            if score_match:
                try:
                    val = int(score_match.group(1))
                    if 0 <= val <= 100:
                        score = float(val)
                except Exception:
                    score = 0.0

            if score >= 75:
                fit = "high"
            elif score >= 50:
                fit = "medium"
            else:
                fit = "low"

            matches.append(ResumeMatchResult(
                resume_id=resume.id,
                filename=resume.filename,
                candidate_id=resume.candidate_id,
                match_score=score,
                skills_match={
                    "matched_required": [],  # можно дополнить парсингом llm_response_text
                    "matched_preferred": []
                },
                experience_match={
                    "level": resume.ai_analysis.get("experience_level", "unknown") if resume.ai_analysis else "unknown"
                },
                overall_fit=fit,
                recommendations=[],  # можно извлечь из llm_response_text
                missing_skills=[],
                matching_skills=[]
            ))
        except Exception as e:
            print(f"Не удалось сопоставить резюме {resume.id}: {str(e)}")
            continue

    try:
        if os.path.exists(temp_vacancy_path):
            os.remove(temp_vacancy_path)
    except Exception:
        pass

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
    """
    Получить статистику и обзор по резюме.
    """
    from sqlalchemy import func

    total_resumes = db.query(Resume).count()

    status_counts = db.query(
        Resume.status,
        func.count(Resume.id).label('count')
    ).group_by(Resume.status).all()

    status_distribution = {status: count for status, count in status_counts}

    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_uploads = db.query(Resume).filter(Resume.created_at >= week_ago).count()

    processed_resumes = db.query(Resume).filter(Resume.status == "processed").count()
    failed_resumes = db.query(Resume).filter(Resume.status == "failed").count()

    processed_resumes_with_skills = db.query(Resume).filter(
        Resume.status == "processed",
        Resume.skills_extracted.isnot(None)
    ).all()

    skill_counts = {}
    for resume in processed_resumes_with_skills:
        if resume.skills_extracted:
            for skill in resume.skills_extracted:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1

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
