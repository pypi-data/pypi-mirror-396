f"""
Quizy - A professional Python quiz framework
"""

from .core import (
    Quiz,
    Question,
    QuestionType,
    MultipleChoiceQuestion,
    MultipleSelectQuestion,
    ShortTextQuestion,
    TrueFalseQuestion,
    MatchingQuestion,
    QuizResult,
    QuestionResult,
    ResultStatus,
)
from .cli import QuizCLI, TimerDisplay

# Optional imports
try:
    from .api import QuizyAPI, create_app

    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

__version__ = "0.4.9-beta"
__all__ = [
    "Quiz",
    "Question",
    "QuestionType",
    "MultipleChoiceQuestion",
    "MultipleSelectQuestion",
    "ShortTextQuestion",
    "TrueFalseQuestion",
    "MatchingQuestion",
    "QuizResult",
    "QuestionResult",
    "ResultStatus",
    "QuizCLI",
    "TimerDisplay",
]

# Add API exports if available
if API_AVAILABLE:
    __all__.extend(["QuizyAPI", "create_app"])
