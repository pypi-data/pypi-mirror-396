# Quick Start - Write Quiz Questions in 5 Minutes

## Basic Template

```yaml
---
title: Your Quiz Title
description: Optional description
points_per_question: 1
---

## Question 1
[Type: multiple_choice]

Your question text here?

a) Choice A
b) Choice B
*c) Correct Choice
d) Choice D

Feedback: Explanation here (optional)

## Question 2
[Type: true_false]

Your statement here.

*a) True
b) False

Feedback: Explanation here (optional)
```

## Copy-Paste Templates

### Multiple Choice Template
```
## Question X
[Type: multiple_choice]

What is your question?

a) Option 1
b) Option 2
*c) Correct Option
d) Option 4

Feedback: Why this is correct.
```

### True/False Template
```
## Question X
[Type: true_false]

Your statement here.

*a) True
b) False

Feedback: Explanation of the answer.
```

## Key Rules

| Rule | Example | ❌ Wrong |
|------|---------|---------|
| Blank line after `[Type: ...]` | `[Type: ...]\n\nQuestion?` | `[Type: ...]\nQuestion?` |
| Mark correct with `*` at start | `*c) Correct` | `c) Correct*` |
| Sequential letters (a, b, c...) | a, b, c, d | a, c, d, e |
| Sequential questions (1, 2, 3...) | Question 1, 2, 3 | Question 1, 2, 4 |
| Exactly 1 correct answer | `*a) Yes\nb) No` | `*a) Yes\n*b) Also Yes` |
| True/False = 2 choices | `*a) True\nb) False` | `a) True\nb) False\nc) Maybe` |
| Blank line between sections | After type, after question | No gaps |

## Metadata Options

```yaml
---
title: Quiz Title              # Required (default: "Untitled Quiz")
description: Short desc        # Optional
points_per_question: 1         # Optional (default: 1)
shuffle_answers: true          # Optional (default: false)
---
```

## Question Metadata Options

```
[Type: multiple_choice]        # Required
[Points: 5]                    # Optional (overrides default)
[ID: unique_id]                # Optional (auto-generated)
```

## Common Mistakes & Fixes

### ❌ No blank line after type
```
## Question 1
[Type: multiple_choice]
What is 2+2?
```
✅ **Fix:** Add blank line after `[Type: ...]`

### ❌ Correct answer not marked
```
a) Choice 1
b) Choice 2
c) Choice 3
```
✅ **Fix:** Mark correct answer: `*c) Choice 3`

### ❌ Wrong answer format
```
c) * Correct answer
[*] Multiple choice
```
✅ **Fix:** `*c) Correct answer` (asterisk at the very start)

### ❌ Non-sequential choices
```
a) Choice
c) Choice
d) Choice
```
✅ **Fix:** Use a, b, c, d (no gaps)

## Validation & Conversion

```bash
# Check syntax
python -m text_to_qti validate my_quiz.txt

# Convert to Canvas
python -m text_to_qti convert my_quiz.txt -o quiz.zip
```

## Real Example

```yaml
---
title: Biology Quiz
description: Chapter 5 Assessment
points_per_question: 1
---

## Question 1
[Type: multiple_choice]

What is the powerhouse of the cell?

a) Nucleus
b) Ribosome
*c) Mitochondrion
d) Golgi apparatus

Feedback: Mitochondria produce ATP through cellular respiration.

## Question 2
[Type: true_false]

Photosynthesis occurs in animal cells.

a) True
*b) False

Feedback: Only plant cells and some protists perform photosynthesis.

## Question 3
[Type: multiple_choice]

Which organelle packages proteins?

a) Rough ER
*b) Golgi apparatus
c) Smooth ER
d) Mitochondrion

Feedback: The Golgi apparatus modifies and packages proteins for export.
```

## Answer Key

For the example above:
- Q1: C (Mitochondrion)
- Q2: B (False)
- Q3: B (Golgi apparatus)

## Pro Tips

✨ **Tip 1:** Use Markdown formatting in questions
```
## Question 1
[Type: multiple_choice]

What does **photosynthesis** produce?

*a) Glucose and oxygen
b) CO2 and water
```

✨ **Tip 2:** Multi-line questions are fine
```
## Question 1
[Type: multiple_choice]

Consider the following formula:
E = mc²

What does this represent?

*a) Einstein's mass-energy equivalence
b) Electron energy states
```

✨ **Tip 3:** Always include feedback for learning
```
Feedback: This helps students understand why the answer is correct
```

✨ **Tip 4:** Custom points per question
```
## Question 1
[Type: multiple_choice]
[Points: 5]

Worth 5 points, not the default 1.
```

## Checklist Before Uploading

- [ ] Each question has a type: `[Type: ...]`
- [ ] Exactly one answer marked with `*`
- [ ] Answer choices are sequential (a, b, c...)
- [ ] Questions are numbered sequentially (1, 2, 3...)
- [ ] Blank lines separate sections
- [ ] Validation passes: `python -m text_to_qti validate file.txt`
- [ ] Quiz converts successfully: `python -m text_to_qti convert file.txt -o output.zip`

---

**For detailed documentation, see QUIZ_SYNTAX_GUIDE.md**
