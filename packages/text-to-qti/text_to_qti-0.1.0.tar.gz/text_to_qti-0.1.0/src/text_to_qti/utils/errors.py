"""Custom exception classes for text-to-qti converter."""

from typing import Optional


class TextToQTIError(Exception):
    """Base exception for all text-to-qti errors."""

    pass


class ParseError(TextToQTIError):
    """Error during parsing of text file."""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        column: Optional[int] = None,
    ) -> None:
        """Initialize ParseError with optional line and column information.

        Args:
            message: Error message
            line_number: Line number where error occurred
            column: Column number where error occurred
        """
        self.message = message
        self.line_number = line_number
        self.column = column

        formatted_message = message
        if line_number is not None:
            formatted_message = f"Line {line_number}: {message}"
            if column is not None:
                formatted_message = f"Line {line_number}, Column {column}: {message}"

        super().__init__(formatted_message)


class ValidationError(TextToQTIError):
    """Error during validation of quiz content."""

    pass


class GenerationError(TextToQTIError):
    """Error during QTI XML generation."""

    pass
