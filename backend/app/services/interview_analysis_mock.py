import asyncio
import re
import logging
from typing import Dict, Any, List
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class InterviewAnalysisMock:
    """
    Mock service for analyzing candidate responses in real-time
    Provides realistic scoring and feedback for development/testing
    """
    
    def __init__(self):
        # Keywords for different technical areas
        self.technical_keywords = {
            "python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "asyncio"],
            "web": ["html", "css", "javascript", "react", "vue", "angular", "api", "rest"],
            "database": ["sql", "postgresql", "mysql", "mongodb", "redis", "database"],
            "devops": ["docker", "kubernetes", "aws", "git", "ci/cd", "jenkins"],
            "general": ["алгоритм", "структура данных", "oop", "тестирование", "отладка"]
        }
        
        # Positive indicators
        self.positive_indicators = [
            "опыт", "работал", "использовал", "изучал", "применял", "реализовал",
            "проект", "команда", "ответственность", "решение", "задача"
        ]
        
        # Communication quality indicators
        self.communication_indicators = {
            "good": ["например", "то есть", "конкретно", "детально", "подробно"],
            "structure": ["во-первых", "во-вторых", "итак", "таким образом", "следовательно"],
            "confidence": ["уверен", "знаю", "понимаю", "умею", "могу"]
        }
        
        logger.info("Interview analysis mock service initialized")
    
    async def analyze_response(
        self, 
        question: str, 
        response: str, 
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze candidate response and provide detailed scoring
        """
        try:
            # Simulate processing time
            await asyncio.sleep(0.3)
            
            if not response or len(response.strip()) < 3:
                return self._create_empty_response_analysis()
            
            # Basic metrics
            word_count = len(response.split())
            sentence_count = len([s for s in response.split('.') if s.strip()])
            
            # Technical analysis
            technical_score = self._analyze_technical_content(response, question)
            
            # Communication analysis
            communication_score = self._analyze_communication_quality(response)
            
            # Relevance analysis
            relevance_score = self._analyze_relevance(response, question)
            
            # Completeness analysis
            completeness_score = self._analyze_completeness(response, word_count)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                technical_score, communication_score, relevance_score, completeness_score
            )
            
            # Generate feedback
            feedback = self._generate_feedback(
                response, overall_score, technical_score, communication_score
            )
            
            # Identify strengths and improvements
            strengths = self._identify_strengths(response, technical_score, communication_score)
            improvements = self._identify_improvements(
                response, technical_score, communication_score, completeness_score
            )
            
            # Keywords matched
            keywords_matched = self._find_keywords(response)
            
            # Sentiment analysis
            sentiment = self._analyze_sentiment(response)
            
            # Confidence level
            confidence_level = self._assess_confidence(response, overall_score)
            
            return {
                "score": round(overall_score, 1),
                "feedback": feedback,
                "strengths": strengths,
                "areas_for_improvement": improvements,
                "technical_accuracy": round(technical_score, 1),
                "communication_clarity": round(communication_score, 1),
                "relevance": round(relevance_score, 1),
                "completeness": round(completeness_score, 1),
                "keywords_matched": keywords_matched,
                "sentiment": sentiment,
                "confidence_level": confidence_level,
                "recommendations": self._generate_recommendations(overall_score, context),
                "word_count": word_count,
                "sentence_count": sentence_count,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "mock": True
            }
            
        except Exception as e:
            logger.error(f"Error in mock analysis: {str(e)}")
            return self._create_error_analysis(str(e))
    
    def _analyze_technical_content(self, response: str, question: str = "") -> float:
        """Analyze technical content quality"""
        response_lower = response.lower()
        
        # Count technical keywords
        tech_score = 0.0
        total_keywords = 0
        
        for category, keywords in self.technical_keywords.items():
            for keyword in keywords:
                if keyword in response_lower:
                    tech_score += 1.0
                total_keywords += 1
        
        # Normalize score
        if total_keywords > 0:
            base_score = (tech_score / len(self.technical_keywords)) * 10
        else:
            base_score = 5.0
        
        # Bonus for specific technical terms
        if any(term in response_lower for term in ["архитектура", "паттерн", "алгоритм"]):
            base_score += 1.0
        
        # Bonus for concrete examples
        if any(indicator in response_lower for indicator in ["пример", "проект", "использовал"]):
            base_score += 0.5
        
        return min(10.0, max(0.0, base_score))
    
    def _analyze_communication_quality(self, response: str) -> float:
        """Analyze communication clarity and structure"""
        response_lower = response.lower()
        word_count = len(response.split())
        
        base_score = 5.0
        
        # Structure bonus
        structure_words = sum(1 for word in self.communication_indicators["structure"] 
                            if word in response_lower)
        base_score += min(2.0, structure_words * 0.5)
        
        # Examples and details bonus
        good_words = sum(1 for word in self.communication_indicators["good"] 
                        if word in response_lower)
        base_score += min(1.5, good_words * 0.3)
        
        # Confidence bonus
        confidence_words = sum(1 for word in self.communication_indicators["confidence"] 
                             if word in response_lower)
        base_score += min(1.0, confidence_words * 0.2)
        
        # Length penalty/bonus
        if word_count < 10:
            base_score -= 2.0
        elif word_count > 50:
            base_score += 1.0
        
        # Grammar and coherence (simplified check)
        if response.count('.') > 0 and word_count > response.count('.') * 3:
            base_score += 0.5
        
        return min(10.0, max(0.0, base_score))
    
    def _analyze_relevance(self, response: str, question: str = "") -> float:
        """Analyze how relevant the response is to the question"""
        if not question:
            return 7.0  # Default if no question context
        
        response_lower = response.lower()
        question_lower = question.lower()
        
        # Extract key words from question
        question_words = [word for word in question_lower.split() 
                         if len(word) > 3 and word not in ["что", "как", "где", "когда", "почему"]]
        
        if not question_words:
            return 7.0
        
        # Check how many question keywords appear in response
        matches = sum(1 for word in question_words if word in response_lower)
        relevance_ratio = matches / len(question_words)
        
        base_score = 5.0 + (relevance_ratio * 4.0)
        
        # Bonus for direct addressing
        if any(phrase in response_lower for phrase in ["отвечая на вопрос", "по поводу", "касательно"]):
            base_score += 1.0
        
        return min(10.0, max(2.0, base_score))
    
    def _analyze_completeness(self, response: str, word_count: int) -> float:
        """Analyze completeness of the response"""
        base_score = 5.0
        
        # Word count impact
        if word_count < 5:
            base_score = 2.0
        elif word_count < 15:
            base_score = 4.0
        elif word_count < 30:
            base_score = 6.0
        elif word_count < 50:
            base_score = 8.0
        else:
            base_score = 9.0
        
        # Check for examples
        response_lower = response.lower()
        if any(word in response_lower for word in ["например", "пример", "случай", "проект"]):
            base_score += 1.0
        
        # Check for details
        if any(word in response_lower for word in ["детально", "подробно", "конкретно"]):
            base_score += 0.5
        
        return min(10.0, max(0.0, base_score))
    
    def _calculate_overall_score(
        self, 
        technical: float, 
        communication: float, 
        relevance: float, 
        completeness: float
    ) -> float:
        """Calculate weighted overall score"""
        # Weights for different aspects
        weights = {
            "technical": 0.3,
            "communication": 0.25,
            "relevance": 0.25,
            "completeness": 0.2
        }
        
        overall = (
            technical * weights["technical"] +
            communication * weights["communication"] +
            relevance * weights["relevance"] +
            completeness * weights["completeness"]
        )
        
        return min(10.0, max(0.0, overall))
    
    def _generate_feedback(
        self, 
        response: str, 
        overall_score: float, 
        technical_score: float, 
        communication_score: float
    ) -> str:
        """Generate contextual feedback"""
        feedback_parts = []
        
        if overall_score >= 8.0:
            feedback_parts.append("Отличный ответ!")
        elif overall_score >= 6.0:
            feedback_parts.append("Хороший ответ.")
        elif overall_score >= 4.0:
            feedback_parts.append("Неплохо, но есть что улучшить.")
        else:
            feedback_parts.append("Ответ требует доработки.")
        
        if technical_score >= 7.0:
            feedback_parts.append("Демонстрируется хорошее техническое понимание.")
        elif technical_score < 5.0:
            feedback_parts.append("Стоит добавить больше технических деталей.")
        
        if communication_score >= 7.0:
            feedback_parts.append("Четкое и структурированное изложение.")
        elif communication_score < 5.0:
            feedback_parts.append("Можно улучшить структуру ответа.")
        
        word_count = len(response.split())
        if word_count < 10:
            feedback_parts.append("Рекомендуется дать более развернутый ответ.")
        
        return " ".join(feedback_parts)
    
    def _identify_strengths(
        self, 
        response: str, 
        technical_score: float, 
        communication_score: float
    ) -> List[str]:
        """Identify response strengths"""
        strengths = []
        response_lower = response.lower()
        
        if technical_score >= 7.0:
            strengths.append("Демонстрация технических знаний")
        
        if communication_score >= 7.0:
            strengths.append("Четкое изложение мыслей")
        
        if any(word in response_lower for word in ["пример", "проект", "опыт"]):
            strengths.append("Использование конкретных примеров")
        
        if any(word in response_lower for word in self.communication_indicators["structure"]):
            strengths.append("Структурированный подход")
        
        if len(response.split()) > 30:
            strengths.append("Подробное объяснение")
        
        return strengths if strengths else ["Готовность отвечать на вопросы"]
    
    def _identify_improvements(
        self, 
        response: str, 
        technical_score: float, 
        communication_score: float, 
        completeness_score: float
    ) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        response_lower = response.lower()
        word_count = len(response.split())
        
        if technical_score < 6.0:
            improvements.append("Добавить больше технических деталей")
        
        if communication_score < 6.0:
            improvements.append("Улучшить структуру изложения")
        
        if completeness_score < 6.0:
            improvements.append("Дать более полный ответ")
        
        if word_count < 15:
            improvements.append("Предоставить более развернутое объяснение")
        
        if not any(word in response_lower for word in ["пример", "проект", "опыт"]):
            improvements.append("Привести конкретные примеры")
        
        return improvements if improvements else ["Продолжать в том же духе"]
    
    def _find_keywords(self, response: str) -> List[str]:
        """Find technical and relevant keywords in response"""
        response_lower = response.lower()
        found_keywords = []
        
        for category, keywords in self.technical_keywords.items():
            for keyword in keywords:
                if keyword in response_lower:
                    found_keywords.append(keyword)
        
        # Add positive indicators found
        for indicator in self.positive_indicators:
            if indicator in response_lower:
                found_keywords.append(indicator)
        
        return list(set(found_keywords))  # Remove duplicates
    
    def _analyze_sentiment(self, response: str) -> str:
        """Analyze response sentiment"""
        response_lower = response.lower()
        
        positive_words = ["хороший", "отличный", "нравится", "интересно", "успешно", "эффективно"]
        negative_words = ["плохой", "сложно", "проблема", "ошибка", "трудно", "неудачно"]
        
        positive_count = sum(1 for word in positive_words if word in response_lower)
        negative_count = sum(1 for word in negative_words if word in response_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _assess_confidence(self, response: str, overall_score: float) -> str:
        """Assess confidence level based on language used"""
        response_lower = response.lower()
        
        confidence_indicators = sum(1 for word in self.communication_indicators["confidence"] 
                                  if word in response_lower)
        
        uncertainty_words = ["возможно", "наверное", "кажется", "думаю", "полагаю"]
        uncertainty_count = sum(1 for word in uncertainty_words if word in response_lower)
        
        if confidence_indicators > uncertainty_count and overall_score >= 7.0:
            return "high"
        elif uncertainty_count > confidence_indicators or overall_score < 4.0:
            return "low"
        else:
            return "medium"
    
    def _generate_recommendations(self, overall_score: float, context: Dict[str, Any] = None) -> List[str]:
        """Generate follow-up recommendations"""
        recommendations = []
        
        if overall_score >= 8.0:
            recommendations.append("Продолжить с более сложными техническими вопросами")
            recommendations.append("Обсудить опыт работы в команде")
        elif overall_score >= 6.0:
            recommendations.append("Задать уточняющие вопросы по техническим навыкам")
            recommendations.append("Проверить практический опыт")
        elif overall_score >= 4.0:
            recommendations.append("Дать возможность дополнить ответ")
            recommendations.append("Задать более конкретные вопросы")
        else:
            recommendations.append("Перефразировать вопрос")
            recommendations.append("Предложить альтернативную тему")
        
        return recommendations
    
    def _create_empty_response_analysis(self) -> Dict[str, Any]:
        """Create analysis for empty or very short responses"""
        return {
            "score": 0.0,
            "feedback": "Ответ не предоставлен или слишком короткий.",
            "strengths": [],
            "areas_for_improvement": ["Предоставить развернутый ответ"],
            "technical_accuracy": 0.0,
            "communication_clarity": 0.0,
            "relevance": 0.0,
            "completeness": 0.0,
            "keywords_matched": [],
            "sentiment": "neutral",
            "confidence_level": "low",
            "recommendations": ["Повторить вопрос", "Дать время на размышление"],
            "word_count": 0,
            "sentence_count": 0,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "mock": True
        }
    
    def _create_error_analysis(self, error: str) -> Dict[str, Any]:
        """Create analysis for error cases"""
        return {
            "score": 5.0,
            "feedback": "Произошла ошибка при анализе ответа.",
            "strengths": ["Участие в интервью"],
            "areas_for_improvement": ["Техническая проблема анализа"],
            "technical_accuracy": 5.0,
            "communication_clarity": 5.0,
            "relevance": 5.0,
            "completeness": 5.0,
            "keywords_matched": [],
            "sentiment": "neutral",
            "confidence_level": "medium",
            "recommendations": ["Продолжить интервью"],
            "word_count": 0,
            "sentence_count": 0,
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "error": error,
            "mock": True
        }
