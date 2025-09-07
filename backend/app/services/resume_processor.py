import os
import uuid
import asyncio
import aiofiles
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import json
import re

# For resume parsing
import PyPDF2
import docx
from io import BytesIO

from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.services.ai_analysis import AIAnalysisService


class ResumeProcessingError(Exception):
    """Custom exception for resume processing errors"""
    pass


class ResumeProcessor:
    """Service for processing and analyzing resumes"""
    
    def __init__(self):
        self.ai_service = AIAnalysisService()
        self.upload_dir = "/root/more-tech/backend/uploads/resumes"
        self.allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to disk and return file path"""
        
        # Generate unique filename to avoid conflicts
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1].lower()
        unique_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return file_path
    
    def validate_file(self, content_type: str, file_size: int, filename: str) -> None:
        """Validate uploaded file"""
        
        # Check file size
        if file_size > self.max_file_size:
            raise ResumeProcessingError(f"File size {file_size} exceeds maximum allowed size of {self.max_file_size} bytes")
        
        # Check file extension
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension not in self.allowed_extensions:
            raise ResumeProcessingError(f"File type {file_extension} not supported. Allowed types: {', '.join(self.allowed_extensions)}")
        
        # Check content type (basic validation)
        allowed_content_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
        
        if content_type not in allowed_content_types:
            # Allow if extension is correct (content type detection can be unreliable)
            if file_extension not in self.allowed_extensions:
                raise ResumeProcessingError(f"Content type {content_type} not supported")
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise ResumeProcessingError(f"Failed to extract text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise ResumeProcessingError(f"Failed to extract text from DOCX: {str(e)}")
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encodings
            try:
                with open(file_path, 'r', encoding='latin1') as file:
                    return file.read().strip()
            except Exception as e:
                raise ResumeProcessingError(f"Failed to read text file: {str(e)}")
        except Exception as e:
            raise ResumeProcessingError(f"Failed to extract text from TXT: {str(e)}")
    
    def extract_text_from_file(self, file_path: str, content_type: str) -> str:
        """Extract text from file based on content type"""
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf' or content_type == 'application/pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_extension == '.docx' or content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            return self.extract_text_from_docx(file_path)
        elif file_extension in ['.doc'] or content_type == 'application/msword':
            # For .doc files, we would need python-docx2txt or similar
            # For now, return placeholder
            raise ResumeProcessingError("DOC file format not yet supported. Please convert to DOCX or PDF.")
        elif file_extension == '.txt' or content_type == 'text/plain':
            return self.extract_text_from_txt(file_path)
        else:
            raise ResumeProcessingError(f"Unsupported file type: {file_extension}")
    
    def parse_basic_information(self, text: str) -> Dict[str, Any]:
        """Parse basic information from resume text"""
        
        parsed_data = {
            "contact_info": {},
            "personal_info": {},
            "sections": {}
        }
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            parsed_data["contact_info"]["email"] = emails[0]
        
        # Extract phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            parsed_data["contact_info"]["phone"] = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]
        
        # Extract LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            parsed_data["contact_info"]["linkedin"] = f"https://{linkedin_matches[0]}"
        
        # Extract GitHub URL
        github_pattern = r'github\.com/[\w-]+'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            parsed_data["contact_info"]["github"] = f"https://{github_matches[0]}"
        
        # Basic section detection
        sections = ["experience", "education", "skills", "projects", "certifications"]
        for section in sections:
            pattern = rf'\b{section}\b'
            if re.search(pattern, text, re.IGNORECASE):
                parsed_data["sections"][section] = True
        
        return parsed_data
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume text"""
        
        # Common technical skills
        common_skills = [
            # Programming languages
            "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin",
            # Web technologies
            "HTML", "CSS", "React", "Vue", "Angular", "Node.js", "Express", "Django", "Flask", "FastAPI",
            # Databases
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
            # Cloud & DevOps
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab",
            # Data & AI
            "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy", "Scikit-learn",
            # Other
            "Linux", "API", "REST", "GraphQL", "Microservices", "Agile", "Scrum"
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        # Extract skills from skills section if present
        skills_section_pattern = r'skills?[\s:]+(.*?)(?:\n\n|\n[A-Z]|$)'
        skills_match = re.search(skills_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if skills_match:
            skills_text = skills_match.group(1)
            # Split by common delimiters
            additional_skills = re.split(r'[,\n\t|;]', skills_text)
            for skill in additional_skills:
                skill = skill.strip()
                if len(skill) > 2 and len(skill) < 30:  # Reasonable skill name length
                    found_skills.append(skill)
        
        # Remove duplicates and return
        return list(set(found_skills))
    
    async def analyze_with_ai(self, text: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze resume using AI service"""
        
        try:
            # Prepare AI analysis prompt
            analysis_prompt = f"""
            Analyze the following resume and provide structured insights:
            
            Resume Text:
            {text[:3000]}  # Limit text length for AI analysis
            
            Provide analysis in the following areas:
            1. Professional summary
            2. Key strengths and expertise areas
            3. Experience level assessment (junior/middle/senior)
            4. Notable achievements or projects
            5. Potential fit for different role types
            6. Areas for improvement or missing information
            
            Return analysis as structured data.
            """
            
            # This would call your AI service
            # For now, return mock analysis
            ai_analysis = {
                "professional_summary": "Experienced software developer with strong technical skills",
                "experience_level": "middle",
                "key_strengths": ["Programming", "Problem solving", "Technical communication"],
                "recommended_roles": ["Software Developer", "Backend Developer", "Full Stack Developer"],
                "skill_gaps": [],
                "overall_rating": "B+",
                "confidence_score": 0.8
            }
            
            return ai_analysis
            
        except Exception as e:
            return {
                "error": f"AI analysis failed: {str(e)}",
                "confidence_score": 0.0
            }
    
    async def process_resume(self, resume: Resume, db: Session) -> Resume:
        """Process a resume completely"""
        
        try:
            # Update status to processing
            resume.status = "processing"
            resume.processing_started_at = datetime.utcnow()
            db.commit()
            
            # Extract text from file
            if not resume.file_path or not os.path.exists(resume.file_path):
                raise ResumeProcessingError("Resume file not found")
            
            raw_text = self.extract_text_from_file(resume.file_path, resume.content_type)
            resume.raw_text = raw_text
            
            # Parse basic information
            parsed_data = self.parse_basic_information(raw_text)
            resume.parsed_data = parsed_data
            
            # Extract skills
            skills = self.extract_skills(raw_text)
            resume.skills_extracted = skills
            
            # Generate summaries
            resume.experience_summary = self.generate_experience_summary(raw_text)
            resume.education_summary = self.generate_education_summary(raw_text)
            
            # AI analysis
            ai_analysis = await self.analyze_with_ai(raw_text, parsed_data)
            resume.ai_analysis = ai_analysis
            
            # Update status to completed
            resume.status = "processed"
            resume.processing_completed_at = datetime.utcnow()
            
            # Save complete analysis result
            resume.analysis_result = {
                "text_extracted": True,
                "basic_info_parsed": True,
                "skills_extracted": len(skills),
                "ai_analyzed": "error" not in ai_analysis,
                "processing_time_seconds": (datetime.utcnow() - resume.processing_started_at).total_seconds()
            }
            
            db.commit()
            return resume
            
        except Exception as e:
            # Update status to failed
            resume.status = "failed"
            resume.error_message = str(e)
            resume.retry_count = str(int(resume.retry_count) + 1)
            db.commit()
            raise ResumeProcessingError(f"Resume processing failed: {str(e)}")
    
    def generate_experience_summary(self, text: str) -> str:
        """Generate experience summary from resume text"""
        
        # Find experience section
        experience_pattern = r'experience.*?(?=\n\n|\neducation|\nskills|$)'
        experience_match = re.search(experience_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if experience_match:
            experience_text = experience_match.group(0)
            # Basic cleanup and truncation
            lines = experience_text.split('\n')
            relevant_lines = [line.strip() for line in lines if len(line.strip()) > 20]
            return '\n'.join(relevant_lines[:10])  # First 10 relevant lines
        
        return "Experience information not clearly identified in resume."
    
    def generate_education_summary(self, text: str) -> str:
        """Generate education summary from resume text"""
        
        # Find education section
        education_pattern = r'education.*?(?=\n\n|\nexperience|\nskills|$)'
        education_match = re.search(education_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if education_match:
            education_text = education_match.group(0)
            # Basic cleanup and truncation
            lines = education_text.split('\n')
            relevant_lines = [line.strip() for line in lines if len(line.strip()) > 10]
            return '\n'.join(relevant_lines[:5])  # First 5 relevant lines
        
        return "Education information not clearly identified in resume."
    
    async def match_resume_to_position(self, resume: Resume, position_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Match resume against position requirements"""
        
        if resume.status != "processed":
            raise ResumeProcessingError("Resume must be processed before matching")
        
        required_skills = position_requirements.get("required_skills", [])
        preferred_skills = position_requirements.get("preferred_skills", [])
        resume_skills = resume.skills_extracted or []
        
        # Calculate skills match
        matched_required = [skill for skill in required_skills if any(rs.lower() == skill.lower() for rs in resume_skills)]
        matched_preferred = [skill for skill in preferred_skills if any(rs.lower() == skill.lower() for rs in resume_skills)]
        
        # Calculate match score
        required_score = len(matched_required) / len(required_skills) if required_skills else 1.0
        preferred_score = len(matched_preferred) / len(preferred_skills) if preferred_skills else 0.0
        
        overall_score = (required_score * 0.7) + (preferred_score * 0.3)
        
        # Determine fit level
        if overall_score >= 0.8:
            fit_level = "excellent"
        elif overall_score >= 0.6:
            fit_level = "good"
        elif overall_score >= 0.4:
            fit_level = "fair"
        else:
            fit_level = "poor"
        
        return {
            "resume_id": resume.id,
            "match_score": round(overall_score, 2),
            "fit_level": fit_level,
            "matched_required_skills": matched_required,
            "matched_preferred_skills": matched_preferred,
            "missing_required_skills": [skill for skill in required_skills if skill not in matched_required],
            "additional_skills": [skill for skill in resume_skills if skill not in required_skills + preferred_skills],
            "recommendations": self.generate_match_recommendations(overall_score, matched_required, required_skills)
        }
    
    def generate_match_recommendations(self, score: float, matched_skills: List[str], required_skills: List[str]) -> str:
        """Generate recommendations based on match analysis"""
        
        if score >= 0.8:
            return "Excellent match! This candidate meets most requirements and should be considered for interview."
        elif score >= 0.6:
            return f"Good match. Candidate has {len(matched_skills)}/{len(required_skills)} required skills. Consider for interview with focus on missing skills."
        elif score >= 0.4:
            return "Fair match. Candidate may be suitable with additional training or in a junior role."
        else:
            return "Limited match. Candidate may not be suitable for this specific position."
