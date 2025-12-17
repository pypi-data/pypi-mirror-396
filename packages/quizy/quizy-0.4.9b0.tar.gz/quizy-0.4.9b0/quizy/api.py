"""
Quizy FastAPI Wrapper - Complete API interface for quiz functionality
"""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    import uvicorn
except ImportError:
    raise ImportError(
        "FastAPI dependencies not installed. Install with: pip install quizy[api]"
    )

from .core import (
    Quiz, Question, QuestionType, QuizResult,
    MultipleChoiceQuestion, MultipleSelectQuestion,
    TrueFalseQuestion, ShortTextQuestion, MatchingQuestion
)

try:
    from .ai_generator import AIQuestionGenerator
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


# Pydantic models for API
class ManualQuestionData(BaseModel):
    text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: Union[str, List[str], Dict[str, str], None] = None
    shuffle_options: bool = False
    shuffle_answers: bool = False
    allow_partial_credit: bool = False
    time_limit: Optional[int] = None
    pairs: Optional[Dict[str, str]] = None


# Pydantic models for API
class AIQuestionData(BaseModel):
    topic: str
    question_type: Union[QuestionType, str] = QuestionType.MULTIPLE_CHOICE
    difficulty: str = "medium"
    num_options: int = 4
    time_limit: int = 20
    context: Optional[str] = None


class QuizData(BaseModel):
    title: str = "Untitled Quiz"
    description: Optional[str] = None
    time_limit: Optional[int] = None
    shuffle_options: bool = False
    questions: List[ManualQuestionData | AIQuestionData] = []


class QuizSessionData(BaseModel):
    quiz_id: str
    answers: Dict[str, Any]
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AIGenerationRequest(BaseModel):
    topic: str
    num_questions: int = 5
    question_types: List[str] = ["multiple_choice", "true_false"]
    difficulty: str = "medium"


class QuizResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    time_limit: Optional[int]
    shuffle_options: bool
    num_questions: int
    created_at: datetime


class QuestionResponse(BaseModel):
    id: str
    text: str
    question_type: str
    options: Optional[List[str]]
    time_limit: Optional[int]
    has_partial_credit: bool


class QuizResultResponse(BaseModel):
    quiz_id: str
    score_percentage: float
    correct_answers: int
    total_questions: int
    time_taken: Optional[float]
    question_results: List[Dict[str, Any]]


