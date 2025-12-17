# Contributing to text-to-qti

Thank you for your interest in contributing to text-to-qti! We welcome contributions from everyone, whether it's bug reports, feature requests, documentation improvements, or code changes.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:

1. **Description**: Clear description of what isn't working
2. **Steps to reproduce**: Exact steps to reproduce the issue
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: Your OS, Python version, and how you installed text-to-qti
6. **Quiz file example** (if applicable): A minimal `.txt` file that triggers the bug

### Suggesting Features

We'd love to hear your ideas! When suggesting a feature:

1. **Use case**: Explain why this feature would be useful
2. **Expected behavior**: Describe how you'd like it to work
3. **Examples**: Provide examples or use cases
4. **Alternatives**: Suggest alternatives you've considered

### Code Contributions

#### Setup Development Environment

1. **Fork the repository** on GitHub
   ```bash
   # Click "Fork" on https://github.com/tableaprogramming-rgb/textmd-to-qti
   ```

2. **Clone your fork locally**
   ```bash
   git clone https://github.com/YOUR_USERNAME/textmd-to-qti.git
   cd textmd-to-qti
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

#### Running Tests

Before submitting a PR, make sure all tests pass:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/text_to_qti --cov-report=html

# Run specific test file
pytest tests/test_parser.py

# Run tests matching a pattern
pytest -k "test_multiple_choice"
```

#### Code Style Guidelines

We use **black** for formatting, **ruff** for linting, and **mypy** for type checking.

```bash
# Format code with black
black src/ tests/

# Check linting
ruff check src/ tests/

# Run type checking
mypy src/
```

Before committing, run all checks:

```bash
black src/ tests/ && ruff check src/ tests/ && mypy src/ && pytest
```

#### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, descriptive commit messages
   - Keep commits focused on single concerns
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   pytest                    # Run tests
   pytest --cov            # Check coverage
   black src/ tests/        # Format
   ruff check src/ tests/   # Lint
   mypy src/               # Type check
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**
   - Go to the original repository
   - Click "Compare & pull request"
   - Fill in the PR template with:
     - Description of changes
     - Related issue numbers (if any)
     - Type of change (bugfix/feature/docs/refactor)
     - Testing done
     - Checklist of completion items

### Pull Request Guidelines

When submitting a PR:

- **One feature per PR** - Keep PRs focused on a single feature or fix
- **Tests required** - Add tests for new functionality
- **Documentation** - Update README, docstrings, or guides as needed
- **Changelog** - Note your changes (we'll add to CHANGELOG.md before release)
- **Code style** - Follow the guidelines above (black, ruff, mypy)
- **Commit messages** - Use clear, descriptive messages
  - Good: `Add support for fill-in-the-blank questions`
  - Bad: `fix stuff`, `update code`

### Project Structure

```
text-to-qti/
├── src/text_to_qti/          # Main source code
│   ├── models/               # Pydantic data models
│   ├── parser/               # Quiz file parsing
│   ├── qti/                  # QTI generation
│   ├── packager/             # ZIP packaging
│   └── cli.py                # Command-line interface
├── tests/                    # Test files
├── docs/                     # Documentation
├── TEMPLATE.txt              # Template quiz file
└── pyproject.toml            # Project configuration
```

### Key Concepts

**Pydantic Models** (`src/text_to_qti/models/`):
- Validate quiz structure and questions
- Type-safe data handling
- See `quiz.py`, `question.py`, `answer.py`

**Parser** (`src/text_to_qti/parser/`):
- Reads markdown quiz files
- Validates YAML metadata
- Extracts questions and answers

**QTI Generators** (`src/text_to_qti/qti/`):
- `assessment.py`: Generates assessment XML
- `canvas_metadata.py`: Canvas-specific metadata
- `manifest.py`: Package manifest
- Individual question type generators

**ZIP Packager** (`src/text_to_qti/packager/`):
- Creates Canvas-compatible package structure
- Handles file organization and compression

## Documentation

- **QUICK_START.md**: Fast reference for quiz syntax
- **QUIZ_SYNTAX_GUIDE.md**: Detailed syntax documentation
- **TEMPLATE.txt**: Example quiz file

When adding features, update relevant documentation.

## Testing

We aim for high test coverage. When adding code:

1. **Write tests first** (TDD preferred)
2. **Test both success and failure cases**
3. **Include edge cases**
4. **Verify coverage** with `pytest --cov`

Example test structure:

```python
def test_parse_multiple_choice_question():
    """Test parsing a multiple choice question."""
    content = """## Question 1
[Type: multiple_choice]

What is 2+2?

a) 3
*b) 4
c) 5
"""
    questions = parse_content(content)
    assert len(questions) == 1
    assert questions[0].type == QuestionType.MULTIPLE_CHOICE
    assert questions[0].correct_answer == "b"
```

## Release Process

(For maintainers)

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions automatically publishes to PyPI

## Code of Conduct

Please note that this project is released with a [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

## Questions?

- Check existing issues and discussions
- Ask in a new issue (we're friendly!)
- Review the documentation

Thank you for contributing! 🎉
