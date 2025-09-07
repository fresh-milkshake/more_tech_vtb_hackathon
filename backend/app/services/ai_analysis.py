import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.config import settings

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """AI service for response analysis and question generation using OpenAI GPT"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-4o-mini"
        self.max_retries = 3
        
        if OPENAI_AVAILABLE and settings.OPENAI_API_KEY:
            try:
                self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        else:
            logger.warning("OpenAI not available or API key not set")
    
    async def analyze_response(
        self,
        question: str,
        response: str,
        context: Dict[str, Any],
        job_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze candidate response and provide scoring"""
        
        if not self.client:
            return await self._mock_analysis(question, response)
        
        try:
            prompt = self._build_analysis_prompt(question, response, context, job_requirements)
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_analysis_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"},
                max_tokens=1500
            )
            
            analysis = json.loads(completion.choices[0].message.content)
            
            # Validate and normalize the analysis
            return self._normalize_analysis(analysis)
            
        except Exception as e:
            logger.error(f"Error during AI analysis: {str(e)}")
            return await self._mock_analysis(question, response, error=str(e))
    
    async def generate_question(
        self,
        context: Dict[str, Any],
        timeline: List[Dict[str, Any]],
        job_requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate next interview question based on context"""
        
        if not self.client:
            return await self._mock_question_generation(context)
        
        try:
            prompt = self._build_question_prompt(context, timeline, job_requirements)
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_question_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"},
                max_tokens=800
            )
            
            question_data = json.loads(completion.choices[0].message.content)
            
            # Validate and normalize question data
            return self._normalize_question(question_data, context)
            
        except Exception as e:
            logger.error(f"Error during question generation: {str(e)}")
            return await self._mock_question_generation(context, error=str(e))
    
    async def generate_introduction(self, context: Dict[str, Any]) -> str:
        """Generate AI introduction for interview"""
        
        if not self.client:
            return self._mock_introduction(context)
        
        try:
            position = context.get("position", "Software Developer")
            candidate_name = context.get("candidate_name", "")
            
            prompt = f"""
            Generate a professional and welcoming introduction for an AI-powered interview.
            Position: {position}
            Candidate: {candidate_name}
            
            The introduction should:
            - Be warm and professional
            - Explain that this is an AI-powered interview
            - Set expectations about the process
            - Be concise (30-45 seconds when spoken)
            - Use Russian language
            """
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional HR AI assistant conducting interviews."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating introduction: {str(e)}")
            return self._mock_introduction(context)
    
    async def generate_farewell(self, context: Dict[str, Any]) -> str:
        """Generate farewell message"""
        
        if not self.client:
            return self._mock_farewell(context)
        
        try:
            total_score = context.get("total_score", 0)
            questions_asked = context.get("questions_asked", 0)
            
            prompt = f"""
            Generate a professional farewell message for completing an interview.
            Questions asked: {questions_asked}
            
            The farewell should:
            - Thank the candidate for their time
            - Mention that the interview is complete
            - Be professional and encouraging
            - Indicate next steps will be communicated separately
            - Use Russian language
            - Be concise (20-30 seconds when spoken)
            """
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional HR AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating farewell: {str(e)}")
            return self._mock_farewell(context)
    
    def _get_analysis_system_prompt(self) -> str:
        """System prompt for response analysis"""
        return """
        You are an expert HR interviewer analyzing candidate responses for technical interviews.
        Analyze the response objectively and provide detailed feedback.
        
        Return your analysis in JSON format with this exact structure:
        {
            "score": <float 0-10>,
            "feedback": "<detailed constructive feedback>",
            "strengths": ["<list of identified strengths>"],
            "areas_for_improvement": ["<list of improvement areas>"],
            "technical_accuracy": <float 0-10>,
            "communication_clarity": <float 0-10>,
            "relevance": <float 0-10>,
            "completeness": <float 0-10>,
            "keywords_matched": ["<relevant keywords found>"],
            "sentiment": "<positive|neutral|negative>",
            "confidence_level": "<high|medium|low>",
            "recommendations": ["<specific recommendations>"]
        }
        """
    
    def _get_question_system_prompt(self) -> str:
        """System prompt for question generation"""
        return """
        You are an expert technical interviewer generating the next question for a candidate.
        Consider the interview context, previous responses, and job requirements.
        
        Return your question in JSON format with this exact structure:
        {
            "text": "<the interview question>",
            "category": "<technical|behavioral|cultural|general>",
            "difficulty": <integer 1-5>,
            "expected_duration": <seconds 60-300>,
            "expected_keywords": ["<keywords to look for>"],
            "scoring_rubric": {
                "excellent": "<criteria for 9-10 score>",
                "good": "<criteria for 7-8 score>",
                "average": "<criteria for 5-6 score>",
                "poor": "<criteria for below 5 score>"
            },
            "reasoning": "<why this question was chosen>"
        }
        """
    
    def _build_analysis_prompt(
        self, 
        question: str, 
        response: str, 
        context: Dict[str, Any], 
        job_requirements: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for response analysis"""
        
        position = context.get("position", "Software Developer")
        questions_asked = context.get("questions_asked", 0)
        
        job_req_text = ""
        if job_requirements:
            job_req_text = f"Job Requirements: {json.dumps(job_requirements, indent=2)}"
        
        return f"""
        Analyze this interview response for a {position} position:
        
        QUESTION: {question}
        
        RESPONSE: {response}
        
        CONTEXT:
        - Position: {position}
        - Questions asked so far: {questions_asked}
        - Interview stage: {"Early" if questions_asked < 2 else "Mid" if questions_asked < 4 else "Advanced"}
        
        {job_req_text}
        
        Please provide a comprehensive analysis focusing on:
        1. Technical accuracy and knowledge demonstrated
        2. Communication clarity and structure
        3. Relevance to the question asked
        4. Completeness of the response
        5. Overall impression and recommendations
        
        Be fair but thorough in your evaluation.
        """
    
    def _build_question_prompt(
        self, 
        context: Dict[str, Any], 
        timeline: List[Dict[str, Any]], 
        job_requirements: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for question generation"""
        
        position = context.get("position", "Software Developer")
        questions_asked = context.get("questions_asked", 0)
        
        # Analyze previous questions and responses
        previous_topics = []
        avg_score = 0
        for entry in timeline[-3:]:  # Last 3 entries
            if "question" in entry:
                question_data = entry["question"]
                if question_data:
                    category = question_data.get("category", "unknown")
                    previous_topics.append(category)
            if "score" in entry:
                avg_score += entry["score"]
        
        if previous_topics:
            avg_score = avg_score / len(previous_topics)
        
        job_req_text = ""
        if job_requirements:
            job_req_text = f"Job Requirements: {json.dumps(job_requirements, indent=2)}"
        
        return f"""
        Generate the next interview question for a {position} position.
        
        INTERVIEW CONTEXT:
        - Questions asked: {questions_asked}
        - Previous question categories: {previous_topics}
        - Average score so far: {avg_score:.1f}/10
        - Interview stage: {"Opening" if questions_asked < 2 else "Technical Deep-dive" if questions_asked < 4 else "Advanced/Cultural"}
        
        {job_req_text}
        
        GUIDELINES:
        - Avoid repeating previous question categories if possible
        - Adjust difficulty based on previous performance
        - Ensure the question is appropriate for the interview stage
        - Focus on practical, job-relevant skills
        - Make questions clear and specific
        - Use Russian language for the question text
        
        Generate a question that will effectively assess the candidate's suitability.
        """
    
    def _normalize_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate analysis results"""
        normalized = {
            "score": max(0.0, min(10.0, float(analysis.get("score", 5.0)))),
            "feedback": str(analysis.get("feedback", "No feedback provided")),
            "strengths": list(analysis.get("strengths", [])),
            "areas_for_improvement": list(analysis.get("areas_for_improvement", [])),
            "technical_accuracy": max(0.0, min(10.0, float(analysis.get("technical_accuracy", 5.0)))),
            "communication_clarity": max(0.0, min(10.0, float(analysis.get("communication_clarity", 5.0)))),
            "relevance": max(0.0, min(10.0, float(analysis.get("relevance", 5.0)))),
            "completeness": max(0.0, min(10.0, float(analysis.get("completeness", 5.0)))),
            "keywords_matched": list(analysis.get("keywords_matched", [])),
            "sentiment": analysis.get("sentiment", "neutral"),
            "confidence_level": analysis.get("confidence_level", "medium"),
            "recommendations": list(analysis.get("recommendations", []))
        }
        
        return normalized
    
    def _normalize_question(self, question_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and validate question data"""
        import uuid
        
        normalized = {
            "id": str(uuid.uuid4()),
            "text": str(question_data.get("text", "Can you tell me about your experience?")),
            "category": question_data.get("category", "general"),
            "difficulty": max(1, min(5, int(question_data.get("difficulty", 3)))),
            "expected_duration": max(60, min(300, int(question_data.get("expected_duration", 120)))),
            "expected_keywords": list(question_data.get("expected_keywords", [])),
            "scoring_rubric": dict(question_data.get("scoring_rubric", {})),
            "reasoning": str(question_data.get("reasoning", ""))
        }
        
        return normalized
    
    async def _mock_analysis(self, question: str, response: str, error: str = None) -> Dict[str, Any]:
        """Mock analysis for development"""
        await asyncio.sleep(1)  # Simulate processing time
        
        response_length = len(response.split()) if response else 0
        
        if response_length == 0:
            score = 0.0
            feedback = "No response provided"
        elif response_length < 5:
            score = 3.0
            feedback = "Response too brief, lacks detail"
        elif response_length < 20:
            score = 6.0
            feedback = "Good start, could provide more specific examples"
        else:
            score = 7.5
            feedback = "Good response with relevant details"
        
        return {
            "score": score,
            "feedback": feedback,
            "strengths": ["Clear communication"] if score > 5 else [],
            "areas_for_improvement": ["Provide more specific examples"],
            "technical_accuracy": score,
            "communication_clarity": min(score + 1, 10),
            "relevance": score,
            "completeness": score - 0.5 if score > 0.5 else 0,
            "keywords_matched": ["experience", "development"] if "experience" in response.lower() else [],
            "sentiment": "positive" if score > 6 else "neutral",
            "confidence_level": "high" if score > 7 else "medium",
            "recommendations": ["Continue with technical questions"],
            "mock": True,
            "error": error
        }
    
    async def _mock_question_generation(self, context: Dict[str, Any], error: str = None) -> Dict[str, Any]:
        """Mock question generation"""
        await asyncio.sleep(0.8)  # Simulate processing time
        
        questions_asked = context.get("questions_asked", 0)
        
        questions = [
            "Расскажите о своем опыте программирования",
            "Как вы подходите к решению сложных технических задач?",
            "Опишите проект, которым вы особенно гордитесь",
            "Как вы работаете в команде?",
            "Какие технологии вы изучаете в настоящее время?"
        ]
        
        question_text = questions[questions_asked % len(questions)]
        
        import uuid
        return {
            "id": str(uuid.uuid4()),
            "text": question_text,
            "category": "technical" if questions_asked < 3 else "behavioral",
            "difficulty": min(questions_asked + 2, 5),
            "expected_duration": 120,
            "expected_keywords": ["опыт", "технологии", "проект"],
            "scoring_rubric": {
                "excellent": "Детальный ответ с конкретными примерами",
                "good": "Хороший ответ с некоторыми деталями",
                "average": "Базовый ответ",
                "poor": "Неполный или неточный ответ"
            },
            "reasoning": f"Вопрос {questions_asked + 1} для оценки опыта",
            "mock": True,
            "error": error
        }
    
    def _mock_introduction(self, context: Dict[str, Any]) -> str:
        """Mock introduction"""
        position = context.get("position", "разработчика")
        return f"Добро пожаловать! Меня зовут AI-ассистент, и я проведу с вами собеседование на позицию {position}. Интервью займет примерно 30 минут. Готовы начать?"
    
    def _mock_farewell(self, context: Dict[str, Any]) -> str:
        """Mock farewell"""
        return "Спасибо за ваше время! Собеседование завершено. Результаты будут отправлены в течение нескольких дней. Хорошего дня!"
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None