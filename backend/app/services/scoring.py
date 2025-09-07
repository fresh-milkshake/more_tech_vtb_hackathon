import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


class ScoringService:
    """Service for calculating interview scores and analytics"""
    
    def __init__(self):
        self.score_weights = {
            "technical_accuracy": 0.3,
            "communication_clarity": 0.25,
            "relevance": 0.25,
            "completeness": 0.2
        }
        
        self.passing_threshold = 6.0  # Minimum score to pass
        self.excellence_threshold = 8.5  # Score for excellent performance
        
    def calculate_response_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate final score for a response based on AI analysis"""
        try:
            # Extract individual scores
            technical = float(analysis.get("technical_accuracy", 0))
            clarity = float(analysis.get("communication_clarity", 0))
            relevance = float(analysis.get("relevance", 0))
            completeness = float(analysis.get("completeness", 0))
            
            # Calculate weighted average
            weighted_score = (
                technical * self.score_weights["technical_accuracy"] +
                clarity * self.score_weights["communication_clarity"] +
                relevance * self.score_weights["relevance"] +
                completeness * self.score_weights["completeness"]
            )
            
            # Ensure score is within valid range
            return max(0.0, min(10.0, weighted_score))
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating response score: {str(e)}")
            return 0.0
    
    def calculate_interview_score(
        self, 
        responses: List[Dict[str, Any]], 
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Calculate overall interview score and analytics"""
        
        if not responses:
            return {
                "total_score": 0.0,
                "average_score": 0.0,
                "score_distribution": {},
                "performance_level": "insufficient",
                "recommendation": "reject"
            }
        
        try:
            scores = []
            category_scores = {}
            
            for response in responses:
                score = float(response.get("score", 0))
                scores.append(score)
                
                # Group by category
                category = response.get("category", "general")
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)
            
            # Calculate statistics
            average_score = statistics.mean(scores)
            median_score = statistics.median(scores)
            std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
            
            # Calculate category averages
            category_averages = {}
            for category, cat_scores in category_scores.items():
                category_averages[category] = statistics.mean(cat_scores)
            
            # Determine performance level
            performance_level = self._get_performance_level(average_score)
            
            # Generate recommendation
            recommendation = self._get_recommendation(average_score, scores)
            
            # Score distribution
            distribution = self._get_score_distribution(scores)
            
            return {
                "total_score": sum(scores),
                "average_score": round(average_score, 2),
                "median_score": round(median_score, 2),
                "standard_deviation": round(std_dev, 2),
                "highest_score": max(scores),
                "lowest_score": min(scores),
                "questions_answered": len(scores),
                "category_scores": category_averages,
                "score_distribution": distribution,
                "performance_level": performance_level,
                "recommendation": recommendation,
                "consistency": self._calculate_consistency(scores),
                "trend": self._calculate_trend(scores)
            }
            
        except Exception as e:
            logger.error(f"Error calculating interview score: {str(e)}")
            return {
                "total_score": 0.0,
                "average_score": 0.0,
                "error": str(e)
            }
    
    def _get_performance_level(self, average_score: float) -> str:
        """Determine performance level based on average score"""
        if average_score >= self.excellence_threshold:
            return "excellent"
        elif average_score >= self.passing_threshold:
            return "good"
        elif average_score >= 4.0:
            return "fair"
        else:
            return "poor"
    
    def _get_recommendation(self, average_score: float, all_scores: List[float]) -> str:
        """Generate hiring recommendation"""
        if average_score >= self.excellence_threshold:
            return "strong_hire"
        elif average_score >= self.passing_threshold:
            # Check consistency - no score below 4.0
            if all(score >= 4.0 for score in all_scores):
                return "hire"
            else:
                return "maybe"
        elif average_score >= 4.0:
            return "maybe"
        else:
            return "reject"
    
    def _get_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution by ranges"""
        distribution = {
            "excellent (8.5-10)": 0,
            "good (6.5-8.4)": 0,
            "fair (4.0-6.4)": 0,
            "poor (0-3.9)": 0
        }
        
        for score in scores:
            if score >= 8.5:
                distribution["excellent (8.5-10)"] += 1
            elif score >= 6.5:
                distribution["good (6.5-8.4)"] += 1
            elif score >= 4.0:
                distribution["fair (4.0-6.4)"] += 1
            else:
                distribution["poor (0-3.9)"] += 1
        
        return distribution
    
    def _calculate_consistency(self, scores: List[float]) -> Dict[str, Any]:
        """Calculate response consistency metrics"""
        if len(scores) < 2:
            return {"level": "insufficient_data", "coefficient": 0}
        
        try:
            mean_score = statistics.mean(scores)
            std_dev = statistics.stdev(scores)
            
            # Coefficient of variation (CV)
            cv = (std_dev / mean_score) if mean_score > 0 else float('inf')
            
            # Consistency levels based on CV
            if cv <= 0.15:
                level = "very_consistent"
            elif cv <= 0.25:
                level = "consistent"
            elif cv <= 0.35:
                level = "moderate"
            else:
                level = "inconsistent"
            
            return {
                "level": level,
                "coefficient": round(cv, 3),
                "standard_deviation": round(std_dev, 2),
                "range": round(max(scores) - min(scores), 2)
            }
            
        except Exception:
            return {"level": "error", "coefficient": 0}
    
    def _calculate_trend(self, scores: List[float]) -> Dict[str, Any]:
        """Calculate performance trend throughout interview"""
        if len(scores) < 3:
            return {"direction": "insufficient_data", "slope": 0}
        
        try:
            # Simple linear regression to find trend
            n = len(scores)
            x_values = list(range(n))
            
            # Calculate slope (trend)
            sum_xy = sum(x * y for x, y in zip(x_values, scores))
            sum_x = sum(x_values)
            sum_y = sum(scores)
            sum_x_sq = sum(x * x for x in x_values)
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x_sq - sum_x * sum_x)
            
            # Determine trend direction
            if slope > 0.5:
                direction = "improving"
            elif slope < -0.5:
                direction = "declining"
            else:
                direction = "stable"
            
            # Calculate first half vs second half comparison
            mid = n // 2
            first_half_avg = statistics.mean(scores[:mid]) if mid > 0 else 0
            second_half_avg = statistics.mean(scores[mid:]) if mid < n else 0
            
            return {
                "direction": direction,
                "slope": round(slope, 3),
                "first_half_average": round(first_half_avg, 2),
                "second_half_average": round(second_half_avg, 2),
                "improvement": round(second_half_avg - first_half_avg, 2)
            }
            
        except Exception:
            return {"direction": "error", "slope": 0}
    
    def generate_score_summary(self, interview_score: Dict[str, Any]) -> str:
        """Generate human-readable score summary"""
        try:
            avg_score = interview_score.get("average_score", 0)
            performance = interview_score.get("performance_level", "unknown")
            recommendation = interview_score.get("recommendation", "unknown")
            questions = interview_score.get("questions_answered", 0)
            consistency = interview_score.get("consistency", {}).get("level", "unknown")
            
            summary = f"""Interview Performance Summary:
            
