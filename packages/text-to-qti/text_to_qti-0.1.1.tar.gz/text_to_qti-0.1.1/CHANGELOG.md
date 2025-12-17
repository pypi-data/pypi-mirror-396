# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nothing yet

## [0.1.1] - 2025-12-15

### Added
- Comprehensive security policy (SECURITY.md)
- Academic citation support (CITATION.cff)
- Authors file documenting contributors including Claude
- Pre-commit configuration for local development

### Improved
- Repository best practices implementation
- PyPI package classifiers for better discoverability
- Python 3.12 and 3.13 testing support
- Dependency version constraints to prevent breaking changes
- GitHub Actions workflows (CodeQL scanning, Dependabot)
- Documentation with Claude attribution

### Fixed
- Author metadata placeholders in package configuration
- Package distribution to include all documentation files
- Type hints support with py.typed marker
- CHANGELOG version tracking
- Rich dependency version constraint to support <15.0.0

### Security
- Added Dependabot for automated dependency updates
- Added CodeQL for code security scanning
- Created security vulnerability reporting policy
- Added CODEOWNERS for automatic review assignment

## [0.1.0] - 2025-12-14

### Initial Release

This is the first public release of text-to-qti.

#### Added
- Complete markdown to QTI conversion pipeline
- Multiple Choice questions (2-4 answer options)
- True/False questions
- YAML front matter support for quiz metadata
  - `title`: Quiz name
  - `description`: Optional quiz description
  - `points_per_question`: Default points per question
  - `shuffle_answers`: Randomize answer order in Canvas
- Per-question metadata
  - `[Type: ...]`: Question type specification
  - `[Points: ...]`: Override default points
  - `[ID: ...]`: Custom question identifier
  - `Feedback: ...`: Optional explanation text
- Comprehensive syntax validation
- Canvas LMS compatibility
  - Common Cartridge v1p1 namespace
  - Proper QTI 1.2 XML structure
  - Assessment metadata file generation
- ZIP package generation for Canvas import
- CLI commands:
  - `validate`: Check quiz syntax without conversion
  - `convert`: Generate QTI package
- Rich CLI output with progress indicators
- Extensive documentation
  - QUICK_START.md: Fast reference guide
  - QUIZ_SYNTAX_GUIDE.md: Detailed syntax documentation
  - TEMPLATE.txt: Ready-to-use template
- Full test suite (57 tests, 95%+ coverage)
- Development setup with black, ruff, mypy, pytest

#### Known Limitations
- QTI 1.2 format only (2.1 support planned)
- No image/media support yet
- No question shuffling within quiz (only answer shuffling)
- No partial credit support
- No essay/free-form response questions
- Multiple Choice limited to 2-4 options
- True/False only (no ranking, matching, etc.)

### Project Setup
- MIT License
- GitHub Actions CI/CD automation
- PyPI package distribution
- Contributing guidelines
- Community Code of Conduct

---

## Release Notes

### How to Report Issues
- Check [GitHub Issues](https://github.com/tableaprogramming-rgb/textmd-to-qti/issues)
- Provide quiz file example and error message
- Include your OS, Python version, and installation method

### How to Suggest Features
- Open a [GitHub Discussion](https://github.com/tableaprogramming-rgb/textmd-to-qti/discussions)
- Describe your use case
- Suggest implementation approach

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for how to:
- Set up development environment
- Run tests
- Submit pull requests
- Follow code style guidelines

---

**Note**: Users will update the version number and dates in this file as new releases are published.
