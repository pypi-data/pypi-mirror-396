# Quiz Syntax Guide - How to Write Questions

This guide explains how to write quiz questions in the text format that can be converted to Canvas QTI format.

## Table of Contents
1. [File Structure](#file-structure)
2. [YAML Front Matter](#yaml-front-matter)
3. [Question Format](#question-format)
4. [Question Types](#question-types)
5. [Examples](#examples)
6. [Tips and Best Practices](#tips-and-best-practices)

---

## File Structure

A quiz file consists of two main parts:

```
YAML Front Matter (optional but recommended)
↓
Blank line
↓
Questions
```

### Example Structure
```
---
title: My Quiz Title
description: Quiz description
points_per_question: 1
---

## Question 1
[Type: multiple_choice]
...content...

## Question 2
[Type: true_false]
...content...
```

---

## YAML Front Matter

The YAML front matter goes at the **very beginning** of the file, between `---` markers.

### Available Metadata Fields

| Field | Required | Type | Default | Description |
|-------|----------|------|---------|-------------|
| `title` | No | Text | "Untitled Quiz" | Quiz title that appears in Canvas |
| `description` | No | Text | (empty) | Quiz description (supports HTML) |
| `points_per_question` | No | Number | 1 | Default points for all questions |
| `shuffle_answers` | No | true/false | false | Randomize answer order in Canvas |

### Valid Front Matter Example
```yaml
---
title: Introduction to Biology
description: Chapter 3 assessment covering cell biology
points_per_question: 2
shuffle_answers: true
---
```

### Minimal Front Matter
```yaml
---
title: Quick Quiz
---
```

### No Front Matter
If you omit the front matter, defaults are used:
```
## Question 1
[Type: multiple_choice]
...
```

---

## Question Format

Each question must follow this exact structure:

```
## Question N
[Type: question_type]

Question text here?

a) First answer choice
b) Second answer choice
*c) Correct answer (marked with *)
d) Another answer choice

Feedback: This is shown after answering (optional)
```

### Required Elements

1. **Question Header**
   - Must start with `## Question` followed by a number
   - Format: `## Question 1`, `## Question 2`, etc.
   - Numbers must be sequential (1, 2, 3...)

2. **Question Type**
   - Format: `[Type: type_name]`
   - Must be on its own line
   - Supported types: `multiple_choice`, `true_false`

3. **Blank Line**
   - Required after `[Type: ...]`
   - Separates metadata from question content

4. **Question Text**
   - The actual question (can be multiple lines)
   - Should end with a question mark
   - Can include formatting (see tips below)

5. **Blank Line**
   - Required after question text
   - Separates question from answer choices

6. **Answer Choices**
   - Format: `a) Choice text`, `b) Choice text`, etc.
   - Must be sequential (a, b, c, d...)
   - At least one choice must be marked correct with `*`
   - Exactly one choice must be correct for multiple choice
   - Exactly one choice must be correct for true/false

### Optional Elements

- **Feedback**
  - Format: `Feedback: Your feedback text here`
  - Shows to students after they answer
  - Optional but recommended

---

## Question Types

### 1. Multiple Choice

- **Type Code:** `multiple_choice`
- **Requirements:**
  - Minimum 2 choices
  - Maximum unlimited choices
  - Exactly 1 correct answer
- **Example:**
```
## Question 1
[Type: multiple_choice]

What is the capital of France?

a) London
b) Berlin
*c) Paris
d) Madrid
e) Amsterdam

Feedback: Paris is the capital and largest city of France.
```

### 2. True/False

- **Type Code:** `true_false`
- **Requirements:**
  - Exactly 2 choices (True and False)
  - Exactly 1 correct answer
  - First choice is typically "True", second is "False"
- **Example:**
```
## Question 2
[Type: true_false]

The Earth orbits around the Sun.

*a) True
b) False

Feedback: Yes, the Earth's orbit takes approximately 365.25 days.
```

---

## Examples

### Complete Quiz with All Features

```yaml
---
title: Biology Chapter 3 Assessment
description: Test your knowledge of cell biology
points_per_question: 1
shuffle_answers: true
---

## Question 1
[Type: multiple_choice]

Which organelle is responsible for producing energy in a cell?

a) Nucleus
b) Golgi apparatus
*c) Mitochondrion
d) Endoplasmic reticulum

Feedback: The mitochondrion is often called the "powerhouse" of the cell because it produces ATP through cellular respiration.

## Question 2
[Type: true_false]

Prokaryotic cells have a membrane-bound nucleus.

a) True
*b) False

Feedback: Prokaryotic cells lack a nucleus and other membrane-bound organelles. Only eukaryotic cells have a nucleus.

## Question 3
[Type: multiple_choice]

Which of the following is NOT a component of the cell membrane?

a) Phospholipid bilayer
*b) Cellulose fiber
c) Cholesterol
d) Proteins

Feedback: Cellulose is found in plant cell walls, not in cell membranes. Cell membranes contain phospholipids, cholesterol, and proteins.
```

### Minimal Quiz (No Metadata)

```
## Question 1
[Type: multiple_choice]

2 + 2 = ?

a) 3
*b) 4
c) 5
d) 6

## Question 2
[Type: true_false]

Water boils at 100°C at sea level.

*a) True
b) False
```

---

## Tips and Best Practices

### 1. Question Text Formatting
- Use **bold** with `**text**` or `__text__`
- Use *italic* with `*text*` or `_text_`
- Code formatting with backticks: `` `code` ``
- Line breaks work normally within question text

### 2. Multiple Line Questions
Question text can span multiple lines:
```
## Question 1
[Type: multiple_choice]

This is a longer question that spans
multiple lines. It's perfectly fine to
break it up for readability.

a) Choice 1
*b) Choice 2
```

### 3. Consistent Spacing
- Always use blank lines as separators
- Blank line after `[Type: ...]`
- Blank line after question text
- No blank lines between answer choices

### 4. Marking Correct Answers
- Prefix with `*` directly (no space): `*c) Correct answer`
- Only ONE answer per question can have `*`
- The `*` must be at the very beginning

### 5. Custom Points
You can override the default points for a specific question:
```
## Question 1
[Type: multiple_choice]
[Points: 5]

Question text?

a) Choice A
*b) Choice B
```

### 6. Custom Question IDs
You can assign custom IDs to questions:
```
## Question 1
[Type: multiple_choice]
[ID: my_question_1]

Question text?

a) Choice A
*b) Choice B
```

### 7. Feedback Best Practices
- Keep feedback concise (1-3 sentences)
- Explain why the correct answer is right
- Use feedback to reinforce learning
- Optional but highly recommended

### 8. Question Numbering
- Questions must be numbered sequentially: 1, 2, 3, 4...
- Non-sequential numbers will cause an error
- Always start at Question 1

### 9. Common Mistakes to Avoid

❌ **Wrong - No blank line after type**
```
## Question 1
[Type: multiple_choice]
What is 2+2?
```

✅ **Correct**
```
## Question 1
[Type: multiple_choice]

What is 2+2?
```

---

❌ **Wrong - Multiple correct answers**
```
## Question 1
[Type: multiple_choice]

Which are primary colors?

*a) Red
*b) Blue
c) Green
```

✅ **Correct (for multiple choice)**
```
## Question 1
[Type: multiple_choice]

Which is a primary color?

*a) Red
b) Blue
c) Green
```

---

❌ **Wrong - Non-sequential answer choices**
```
## Question 1
[Type: multiple_choice]

Question?

a) Choice A
c) Choice C
d) Choice D
```

✅ **Correct**
```
## Question 1
[Type: multiple_choice]

Question?

a) Choice A
b) Choice B
c) Choice C
```

---

❌ **Wrong - True/False with non-binary choices**
```
## Question 1
[Type: true_false]

Question?

a) Yes
b) No
c) Maybe
```

✅ **Correct**
```
## Question 1
[Type: true_false]

Question?

*a) True
b) False
```

---

## Validation

Before converting to Canvas format, validate your quiz file:

```bash
python -m text_to_qti validate quiz_file.txt
```

Output will tell you if there are any syntax errors.

## Conversion

Convert your validated quiz to Canvas QTI format:

```bash
python -m text_to_qti convert quiz_file.txt -o output.zip
```

The output ZIP file can be imported directly into Canvas.

---

## Quick Reference

### Question Type Codes
- `multiple_choice` - Multiple choice question
- `true_false` - True/False question

### Metadata Fields
```yaml
title: Quiz Title
description: Quiz description
points_per_question: 1
shuffle_answers: true
```

### Question Metadata
```
[Type: multiple_choice]    # Required
[Points: 2]                # Optional (overrides default)
[ID: custom_id]            # Optional (auto-generated if not provided)
```

### Answer Format
- `a) Text` - Regular choice
- `*a) Text` - Correct choice (exactly ONE per question)

---

## Need Help?

- **Validation errors?** Run the validate command and read the error message
- **Syntax unsure?** Compare with examples in this guide
- **Still stuck?** Check that you have:
  - Required blank lines
  - Sequential answer choices (a, b, c...)
  - Exactly one correct answer marked with `*`
  - Sequential question numbers (1, 2, 3...)
