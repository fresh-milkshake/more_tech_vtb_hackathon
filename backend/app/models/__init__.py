# Import all models to ensure they are registered with SQLAlchemy
from .candidate import Candidate
from .interview import Interview
from .question import Question
from .response import Response
from .resume import Resume
from .timeline import TimelineEntry
from .user import User
from .vacancy import Vacancy
from .interview_link import InterviewLink

__all__ = [
    "Candidate",
    "Interview", 
    "Question",
    "Response",
    "Resume",
    "TimelineEntry",
    "User",
    "Vacancy",
    "InterviewLink"
]
