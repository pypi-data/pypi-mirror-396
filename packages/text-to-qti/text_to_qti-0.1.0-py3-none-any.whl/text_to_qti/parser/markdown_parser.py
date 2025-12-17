"""Parser for converting markdown quiz files to Question objects."""

import re
from typing import List, Optional

import markdown
import yaml

from text_to_qti.parser.question_models import (
    AnswerChoice,
    Question,
    QuestionType,
    Quiz,
    QuizMetadata,
)
from text_to_qti.utils.errors import ParseError


class MarkdownParser:
    """Parse markdown-formatted quiz files into Quiz objects."""

    # Regex patterns
    YAML_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL)
    QUESTION_PATTERN = re.compile(
        r"^##\s+Question\s+\d+\s*\n(.*?)(?=^##\s+Question|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    METADATA_PATTERN = re.compile(r"^\[(\w+):\s*([^\]]+)\]\s*$", re.MULTILINE)
    ANSWER_PATTERN = re.compile(r"^(\*)?([a-z])\)\s+(.+)$", re.MULTILINE)

    def __init__(self) -> None:
        """Initialize the parser."""
        self.markdown_converter = markdown.Markdown(extensions=["extra", "sane_lists"])

    def parse_file(self, file_path: str) -> Quiz:
        """Parse a quiz file and return a Quiz object.

        Args:
            file_path: Path to the quiz file

        Returns:
            Parsed Quiz object

        Raises:
            ParseError: If parsing fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError as e:
            raise ParseError(f"File not found: {file_path}") from e
        except UnicodeDecodeError as e:
            raise ParseError(f"File must be UTF-8 encoded: {file_path}") from e

        return self.parse_content(content)

    def parse_content(self, content: str) -> Quiz:
        """Parse quiz content from a string.

        Args:
            content: Quiz content as string

        Returns:
            Parsed Quiz object

        Raises:
            ParseError: If parsing fails
        """
        # Extract and parse YAML front matter
        metadata = self._extract_metadata(content)

        # Remove YAML from content
        content_without_yaml = self.YAML_PATTERN.sub("", content).strip()

        # Extract questions
        questions = self._extract_questions(content_without_yaml)

        # Create and return Quiz object
        quiz = Quiz(metadata=metadata, questions=questions)
        return quiz

    def _extract_metadata(self, content: str) -> QuizMetadata:
        """Extract YAML metadata from content.

        Args:
            content: Content to parse

        Returns:
            QuizMetadata object

        Raises:
            ParseError: If YAML is invalid
        """
        yaml_match = self.YAML_PATTERN.search(content)

        if yaml_match:
            yaml_content = yaml_match.group(1)
            try:
                yaml_data = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError as e:
                raise ParseError(f"Invalid YAML front matter: {e}") from e

            # Set defaults
            title = yaml_data.get("title", "Untitled Quiz")
            description = yaml_data.get("description")
            points_per_question = yaml_data.get("points_per_question", 1)
            shuffle_answers = yaml_data.get("shuffle_answers", False)

            return QuizMetadata(
                title=title,
                description=description,
                points_per_question=points_per_question,
                shuffle_answers=shuffle_answers,
            )
        else:
            # Use defaults
            return QuizMetadata(title="Untitled Quiz")

    def _extract_questions(self, content: str) -> List[Question]:
        """Extract question blocks from content.

        Args:
            content: Content to parse

        Returns:
            List of Question objects

        Raises:
            ParseError: If parsing fails
        """
        questions: List[Question] = []
        question_blocks = self.QUESTION_PATTERN.findall(content)

        if not question_blocks:
            raise ParseError(
                "No questions found in quiz. Questions must start with '## Question N'"
            )

        for idx, block in enumerate(question_blocks, 1):
            try:
                question = self._parse_question_block(block)
                questions.append(question)
            except ParseError as e:
                raise ParseError(f"Error parsing Question {idx}: {e.message}") from e

        return questions

    def _parse_question_block(self, block: str) -> Question:
        """Parse a single question block.

        Args:
            block: Question block text

        Returns:
            Parsed Question object

        Raises:
            ParseError: If parsing fails
        """
        lines = block.split("\n")
        question_id: str = ""  # Generate ID only if not provided, don't set it later
        question_type: Optional[QuestionType] = None
        points = 1
        question_text = ""
        text_lines: List[str] = []
        choices: List[AnswerChoice] = []
        feedback: Optional[str] = None
        in_choices = False
        in_feedback = False

        line_idx = 0
        while line_idx < len(lines):
            line = lines[line_idx]

            # Parse metadata tags
            meta_match = self.METADATA_PATTERN.match(line)
            if meta_match:
                key, value = meta_match.groups()
                if key == "Type":
                    try:
                        question_type = QuestionType(value.strip().lower())
                    except ValueError:
                        raise ParseError(
                            f"Invalid question type: {value}. "
                            "Must be 'multiple_choice' or 'true_false'"
                        )
                elif key == "Points":
                    try:
                        points = int(value.strip())
                    except ValueError:
                        raise ParseError(
                            f"Invalid points value: {value}. Must be an integer"
                        )
                elif key == "ID":
                    question_id = value.strip()
                line_idx += 1
                continue

            # Check for answer choices
            if line.strip() and not in_feedback:
                choice_match = self.ANSWER_PATTERN.match(line)
                if choice_match:
                    is_correct, letter, text = choice_match.groups()
                    choices.append(
                        AnswerChoice(
                            letter=letter,
                            text=text.strip(),
                            is_correct=is_correct is not None,
                        )
                    )
                    in_choices = True
                    line_idx += 1
                    continue

            # Check for feedback
            if (
                in_choices
                and line.strip()
                and line.strip().lower().startswith("feedback:")
            ):
                feedback_text = line.strip()[9:].strip()
                feedback_lines = [feedback_text] if feedback_text else []

                # Collect remaining feedback lines
                line_idx += 1
                while line_idx < len(lines):
                    next_line = lines[line_idx]
                    if next_line.strip():
                        feedback_lines.append(next_line.strip())
                    else:
                        break
                    line_idx += 1

                feedback = " ".join(feedback_lines)
                in_feedback = True
                continue

            # Question text
            if not in_choices and line.strip():
                text_lines.append(line)

            line_idx += 1

        # Join question text
        if text_lines:
            question_text = "\n".join(text_lines).strip()

        # Validate
        if not question_type:
            raise ParseError(
                "Question type not specified. "
                "Use [Type: multiple_choice] or [Type: true_false]"
            )

        if not question_text:
            raise ParseError("Question text is empty")

        if not choices:
            raise ParseError("No answer choices found")

        # Create and return Question
        # Note: If question_id is empty, Question model will auto-generate one
        return Question(
            id=question_id,  # Empty string will trigger auto-generation in model
            type=question_type,
            text=question_text,
            choices=choices,
            points=points,
            feedback=feedback,
        )
