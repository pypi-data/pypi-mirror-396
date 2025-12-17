# Example Quiz Files

This directory contains example quiz files to help you get started with the Text-to-QTI converter.

## simple_quiz.txt

A 5-question quiz about Python basics covering:
- Multiple choice questions
- True/false questions
- Custom points per question
- Feedback for each question
- Shuffled answer choices

### Usage

```bash
text-to-qti convert simple_quiz.txt -o python_quiz.zip
```

Then import `python_quiz.zip` into Canvas.

## Creating Your Own Quizzes

1. Copy `simple_quiz.txt` as a template
2. Replace the title and description
3. Add your questions following the syntax
4. Run `text-to-qti validate` to check for errors
5. Run `text-to-qti convert` to generate the QTI package

## Tips

- Keep question text concise
- Mark exactly one answer as correct with `*`
- Use `Feedback:` to provide helpful information
- Test in Canvas before using in production
- Use sections (headers) to organize your quiz logically
