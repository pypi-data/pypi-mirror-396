# Text-to-QTI Converter

[![Tests](https://github.com/tableaprogramming-rgb/textmd-to-qti/actions/workflows/test.yml/badge.svg)](https://github.com/tableaprogramming-rgb/textmd-to-qti/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/text-to-qti.svg)](https://badge.fury.io/py/text-to-qti)
[![Python Versions](https://img.shields.io/pypi/pyversions/text-to-qti.svg)](https://pypi.org/project/text-to-qti/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Built with Claude](https://img.shields.io/badge/Built%20with-Claude-5A67D8?logo=anthropic)](https://claude.ai)

Convert markdown-based quiz files to QTI format for Canvas LMS import.

## Overview

Text-to-QTI is a Python CLI tool that converts simple markdown quiz files into QTI (Question and Test Interoperability) packages compatible with Canvas LMS. It supports multiple choice and true/false questions with optional feedback.

## Features

- 📝 Simple markdown syntax for quiz authoring
- ✅ Pre-parsing syntax validation with helpful error messages
- 🎯 Support for Multiple Choice and True/False questions
- 📦 Canvas-compatible QTI 1.2 ZIP package generation
- 🔧 Extensible architecture for adding new question types
- 🎨 Colorful CLI with progress indicators
- 📊 Configurable metadata (title, description, points, shuffle)

## Installation

### From PyPI (Recommended)

```bash
pip install text-to-qti
```

### From GitHub

```bash
pip install git+https://github.com/tableaprogramming-rgb/textmd-to-qti.git
```

### From Source (Development)

```bash
git clone https://github.com/tableaprogramming-rgb/textmd-to-qti.git
cd textmd-to-qti
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### Requirements

- Python 3.8+
- lxml
- pydantic
- click
- rich
- markdown
- PyYAML

## Quick Start

### 1. Create a Quiz File

Create a file `quiz.txt`:

```markdown
---
title: My First Quiz
description: A simple quiz about geography
points_per_question: 1
shuffle_answers: false
---

## Question 1
[Type: multiple_choice]

What is the capital of France?

a) London
b) Berlin
*c) Paris
d) Madrid

Feedback: Paris is the capital and largest city of France.

## Question 2
[Type: true_false]

The Earth is flat.

*a) False
b) True

Feedback: The Earth is an oblate spheroid.
```

### 2. Validate (Optional)

```bash
text-to-qti validate quiz.txt
```

### 3. Convert to QTI

```bash
text-to-qti convert quiz.txt -o quiz.zip
```

### 4. Import to Canvas

1. Go to your Canvas course
2. Navigate to **Quizzes**
3. Click **Import Existing Content**
4. Select **QTI .zip file**
5. Upload `quiz.zip`

## Syntax Guide

### File Structure

Every quiz file has:
1. **Optional YAML front matter** with metadata
2. **Section headers** (optional) for organization
3. **Questions** with metadata and answer choices

### YAML Front Matter

```yaml
---
title: Quiz Title (required)
description: Optional description
points_per_question: 1 (default)
shuffle_answers: false (default)
---
```

### Question Format

```markdown
## Question N
[Type: question_type]
[Points: number]
[ID: custom_id]

Question text here.

a) Answer choice 1
b) Answer choice 2
*c) Correct answer
d) Answer choice 4

Feedback: Optional feedback shown after answering.
```

### Metadata Tags

- `[Type: multiple_choice]` or `[Type: true_false]` (**required**)
- `[Points: number]` - Points for this question (default: from metadata)
- `[ID: custom_id]` - Custom question ID (default: auto-generated)
- `Feedback:` - Feedback text shown after answering (optional)

### Answer Choices

- Each choice starts with a letter: `a)`, `b)`, `c)`, etc.
- Letters must be sequential
- Exactly one answer must be marked as correct with `*`
  - `*a) Correct answer`
  - `b) Wrong answer`
- For True/False: must have exactly 2 choices

### Text Formatting

Question text supports markdown:

```markdown
## Question 1
[Type: multiple_choice]

This is **bold** text and *italic* text.

You can use `inline code` or [links](https://example.com).

a) First choice
*b) Correct choice
```

### Comments

HTML comments are ignored:

```markdown
<!-- This comment will be ignored -->

## Question 1
[Type: multiple_choice]
```

## CLI Commands

### Convert Command

```bash
text-to-qti convert INPUT_FILE [OPTIONS]

Options:
  -o, --output PATH         Output ZIP file path (default: output.zip)
  --validate-only          Only validate syntax, don't generate
  --qti-version {1.2,2.1}  QTI version (default: 1.2)
```

### Validate Command

```bash
text-to-qti validate INPUT_FILE

Validates syntax without generating QTI.
```

## Examples

### Simple Multiple Choice

```markdown
---
title: Basic Math Quiz
---

## Question 1
[Type: multiple_choice]

What is 2 + 2?

a) 3
*b) 4
c) 5
```

### True/False with Custom Points

```markdown
---
title: Science Quiz
points_per_question: 2
---

## Question 1
[Type: true_false]
[Points: 5]

Photosynthesis requires sunlight.

*a) True
b) False

Feedback: Photosynthesis is the process plants use to convert light energy into chemical energy.
```

### Mixed Question Types

```markdown
---
title: Comprehensive Quiz
description: Tests various knowledge areas
points_per_question: 1
---