class QuizyAPI:
    """
    FastAPI wrapper for Quizy quiz framework.
    
    Usage:
        from quizy.api import QuizyAPI
        app = QuizyAPI()
        
    Then run with: uvicorn main:app --reload
    """
    
    def __init__(
        self,
        title: str = "Quizy API",
        description: str = "Interactive Quiz Framework API",
        version: str = "1.0.0",
        enable_cors: bool = True,
        prefix: str = "",
        docs_url: Optional[str] = "/docs",
        redoc_url: Optional[str] = "/redoc"
    ):
        # Store prefix for route configuration
        self.prefix = prefix.rstrip("/") if prefix else ""
        
        # Adjust docs URLs with prefix
        final_docs_url = f"{self.prefix}{docs_url}" if docs_url else None
        final_redoc_url = f"{self.prefix}{redoc_url}" if redoc_url else None
        
        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
            docs_url=final_docs_url,
            redoc_url=final_redoc_url
        )
        
        if enable_cors:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        # In-memory storage (replace with database in production)
        self.quizzes: Dict[str, Quiz] = {}
        self.quiz_sessions: Dict[str, QuizSessionData] = {}
        
        # Initialize AI generator if available
        self.ai_generator = AIQuestionGenerator() if AI_AVAILABLE else None
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get(f"{self.prefix}/", tags=["General"])
        async def root():
            """Root endpoint with API information"""
            return {
                "message": "Welcome to Quizy API",
                "docs": f"{self.prefix}/docs" if docs_url else "Documentation disabled",
                "redoc": f"{self.prefix}/redoc" if redoc_url else "ReDoc disabled",
                "ai_enabled": AI_AVAILABLE,
                "prefix": self.prefix if self.prefix else "No prefix",
                "endpoints": {
                    "quizzes": f"{self.prefix}/quizzes",
                    "generate_ai": f"{self.prefix}/generate-ai-quiz",
                    "add_manual_question": f"{self.prefix}/quizzes/{{quiz_id}}/add_manual_question",
                    "add_ai_question": f"{self.prefix}/quizzes/{{quiz_id}}/add_ai_question"
                }
            }
        
        @self.app.get(f"{self.prefix}/health", tags=["General"])
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now()}
        
        # Quiz CRUD operations
        @self.app.post(f"{self.prefix}/quizzes", response_model=QuizResponse, tags=["Quizzes"])
        async def create_quiz(quiz_data: QuizData):
            """Create a new quiz"""
            quiz_id = str(uuid.uuid4())
            
            # Create quiz object
            quiz = Quiz(
                title=quiz_data.title,
                time_limit=quiz_data.time_limit,
                shuffle_options=quiz_data.shuffle_options
            )
            
            # Add questions
            for q_data in quiz_data.questions:
                question = self._create_question_from_data(q_data)
                if question:
                    quiz.add_question(question)
            
            self.quizzes[quiz_id] = quiz
            
            return QuizResponse(
                id=quiz_id,
                title=quiz.title,
                description=quiz_data.description,
                time_limit=quiz.time_limit,
                shuffle_options=quiz.shuffle_options,
                num_questions=len(quiz.questions),
                created_at=datetime.now()
            )
        
        @self.app.get(f"{self.prefix}/quizzes", tags=["Quizzes"])
        async def list_quizzes():
            """List all available quizzes"""
            quiz_list = []
            for quiz_id, quiz in self.quizzes.items():
                quiz_list.append({
                    "id": quiz_id,
                    "title": quiz.title,
                    "num_questions": len(quiz.questions),
                    "time_limit": quiz.time_limit
                })
            return {"quizzes": quiz_list}
        
        @self.app.get(f"{self.prefix}/quizzes/{{quiz_id}}", tags=["Quizzes"])
        async def get_quiz(quiz_id: str):
            """Get quiz details without revealing correct answers"""
            if quiz_id not in self.quizzes:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            quiz = self.quizzes[quiz_id]
            questions = []
            
            for i, question in enumerate(quiz.questions):
                q_data = {
                    "id": str(i),
                    "text": question.text,
                    "question_type": question.__class__.__name__,
                    "time_limit": getattr(question, 'time_limit', None),
                    "has_partial_credit": getattr(question, 'allow_partial_credit', False)
                }
                
                # Add options without revealing correct answers
                if hasattr(question, 'options'):
                    q_data["options"] = question.options
                elif hasattr(question, 'pairs') and hasattr(question, 'get_shuffled_answers'):
                    # For matching questions, provide items to match
                    q_data["items"] = list(question.pairs.keys())
                    q_data["answers"] = question.get_shuffled_answers()
                
                questions.append(q_data)
            
            return {
                "id": quiz_id,
                "title": quiz.title,
                "time_limit": quiz.time_limit,
                "shuffle_options": quiz.shuffle_options,
                "questions": questions
            }
        
        @self.app.delete(f"{self.prefix}/quizzes/{{quiz_id}}", tags=["Quizzes"])
        async def delete_quiz(quiz_id: str):
            """Delete a quiz"""
            if quiz_id not in self.quizzes:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            del self.quizzes[quiz_id]
            return {"message": f"Quiz {quiz_id} deleted successfully"}
        
        # Question management within quizzes
        @self.app.post(f"{self.prefix}/quizzes/{{quiz_id}}/add_manual_question", tags=["Questions"])
        async def add_manual_question_to_quiz(quiz_id: str, question_request: ManualQuestionData):
            """
            Add a new question to an existing quiz.
            
            Manual Questions:
            - Provide: text, question_type, options/pairs, correct_answer
            - Optional: shuffle_options, allow_partial_credit, time_limit


            Question Types:
                1. "multiple_choice" (default)
                2. "multiple_select"
                3. "short_text"
                4. "matching"
                5. "true_false"

            """
            if quiz_id not in self.quizzes:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            quiz = self.quizzes[quiz_id]
            question = None
            
            if not question_request.text:
                raise HTTPException(status_code=400, detail="Text is required for manual questions")
            if not question_request.question_type:
                raise HTTPException(status_code=400, detail="Question type is required for manual questions")
        
            
            question = self._create_question_from_data(question_request)
            
            
            if not question:
                raise HTTPException(status_code=400, detail="Invalid question data or generation failed")
            
            quiz.add_question(question)
            question_idx = len(quiz.questions) - 1
            
            return {
                "message": "Manual question added successfully",
                "question_id": str(question_idx),
                "quiz_id": quiz_id,
                "total_questions": len(quiz.questions),
                "question_text": question.text,
                "question_type": question.__class__.__name__
            }

        @self.app.post(f"{self.prefix}/quizzes/{{quiz_id}}/add_ai_question", tags=["Questions"])
        async def add_ai_question_to_quiz(quiz_id: str, question_request: AIQuestionData):
            """
            Add a new question to an existing quiz (AI)
            
            For AI Questions:
            - Provide: topic, question_type, difficulty
            - Optional: num_options, context, time_limit

            Question Types:
                1. "multiple_choice" (default)
                2. "multiple_select"
                3. "short_text"
                4. "matching"
                5. "true_false"
            """
            if quiz_id not in self.quizzes:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            quiz = self.quizzes[quiz_id]
            question = None
            
            if not question_request.topic:
                raise HTTPException(status_code=400, detail="Text is required for manual questions")
        
            question = await self.ai_generator.generate_question_async(**question_request.model_dump())
            
            
            if not question:
                raise HTTPException(status_code=400, detail="Invalid question data or generation failed")
            
            quiz.add_question(question)
            question_idx = len(quiz.questions) - 1
            
            return {
                "message": f"AI question added successfully",
                "question_id": str(question_idx),
                "quiz_id": quiz_id,
                "total_questions": len(quiz.questions),
                "question_text": question.text,
                "question_type": question.__class__.__name__
            }
        
        @self.app.get(f"{self.prefix}/quizzes/{{quiz_id}}/questions", tags=["Questions"])
        async def get_quiz_questions(quiz_id: str, include_answers: bool = False):
            """Get all questions from a quiz with optional answer inclusion"""
            if quiz_id not in self.quizzes:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            quiz = self.quizzes[quiz_id]
            questions = []
            
            for i, question in enumerate(quiz.questions):
                q_data = {
                    "id": str(i),
                    "text": question.text,
                    "question_type": question.__class__.__name__,
                    "time_limit": getattr(question, 'time_limit', None),
                    "has_partial_credit": getattr(question, 'allow_partial_credit', False)
                }
                
                # Add options and answers based on question type
                if hasattr(question, 'options'):
                    q_data["options"] = question.options
                    if include_answers:
                        q_data["correct_answer"] = question.get_correct_option()
                
                elif hasattr(question, 'pairs'):
                    q_data["items"] = list(question.pairs.keys())
                    if hasattr(question, 'get_shuffled_answers'):
                        q_data["answers"] = question.get_shuffled_answers()
                    if include_answers:
                        q_data["correct_pairs"] = question.pairs
                
                else:
                    # For true/false and short text questions
                    if include_answers:
                        q_data["correct_answer"] = question.get_correct_option()
                
                questions.append(q_data)
            
            return {
                "quiz_id": quiz_id,
                "quiz_title": quiz.title,
                "total_questions": len(questions),
                "questions": questions
            }
        
        @self.app.get(f"{self.prefix}/quizzes/{{quiz_id}}/questions/{{question_id}}", tags=["Questions"])
        async def get_specific_question(quiz_id: str, question_id: str, include_answer: bool = False):
            """Get a specific question from a quiz"""
            if quiz_id not in self.quizzes:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            quiz = self.quizzes[quiz_id]
            
            try:
                question_idx = int(question_id)
                if question_idx < 0 or question_idx >= len(quiz.questions):
                    raise HTTPException(status_code=404, detail="Question not found")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid question ID")
            
            question = quiz.questions[question_idx]
            
            q_data = {
                "id": question_id,
                "text": question.text,
                "question_type": question.__class__.__name__,
                "time_limit": getattr(question, 'time_limit', None),
                "has_partial_credit": getattr(question, 'allow_partial_credit', False)
            }
            
            # Add question-specific data
            if hasattr(question, 'options'):
                q_data["options"] = question.options
                q_data["shuffle_options"] = getattr(question, 'shuffle_options', False)
                if include_answer:
                    q_data["correct_answer"] = question.get_correct_option()
            
            elif hasattr(question, 'pairs'):
                q_data["items"] = list(question.pairs.keys())
                q_data["shuffle_answers"] = getattr(question, 'shuffle_answers', False)
                if hasattr(question, 'get_shuffled_answers'):
                    q_data["answers"] = question.get_shuffled_answers()
                if include_answer:
                    q_data["correct_pairs"] = question.pairs
            
            else:
                if include_answer:
                    q_data["correct_answer"] = question.get_correct_option()
            
            return q_data
        
        @self.app.put(f"{self.prefix}/quizzes/{{quiz_id}}/questions/{{question_id}}", tags=["Questions"])
        async def update_question(quiz_id: str, question_id: str, question_data: ManualQuestionData | AIQuestionData):
            """Update a specific question in a quiz"""
            if quiz_id not in self.quizzes:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            quiz = self.quizzes[quiz_id]
            
            try:
                question_idx = int(question_id)
                if question_idx < 0 or question_idx >= len(quiz.questions):
                    raise HTTPException(status_code=404, detail="Question not found")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid question ID")
            
            new_question = self._create_question_from_data(question_data)
            if not new_question:
                raise HTTPException(status_code=400, detail="Invalid question data")
            
            # Replace the question
            quiz.questions[question_idx] = new_question
            
            return {
                "message": "Question updated successfully",
                "question_id": question_id,
                "quiz_id": quiz_id
            }
        
        @self.app.delete(f"{self.prefix}/quizzes/{{quiz_id}}/questions/{{question_id}}", tags=["Questions"])
        async def delete_question_from_quiz(quiz_id: str, question_id: str):
            """Delete a specific question from a quiz"""
            if quiz_id not in self.quizzes:
                raise HTTPException(status_code=404, detail="Quiz not found")
            
            quiz = self.quizzes[quiz_id]
            
            try:
                question_idx = int(question_id)
                if question_idx < 0 or question_idx >= len(quiz.questions):
                    raise HTTPException(status_code=404, detail="Question not found")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid question ID")
            
            # Remove the question
            deleted_question = quiz.questions.pop(question_idx)
            
            return {
                "message": "Question deleted successfully",
                "deleted_question_text": deleted_question.text,
                "quiz_id": quiz_id,
                "remaining_questions": len(quiz.questions)
            }
        
       # AI-powered question generation (if available)
        if AI_AVAILABLE:
            @self.app.post(f"{self.prefix}/generate-ai-quiz", response_model=QuizResponse, tags=["AI Generation"])
            async def generate_ai_quiz(request: AIGenerationRequest):
                """Generate a quiz using AI"""
                if not self.ai_generator:
                    raise HTTPException(status_code=503, detail="AI generation not available")
                
                try:
                    # Convert string types to enum
                    question_types = []
                    type_mapping = {
                        "multiple_choice": QuestionType.MULTIPLE_CHOICE,
                        "multiple_select": QuestionType.MULTIPLE_SELECT,
                        "true_false": QuestionType.TRUE_FALSE,
                        "short_text": QuestionType.SHORT_TEXT,
                        "matching": QuestionType.MATCHING
                    }
                    
                    for q_type in request.question_types:
                        if q_type in type_mapping:
                            question_types.append(type_mapping[q_type])
                    
                    # Generate questions - handle async properly
                    if hasattr(self.ai_generator, 'generate_questions_set_async'):
                        questions = await self.ai_generator.generate_questions_set_async(
                            topic=request.topic,
                            num_questions=request.num_questions,
                            question_types=question_types,
                            difficulty=request.difficulty
                        )
                    else:
                        # Run in executor to avoid blocking the event loop
                        import asyncio
                        from concurrent.futures import ThreadPoolExecutor
                        
                        loop = asyncio.get_event_loop()
                        with ThreadPoolExecutor() as executor:
                            questions = await loop.run_in_executor(
                                executor,
                                lambda: self.ai_generator.generate_questions_set(
                                    topic=request.topic,
                                    num_questions=request.num_questions,
                                    question_types=question_types,
                                    difficulty=request.difficulty
                                )
                            )
                    
                    # Create quiz
                    quiz_id = str(uuid.uuid4())
                    quiz = Quiz(title=f"AI Generated Quiz: {request.topic}")
                    
                    for question in questions:
                        if question:
                            quiz.add_question(question)
                    
                    self.quizzes[quiz_id] = quiz
                    
                    return QuizResponse(
                        id=quiz_id,
                        title=quiz.title,
                        description=f"AI-generated quiz about {request.topic}",
                        time_limit=quiz.time_limit,
                        shuffle_options=quiz.shuffle_options,
                        num_questions=len(quiz.questions),
                        created_at=datetime.now()
                    )
                
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
        
        # Question types information
        @self.app.get(f"{self.prefix}/question-types", tags=["General"])
        async def get_question_types():
            """Get available question types and their schemas"""
            return {
                "types": {
                    "multiple_choice": {
                        "description": "Single correct answer from multiple options",
                        "required_fields": ["text", "options", "correct_answer"],
                        "optional_fields": ["shuffle_options", "time_limit"]
                    },
                    "multiple_select": {
                        "description": "Multiple correct answers from options",
                        "required_fields": ["text", "options", "correct_answer"],
                        "optional_fields": ["shuffle_options", "allow_partial_credit", "time_limit"]
                    },
                    "true_false": {
                        "description": "Binary true/false question",
                        "required_fields": ["text", "correct_answer"],
                        "optional_fields": ["time_limit"]
                    },
                    "short_text": {
                        "description": "Free-form text answer",
                        "required_fields": ["text", "correct_answer"],
                        "optional_fields": ["time_limit"]
                    },
                    "matching": {
                        "description": "Match items to their descriptions",
                        "required_fields": ["text", "pairs"],
                        "optional_fields": ["shuffle_answers", "allow_partial_credit", "time_limit"]
                    }
                }
            }
    
    def _create_question_from_data(self, q_data: ManualQuestionData | AIQuestionData) -> Optional[Question]:
        """Create a question object from API data"""
        try:
            if q_data.question_type.lower() == "multiple_choice" or q_data.question_type == "MultipleChoiceQuestion":
                return MultipleChoiceQuestion(
                    text=q_data.text,
                    options=q_data.options or [],
                    correct_answer=q_data.correct_answer,
                    shuffle_options=q_data.shuffle_options,
                    time_limit=q_data.time_limit
                )
            
            elif q_data.question_type.lower() == "multiple_select" or q_data.question_type == "MultipleSelectQuestion":
                return MultipleSelectQuestion(
                    text=q_data.text,
                    options=q_data.options or [],
                    correct_answers=q_data.correct_answer if isinstance(q_data.correct_answer, list) else [q_data.correct_answer],
                    shuffle_options=q_data.shuffle_options,
                    allow_partial_credit=q_data.allow_partial_credit,
                    time_limit=q_data.time_limit
                )
            
            elif q_data.question_type.lower() == "true_false" or q_data.question_type == "TrueFalseQuestion":
                return TrueFalseQuestion(
                    text=q_data.text,
                    correct_answer=q_data.correct_answer,
                    time_limit=q_data.time_limit
                )
            
            elif q_data.question_type.lower() == "short_text" or q_data.question_type == "ShortTextQuestion":
                return ShortTextQuestion(
                    text=q_data.text,
                    correct_answer=q_data.correct_answer,
                    time_limit=q_data.time_limit
                )
            
            elif q_data.question_type.lower() == "matching" or q_data.question_type == "MatchingQuestion":
                return MatchingQuestion(
                    text=q_data.text,
                    pairs=q_data.pairs or {},
                    shuffle_answers=q_data.shuffle_answers,
                    allow_partial_credit=q_data.allow_partial_credit,
                    time_limit=q_data.time_limit
                )
            
            return None
            
        except Exception as e:
            print(f"Error creating question: {e}")
            return None
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Run the FastAPI application with Uvicorn"""
        uvicorn.run(self.app, host=host, port=port, **kwargs)
    
    def __call__(self):
        """Make the class callable to return the FastAPI app"""
        return self.app


# Convenience function for creating the app
def create_app(**kwargs) -> FastAPI:
    """Create and return a Quizy FastAPI application
    
    Args:
        title: API title (default: "Quizy API")
        description: API description (default: "Interactive Quiz Framework API")
        version: API version (default: "1.0.0")
        enable_cors: Enable CORS middleware (default: True)
        prefix: URL prefix for all routes (default: "", example: "/api/v1")
        docs_url: Swagger documentation URL (default: "/docs", None to disable)
        redoc_url: ReDoc documentation URL (default: "/redoc", None to disable)
    """
    api = QuizyAPI(**kwargs)
    return api.app