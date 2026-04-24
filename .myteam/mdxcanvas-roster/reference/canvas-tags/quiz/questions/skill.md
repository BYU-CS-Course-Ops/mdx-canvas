---
id: canvas-tags-quiz-questions
description: Syntax and examples for all 12 MDXCanvas question types.
---

# `<question>` Types

## When to Use This Reference

Use this reference when working with:

- Writing any quiz question
- Choosing between question types (multiple-choice, matching, fill-in, numerical, etc.)
- Setting per-question point values
- Using `id` on questions generated in a loop

## Non-Negotiables

- Always set a `type` attribute on every `<question>` tag.
- Use `<correct>` and `<incorrect>` tags exactly as shown for each type — structure varies by type.
- Use `id` on questions generated programmatically so they can be updated without duplication.

---

## Common Question Attributes

These attributes apply to any question type:

| Attribute         | Required | Description                                                                     |
|-------------------|----------|---------------------------------------------------------------------------------|
| `type`            | yes      | Question type (see sections below)                                              |
| `id`              | no       | Stable identifier for the question (useful when generating questions in a loop) |
| `points_possible` | no       | Points for this question; also accepted as `points`                             |

### `id`

Assign a stable ID when generating questions programmatically or referencing them elsewhere:

```xml
<question type="essay" id="midterm-q0">
    What is a large language model?
</question>
```

### `points_possible` / `points`

Override the default point value per question. Use `points="0"` for checklist-style questions that carry no grade
weight:

```xml
<!-- Worth 0 points — used as a checklist -->
<question type="multiple-answers" points="0">
    Project checklist:
    <correct>I completed the baseline requirements</correct>
    <correct>I pushed my code to GitHub</correct>
</question>

<!-- Custom point value -->
<question type="essay" points_possible="3">
    Estimate your hours worked this week.
</question>
```

---

## `text`

Displays a block of instructional or contextual text. Does not require an answer.

```xml
<question type="text">
    This is a text question that provides instructions for the following questions.
</question>
```

---

## `true-false`

Presents a True/False question. Requires the `answer` attribute (`true` or `false`).

```xml
<question type="true-false" answer="true">
    Is the sky blue?
</question>
```

---

## `multiple-choice`

Single-answer multiple choice. Requires at least one `<correct>` and one or more `<incorrect>` options.

```xml
<question type="multiple-choice">
    What is the capital of France?

    <correct>Paris</correct>
    <incorrect>London</incorrect>
    <incorrect>Berlin</incorrect>
    <incorrect>Madrid</incorrect>
</question>
```

---

## `multiple-answers`

Allows selection of multiple correct answers.

```xml
<question type="multiple-answers">
    Which of the following are programming languages?

    <correct>Python</correct>
    <correct>JavaScript</correct>
    <incorrect>HTML</incorrect>
    <incorrect>CSS</incorrect>
</question>
```

---

## `matching`

Students match items from two columns. Use `<pair>` for correct matches and optionally `<distractors>` for extra
wrong-side items.

```xml
<question type="matching">
    Match the following countries with their capitals.

    <pair left="France" right="Paris"/>
    <pair left="Germany" right="Berlin"/>
    <pair left="Spain" right="Madrid"/>

    <distractors>
        London
        Rome
        Lisbon
    </distractors>
</question>
```

---

## `multiple-tf`

Presents multiple True/False statements. Students select which are true.

```xml
<question type="multiple-tf">
    Which of the following statements are true?

    <correct>Python is a programming language.</correct>
    <incorrect>HTML is a programming language.</incorrect>
    <correct>JavaScript can be used for web development.</correct>
    <incorrect>CSS is a programming language.</incorrect>
</question>
```

---

## `fill-in-the-blank`

A single blank the student must fill in. Use `[blank]` in the sentence and `<correct text="..." />` for valid answers.

```xml
<question type="fill-in-the-blank">
    The capital of France is [blank].

    <correct text="Paris"/>
</question>
```

---

## `fill-in-multiple-blanks`

Multiple named blanks. Each `<correct>` must specify the matching `blank` name.

```xml
<question type="fill-in-multiple-blanks">
    The U.S. flag has [stripes] stripes and [stars] stars.

    <correct text="13" blank="stripes"/>
    <correct text="50" blank="stars"/>
</question>
```

---

## `fill-in-multiple-blanks-filled-answers`

Shorthand: embed correct answers directly using `[[answer]]` syntax.

```xml
<question type="fill-in-multiple-blanks-filled-answers">
    The U.S. flag has [[13]] stripes and [[50]] stars.
</question>
```

---

## `essay`

Open-ended text response. No `answer` or child tags required.

```xml
<question type="essay">
    Discuss the impact of technology on modern education.
</question>
```

---

## `file-upload`

Prompts the student to upload a file as their response.

```xml
<question type="file-upload">
    Upload your project files for review.
</question>
```

---

## `numerical`

Accepts a numerical answer. Supports three modes via `numerical_answer_type`.

### Exact Answer

```xml
<question type="numerical" numerical_answer_type="exact">
    What is π?

    <correct answer_exact="3.14159" answer_error_margin="0.0001"/>
</question>
```

### Range Answer

```xml
<question type="numerical" numerical_answer_type="range">
    Give a value for x such that 1 ≤ x ≤ 10.

    <correct answer_range_start="1" answer_range_end="10"/>
</question>
```

### Precision Answer

```xml
<question type="numerical" numerical_answer_type="precision">
    What is the value of π?

    <correct answer_approximate="3.14159" answer_precision="5"/>
</question>
```
