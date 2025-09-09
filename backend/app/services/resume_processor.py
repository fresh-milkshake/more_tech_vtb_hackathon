import os
import uuid
import asyncio
import aiofiles
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import json
import re

import PyPDF2
import docx
from io import BytesIO

from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.services.ai_analysis import AIAnalysisService

import markitdown
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer, util
from openai import AsyncOpenAI

load_dotenv()


class ResumeProcessingError(Exception):
    """Custom exception for resume processing errors"""
    pass


class ResumeProcessor:
    """Service for processing and analyzing resumes"""
    
    def __init__(self):
        self.upload_dir = "/root/more-tech/backend/uploads/resumes"
        self.allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        os.makedirs(self.upload_dir, exist_ok=True)
        
        self.md_parser = markitdown.MarkItDown()
        self.vector_model = SentenceTransformer('all-MiniLM-L6-v2')

        self.skills_dict = os.getenv("SKILLS_DICT", "").split(",") if os.getenv("SKILLS_DICT") else []
        api_key = os.getenv("OPENAI_API_NIKITA")
        self.client = AsyncOpenAI(api_key=api_key)

    def parse_document(self, path: str) -> str:
        """Парсинг документа в текст через markitdown"""
        output = self.md_parser.convert(path)
        return output.text_content
    
    # В ПРОДЕ БУДЕМ ИСПОЛЬЗОВАТЬ match_resume_vacancy_llm ТАК КАК КАЧЕСТВО ПРИМЕРНО СХОЖЕЕ, НО ЕСТЬ ОБОСНОВАНИЯ, ЧТО ВАЖНО ПО ЗАДАЧЕ
    def match_resume_vacancy(self, resume: str, vacancy: str) -> float:
        """Векторное сравнение резюме и вакансии"""
        resume_embs = self.vector_model.encode(resume, convert_to_tensor=True)
        vacancy_embs = self.vector_model.encode(vacancy, convert_to_tensor=True)
        return round(util.cos_sim(resume_embs, vacancy_embs).item() * 100, 2)
    
    async def match_resume_vacancy_llm(self, resume: str, vacancy: str) -> str:
        parsed_resume = self.parse_document(resume)
        parsed_vacancy = self.parse_document(vacancy)
        
        """Сравнение резюме и вакансии через LLM"""
        prompt = f"""
        Ты HR-специалист. Оцени, насколько данное резюме соответствует вакансии.
        Поставь оценку от 0 до 100 и расскажи подробно, почему именно такую оценку ты поставил.
        Сделай ответ максимально подробным, но без форматирования и перечислений.
        Резюме:
        {parsed_resume}
        Вакансия:
        {parsed_vacancy}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    
    def extract_skills(self, text: str) -> set:
        """Извлечение навыков по словарю"""
        lower_text = text.lower()
        skills = set()
        for skill in self.skills_dict:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', lower_text):
                skills.add(skill)
        return skills
    
    # В ПРОДЕ БУДЕМ ИСПОЛЬЗОВАТЬ match_skills_llm ТАК КАК КАЧЕСТВО ПРИМЕРНО СХОЖЕЕ, НО ЕСТЬ ОБОСНОВАНИЯ, ЧТО ВАЖНО ПО ЗАДАЧЕ
    def match_skills(self, resume: str, vacancy: str) -> Dict[str, Any]:
        """Сравнение навыков резюме и вакансии"""
        resume_skills = self.extract_skills(resume)
        vacancy_skills = self.extract_skills(vacancy)
        inter = resume_skills & vacancy_skills
        cov = len(inter) / len(vacancy_skills) * 100 if vacancy_skills else 0
        return {
            'resume_skills': resume_skills,
            'vacancy_skills': vacancy_skills,
            'match': inter,
            'cov': round(cov, 2)
        }
    
    async def match_skills_llm(self, resume: str, vacancy: str) -> str:
        """Сравнение навыков резюме и вакансии через LLM"""
        parsed_resume = self.parse_document(resume)
        parsed_vacancy = self.parse_document(vacancy)
        
        prompt = f"""
        Выдели из текстов резюме и вакансии список ключевых профессиональных навыков.
        Сравни на сколько совпадают навыки, требуемые для вакансии с навыками в резюме.
        Ответь насколько совпадают навыки от 0 до 100 и скажи каких навыков не хватает, а какие совпадают.
        Ответ сделай подробным, с пунктами, необходимым форматированием.
        Если навыки не совпадают один в один, но их смысл одинаковый, считай, что они совпадают.
        Текст резюме:
        {parsed_resume}
        Текст вакансии:
        {parsed_vacancy}
        """
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
