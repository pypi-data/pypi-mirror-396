"""Base class for QTI item generators (extensible for different question types)."""

from abc import ABC, abstractmethod

from lxml import etree

from text_to_qti.parser.question_models import Question


class BaseItemGenerator(ABC):
    """Abstract base class for question type generators.

    This allows for extensibility - new question types can be added by
    creating new subclasses without modifying core code.
    """

    @abstractmethod
    def generate(self, question: Question) -> etree._Element:
        """Generate QTI item XML for a question.

        Args:
            question: Question to generate XML for

        Returns:
            XML element representing the item

        Raises:
            GenerationError: If generation fails
        """
        pass

    def validate_question(self, question: Question) -> None:
        """Validate that question is suitable for this generator.

        Args:
            question: Question to validate

        Raises:
            ValueError: If question is invalid for this type
        """
        pass