Average Score: {avg_score}/10 ({performance.title()} Performance)
Questions Answered: {questions}
Recommendation: {recommendation.replace('_', ' ').title()}
Consistency: {consistency.replace('_', ' ').title()}

Score Breakdown:"""
            
            # Add category scores if available
            category_scores = interview_score.get("category_scores", {})
            if category_scores:
                summary += "\n"
                for category, score in category_scores.items():
                    summary += f"- {category.title()}: {score:.1f}/10\n"
            
            # Add trend information
            trend = interview_score.get("trend", {})
            if trend.get("direction") != "insufficient_data":
                summary += f"\nPerformance Trend: {trend.get('direction', 'stable').title()}"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating score summary: {str(e)}")
            return "Score summary unavailable"
    
    def compare_to_benchmarks(
        self, 
        average_score: float, 
        position: str = "general"
    ) -> Dict[str, Any]:
        """Compare score to position benchmarks"""
        
        # Mock benchmarks - in production, these would come from historical data
        benchmarks = {
            "software_developer": {"avg": 7.2, "min": 6.0, "excellent": 8.5},
            "senior_developer": {"avg": 8.0, "min": 7.0, "excellent": 9.0},
            "data_scientist": {"avg": 7.5, "min": 6.5, "excellent": 8.8},
            "product_manager": {"avg": 7.0, "min": 5.5, "excellent": 8.3},
            "general": {"avg": 7.0, "min": 6.0, "excellent": 8.5}
        }
        
        # Normalize position name
        position_key = position.lower().replace(" ", "_")
        benchmark = benchmarks.get(position_key, benchmarks["general"])
        
        return {
            "candidate_score": average_score,
            "benchmark_average": benchmark["avg"],
            "benchmark_minimum": benchmark["min"],
            "benchmark_excellent": benchmark["excellent"],
            "percentile": self._calculate_percentile(average_score, benchmark),
            "meets_minimum": average_score >= benchmark["min"],
            "above_average": average_score >= benchmark["avg"],
            "excellent_level": average_score >= benchmark["excellent"]
        }
    
    def _calculate_percentile(self, score: float, benchmark: Dict[str, float]) -> int:
        """Estimate percentile based on score and benchmarks"""
        if score >= benchmark["excellent"]:
            return min(95, int(90 + (score - benchmark["excellent"]) * 2))
        elif score >= benchmark["avg"]:
            return min(75, int(50 + (score - benchmark["avg"]) * 15))
        elif score >= benchmark["min"]:
            return max(25, int(25 + (score - benchmark["min"]) * 25))
        else:
            return max(5, int(score * 4))  # Scale 0-6 to 0-25 percentile