"""Pydantic models for quiz questions and metadata."""

import uuid
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class QuestionType(str, Enum):
    """Supported question types."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"


class AnswerChoice(BaseModel):
    """Model for a single answer choice."""

    letter: str = Field(..., description="Letter identifier (a, b, c, etc.)")
    text: str = Field(..., description="Answer choice text")
    is_correct: bool = Field(..., description="Whether this is the correct answer")

    @field_validator("letter")
    @classmethod
    def validate_letter(cls, v: str) -> str:
        """Validate that letter is a single lowercase letter."""
        if not (len(v) == 1 and v.isalpha() and v.islower()):
            raise ValueError(f"Letter must be a single lowercase letter, got: {v}")
        return v

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate that text is not empty."""
        if not v.strip():
            raise ValueError("Answer choice text cannot be empty")
        return v.strip()


class Question(BaseModel):
    """Model for a question."""

    model_config = {"validate_default": True}

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique question ID"
    )
    type: QuestionType = Field(..., description="Question type")
    text: str = Field(..., description="Question text")
    choices: List[AnswerChoice] = Field(..., description="Answer choices")
    points: int = Field(default=1, ge=1, description="Points for this question")
    feedback: Optional[str] = Field(
        default=None, description="Feedback shown after answering"
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate that question text is not empty."""
        if not v.strip():
            raise ValueError("Question text cannot be empty")
        return v.strip()

    @field_validator("id", mode="before")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Generate ID if empty string provided."""
        if not v or not v.strip():
            return str(uuid.uuid4())
        return v

    @field_validator("choices")
    @classmethod
    def validate_choices(cls, v: List[AnswerChoice], info) -> List[AnswerChoice]:
        """Validate answer choices structure."""
        if not v:
            raise ValueError("Question must have at least one answer choice")

        # Check that letters are sequential
        letters = [choice.letter for choice in v]
        expected_letters = [chr(ord("a") + i) for i in range(len(v))]
        if letters != expected_letters:
            raise ValueError(
                f"Answer letters must be sequential (a, b, c, ...), got: {letters}"
            )

        # Check that at least one answer is correct
        if not any(choice.is_correct for choice in v):
            raise ValueError("Question must have at least one correct answer")

        # Type-specific validation
        question_type = info.data.get("type")
        if question_type == QuestionType.TRUE_FALSE:
            if len(v) != 2:
                raise ValueError("True/False questions must have exactly 2 choices")
        elif question_type == QuestionType.MULTIPLE_CHOICE:
            if len(v) < 2:
                raise ValueError(
                    "Multiple choice questions must have at least 2 choices"
                )
            # Only one correct answer for multiple choice
            correct_count = sum(1 for choice in v if choice.is_correct)
            if correct_count != 1:
                raise ValueError(
                    "Multiple choice questions must have exactly "
                    f"1 correct answer, got: {correct_count}"
                )

        return v

    @field_validator("feedback")
    @classmethod
    def validate_feedback(cls, v: Optional[str]) -> Optional[str]:
        """Validate feedback if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class QuizMetadata(BaseModel):
    """Model for quiz metadata."""

    title: str = Field(..., description="Quiz title")
    description: Optional[str] = Field(default=None, description="Quiz description")
    points_per_question: int = Field(
        default=1, ge=1, description="Default points per question"
    )
    shuffle_answers: bool = Field(
        default=False, description="Whether to shuffle answer choices"
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate that title is not empty."""
        if not v.strip():
            raise ValueError("Quiz title cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Validate description if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class Quiz(BaseModel):
    """Model for a complete quiz."""

    metadata: QuizMetadata = Field(..., description="Quiz metadata")
    questions: List[Question] = Field(..., description="List of questions")

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, v: List[Question]) -> List[Question]:
        """Validate questions list."""
        if not v:
            raise ValueError("Quiz must have at least one question")

        # Check for duplicate question IDs
        ids = [q.id for q in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate question IDs found")

        return v

    def get_total_points(self) -> int:
        """Calculate total possible points for the quiz."""
        return sum(q.points for q in self.questions)