# Section 1: Multiple Choice

## Question 1
[Type: multiple_choice]

What programming language is known for web development?

a) Python
b) Go
*c) JavaScript
d) Rust

## Question 2
[Type: multiple_choice]

Which is NOT a relational database?

a) PostgreSQL
b) MySQL
c) Oracle
*d) MongoDB

# Section 2: True/False

## Question 3
[Type: true_false]

Git is a distributed version control system.

*a) True
b) False

## Question 4
[Type: true_false]

REST APIs always use JSON.

a) True
*b) False
```

## Error Messages

The validator provides helpful error messages:

```
ERROR: Line 15: Question 1: No correct answer specified.
  Mark correct answer with * (e.g., *c) Correct answer)

ERROR: Line 20: Question 2: Answer letters must be sequential (a, b, c, ...).
  Found: a, c

ERROR: Line 25: Question 3: True/False questions must have exactly 2 choices, found 3
```

## Canvas Import Guide

1. **Prepare your quiz file** - Use the syntax guide above
2. **Validate** - Run `text-to-qti validate quiz.txt` to check for errors
3. **Convert** - Run `text-to-qti convert quiz.txt` to create `output.zip`
4. **Import to Canvas:**
   - Go to your course
   - Click **Settings** → **Import Existing Content**
   - Select **QTI .zip file**
   - Upload the ZIP file
   - Review the imported quiz in your question bank or quizzes

## Architecture

The project is designed with extensibility in mind:

```
Input Text File
      ↓
   [Parser] ──→ Validates & parses markdown
      ↓
[Question Models] ──→ Pydantic validated data
      ↓
[Item Generators] ──→ Pluggable generators per question type
      ↓
[QTI XML Builders] ──→ Creates assessment & manifest
      ↓
[ZIP Packager] ──→ Creates Canvas-ready package
      ↓
Output QTI ZIP
```

### Adding New Question Types

To add a new question type:

1. Create a new generator class inheriting from `BaseItemGenerator`
2. Implement the `generate()` method
3. Register with the main generator

Example (in your code):

```python
from text_to_qti.qti.base_item import BaseItemGenerator
from text_to_qti.qti.generator import QTIGenerator

class FillInBlankGenerator(BaseItemGenerator):
    def generate(self, question):
        # Custom implementation
        pass

# Use it
generator = QTIGenerator(quiz)
generator.register_item_generator(
    QuestionType.FILL_IN_BLANK,
    FillInBlankGenerator()
)
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest                    # Run all tests
pytest -v               # Verbose output
pytest --cov           # With coverage report
```

### Code Quality

```bash
black src/              # Format code
ruff check src/         # Lint
mypy src/              # Type checking
```

## Limitations

Current MVP limitations (Phase 1):

- Only supports Multiple Choice and True/False questions
- QTI 1.2 format only (2.1 support coming)
- No image/media support yet
- No question shuffling within quiz (only answer shuffling)
- No partial credit support
- No essay/free-form response questions

## Troubleshooting

### "File must be UTF-8 encoded"

Save your quiz file as UTF-8. In most editors:
- VS Code: Click encoding in bottom right, select UTF-8
- Sublime: File → Save with Encoding → UTF-8
- macOS: Use TextEdit → Format → Plain Text, then save

### "No questions found"

Ensure questions start with `## Question N` where N is a number.

### "Invalid question type"

Ensure you use exactly: `[Type: multiple_choice]` or `[Type: true_false]`

### "Answer letters must be sequential"

Answers must be a, b, c, d, etc. in order. You can't skip letters.

## Contributing

Contributions are welcome and appreciated! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Development setup instructions
- How to run tests locally
- Code style guidelines
- How to submit pull requests
- Reporting bugs and suggesting features

## Acknowledgments

This project was made possible with **[Claude](https://claude.ai)**, an AI assistant by Anthropic. Claude contributed significantly to:

- **Architecture Design** - Conceptualized the overall system design for QTI generation
- **Implementation** - Built the complete markdown-to-QTI conversion pipeline
- **Testing** - Developed comprehensive test suite (57 tests, 95%+ coverage)
- **Documentation** - Created all guides, templates, and setup documentation
- **DevOps** - Configured GitHub Actions CI/CD and PyPI publishing automation
- **Best Practices** - Implemented repository standards and security scanning

We're grateful for Claude's essential contributions to making educational technology more accessible.

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:

1. Check the [troubleshooting](#troubleshooting) section
2. Review [examples](#examples) for similar use cases
3. Check existing issues on GitHub
4. Create a new issue with details

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history and release notes.

### Latest Version: 0.1.0 (Initial MVP)

- ✅ Markdown parser with YAML metadata
- ✅ Multiple choice and true/false support
- ✅ Syntax validation with error reporting
- ✅ QTI 1.2 package generation
- ✅ Canvas LMS compatibility
- ✅ CLI with progress indicators
- ✅ Extensible architecture for question types

## Roadmap

### Phase 2 (Coming Soon)

- [ ] Fill-in-the-blank questions
- [ ] Multiple answer questions
- [ ] Image/media support
- [ ] QTI 2.1 format support
- [ ] Quiz import/editing from Canvas

### Phase 3 (Future)

- [ ] Web UI for quiz creation
- [ ] Question bank management
- [ ] CSV/Excel import
- [ ] Question randomization
- [ ] Partial credit support

---

Made with ❤️ for educators
