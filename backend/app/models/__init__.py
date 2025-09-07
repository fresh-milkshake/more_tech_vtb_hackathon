# Import all models to ensure they are registered with SQLAlchemy
from .candidate import Candidate
from .interview import Interview
from .question import Question
from .response import Response
from .timeline import TimelineEntry
from .user import User
from .vacancy import Vacancy
from .interview_link import InterviewLink

__all__ = [
    "Candidate",
    "Interview", 
    "Question",
    "Response",
    "TimelineEntry",
    "User",
    "Vacancy",
    "InterviewLink"
]
