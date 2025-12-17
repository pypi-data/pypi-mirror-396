"""Validator for markdown quiz file syntax."""

import re

import yaml

from text_to_qti.utils.errors import ValidationError


class SyntaxValidator:
    """Validate markdown quiz file syntax before parsing."""

    # Regex patterns
    YAML_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*$", re.MULTILINE | re.DOTALL)
    QUESTION_HEADER_PATTERN = re.compile(r"^##\s+Question\s+\d+\s*$", re.MULTILINE)
    METADATA_PATTERN = re.compile(r"^\[(\w+):\s*([^\]]+)\]\s*$", re.MULTILINE)
    ANSWER_PATTERN = re.compile(r"^(\*)?([a-z])\)\s+(.+)$", re.MULTILINE)
    COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)

    def validate_file(self, file_path: str) -> None:
        """Validate a quiz file.

        Args:
            file_path: Path to the quiz file

        Raises:
            ValidationError: If file validation fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError as e:
            raise ValidationError(f"File not found: {file_path}") from e
        except UnicodeDecodeError as e:
            raise ValidationError(f"File must be UTF-8 encoded: {file_path}") from e

        self.validate_content(content)

    def validate_content(self, content: str) -> None:
        """Validate quiz content.

        Args:
            content: Quiz content as string

        Raises:
            ValidationError: If validation fails
        """
        # Remove comments
        content_no_comments = self.COMMENT_PATTERN.sub("", content)

        # Validate YAML if present
        self._validate_yaml(content_no_comments)

        # Validate structure
        self._validate_structure(content_no_comments)

        # Validate questions
        self._validate_questions(content_no_comments)

    def _validate_yaml(self, content: str) -> None:
        """Validate YAML front matter.

        Args:
            content: Content to validate

        Raises:
            ValidationError: If YAML is invalid
        """
        yaml_match = self.YAML_PATTERN.search(content)

        if yaml_match:
            yaml_content = yaml_match.group(1)
            try:
                yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                raise ValidationError(
                    f"Invalid YAML syntax in front matter: {e}"
                ) from e

    def _validate_structure(self, content: str) -> None:
        """Validate overall structure.

        Args:
            content: Content to validate

        Raises:
            ValidationError: If structure is invalid
        """
        # Check if there are any questions
        if not self.QUESTION_HEADER_PATTERN.search(content):
            raise ValidationError(
                "No questions found. "
                "Questions must start with '## Question N' where N is a number."
            )

    def _validate_questions(self, content: str) -> None:
        """Validate individual questions.

        Args:
            content: Content to validate

        Raises:
            ValidationError: If any question is invalid
        """
        # Remove YAML from content
        content_without_yaml = self.YAML_PATTERN.sub("", content).strip()

        # Split into question blocks
        question_pattern = re.compile(
            r"^##\s+Question\s+(\d+)(.*?)(?=^##\s+Question|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        questions = question_pattern.findall(content_without_yaml)

        if not questions:
            raise ValidationError("No questions found in content")

        for question_num, block in questions:
            self._validate_question_block(block, int(question_num))

    def _validate_question_block(self, block: str, question_num: int) -> None:
        """Validate a single question block.

        Args:
            block: Question block content
            question_num: Question number for error reporting

        Raises:
            ValidationError: If question is invalid
        """
        lines = block.split("\n")

        # Check for question type
        has_type = False
        question_type: str = ""

        for line in lines:
            meta_match = self.METADATA_PATTERN.match(line)
            if meta_match:
                key, value = meta_match.groups()
                if key == "Type":
                    has_type = True
                    question_type = value.strip().lower()
                    if question_type not in ["multiple_choice", "true_false"]:
                        raise ValidationError(
                            f"Question {question_num}: "
                            f"Invalid question type '{question_type}'. "
                            "Must be 'multiple_choice' or 'true_false'"
                        )
                elif key == "Points":
                    try:
                        int(value.strip())
                    except ValueError:
                        raise ValidationError(
                            f"Question {question_num}: Points value '{value}' "
                            "is not an integer"
                        )

        if not has_type:
            raise ValidationError(
                f"Question {question_num}: No question type specified. "
                "Use [Type: multiple_choice] or [Type: true_false]"
            )

        # Check for question text and choices
        choice_lines = [
            line for line in lines if self.ANSWER_PATTERN.match(line.strip())
        ]

        if not choice_lines:
            raise ValidationError(
                f"Question {question_num}: No answer choices found. "
                "Answer choices must be in format: a) Text or *a) Correct answer"
            )

        # Validate answer choice format
        letters = []
        correct_count = 0
        for line in choice_lines:
            match = self.ANSWER_PATTERN.match(line.strip())
            if match:
                is_correct, letter, text = match.groups()
                letters.append(letter)
                if is_correct:
                    correct_count += 1
                if not text.strip():
                    raise ValidationError(
                        f"Question {question_num}: "
                        f"Empty answer choice text for '{letter})'"
                    )

        # Check for sequential letters
        expected_letters = [chr(ord("a") + i) for i in range(len(letters))]
        if letters != expected_letters:
            raise ValidationError(
                f"Question {question_num}: "
                "Answer letters must be sequential (a, b, c, ...). "
                f"Found: {', '.join(letters)}"
            )

        # Check for correct answer
        if correct_count == 0:
            raise ValidationError(
                f"Question {question_num}: No correct answer specified. "
                "Mark correct answer with * (e.g., *c) Correct answer)"
            )

        # Type-specific validation
        if question_type == "true_false":
            if len(letters) != 2:
                raise ValidationError(
                    f"Question {question_num}: "
                    f"True/False questions must have exactly 2 choices, "
                    f"found {len(letters)}"
                )
        elif question_type == "multiple_choice":
            if len(letters) < 2:
                raise ValidationError(
                    f"Question {question_num}: "
                    f"Multiple choice must have at least 2 choices, "
                    f"found {len(letters)}"
                )
            if correct_count != 1:
                raise ValidationError(
                    f"Question {question_num}: "
                    f"Multiple choice must have exactly 1 correct answer, "
                    f"found {correct_count}"
                )
