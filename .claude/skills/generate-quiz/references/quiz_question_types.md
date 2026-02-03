# `<question>` Types

The `<question>` tag is used within the `<questions>` section of a `<quiz>` to define individual quiz questions.

Each question has a `type` attribute and may include one or more child tags (e.g., `<correct>`, `<incorrect>`, `<pair>`). The content body is treated as the question prompt.

## Question Types

### `text`

Displays a block of instructional or contextual text. It does not require an answer.

```xml
<question type="text">
    This is a text question that provides instructions for the following questions.
</question>
```

### `true-false`

Presents a True/False question. Requires the `answer` attribute (`true` or `false`).

```xml
<question type="true-false" answer="true">
    Is the sky blue?
</question>
```

### `multiple-choice`

Creates a single-answer multiple-choice question. Requires at least one `<correct>` and one or more `<incorrect>` options.

```xml
<question type="multiple-choice">
    What is the capital of France?

    <correct>Paris</correct>
    <incorrect>London</incorrect>
    <incorrect>Berlin</incorrect>
    <incorrect>Madrid</incorrect>
</question>
```

### `multiple-answers`

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

### `matching`

Requires students to match items from two columns. Use `<pair>` for correct matches and optionally `<distractors>`.

```xml
<question type="matching">
    Match the following countries with their capitals.

    <pair left="France" right="Paris" />
    <pair left="Germany" right="Berlin" />
    <pair left="Spain" right="Madrid" />

    <distractors>
        London
        Rome
        Lisbon
    </distractors>
</question>
```

### `multiple-tf`

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

### `fill-in-the-blank`

Creates a single blank the student must fill in. Use `[blank]` in the sentence and `<correct text="..." />` to define valid answers.

```xml
<question type="fill-in-the-blank">
    The capital of France is [blank].

    <correct text="Paris" />
</question>
```

### `fill-in-multiple-blanks`

Creates multiple blanks identified by name (e.g., `[stars]`). Each `<correct>` must define the matching `blank`.

```xml
<question type="fill-in-multiple-blanks">
    The U.S. flag has [stripes] stripes and [stars] stars.

    <correct text="13" blank="stripes" />
    <correct text="50" blank="stars" />
</question>
```

### `fill-in-multiple-blanks-filled-answers`

A shorthand variation of the previous format where correct answers are embedded directly.

```xml
<question type="fill-in-multiple-blanks-filled-answers">
    The U.S. flag has [[13]] stripes and [[50]] stars.
</question>
```

### `essay`

Accepts an open-ended text response. No `answer` or child tags are required.

```xml
<question type="essay">
    Discuss the impact of technology on modern education.
</question>
```

### `file-upload`

Prompts the student to upload a file as their response.

```xml
<question type="file-upload">
    Upload your project files for review.
</question>
```

### `numerical`

Accepts a numerical answer and supports three modes via `numerical_answer_type`:

#### 1. Exact Answer

```xml
<question type="numerical" numerical_answer_type="exact">
    What is π?

    <correct answer_exact="3.14159" answer_error_margin="0.0001" />
</question>
```

#### 2. Range Answer

```xml
<question type="numerical" numerical_answer_type="range">
    Give a value for x such that 1 ≤ x ≤ 10.

    <correct answer_range_start="1" answer_range_end="10" />
</question>
```

#### 3. Precision Answer

```xml
<question type="numerical" numerical_answer_type="precision">
    What is the value of π?

    <correct answer_approximate="3.14159" answer_precision="5" />
</question>
```
