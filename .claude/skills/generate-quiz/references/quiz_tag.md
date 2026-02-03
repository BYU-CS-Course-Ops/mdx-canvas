# `<quiz>` Tag

The `<quiz>` tag defines a quiz in the course. It supports various attributes for settings like availability, time limits, attempts, and access codes. Quizzes include a `<description>` and a `<questions>` block that defines individual quiz questions.

## Attributes

The following attributes are supported on the `<quiz>` tag. Several of them are shared with `<assignment>` and behave the same way.

### `title`

Sets the quiz title (required).

```xml
<quiz title="Midterm Exam">
...
</quiz>
```

### `id`

Optional unique identifier for the quiz. If not specified, defaults to the `title` value.

Use an explicit `id` when you need to change the quiz's title later without creating a new resource, or when you want a more stable identifier for referencing.

```xml
<quiz
    id="midterm_exam"
    title="Midterm Exam">
...
</quiz>
```

**Legacy scenario:** If you have an existing quiz without an `id` and want to rename it, add an `id` attribute with the value of the old title before changing the title.

### Shared Assignment Attributes

You may use these assignment-style attributes on quizzes:

- `due_at`
- `available_from`
- `available_to`
- `assignment_group`

See the [`<assignment>` tag documentation](../../../documents/supported_tags/tags/assignment_tag.md) for details on how these attributes work.

### `shuffle_answers`

Set to `"true"` to randomize the order of answer choices for each student.

```xml
<quiz 
    title="Quiz 1" 
    shuffle_answers="true">
...
</quiz>
```

### `time_limit`

Specifies the time limit in minutes. If omitted, the quiz has no time limit.

```xml
<quiz title="Quiz 1" time_limit="30">
...
</quiz>
```

### `allowed_attempts`

Sets how many times a student may attempt the quiz. Use `-1` for unlimited attempts.

```xml
<quiz 
    title="Quiz 1" 
    allowed_attempts="3">
...
</quiz>
```

### `access_code`

Sets a passcode students must enter to access the quiz.

```xml
<quiz
    title="Quiz 1"
    access_code="secure123">
...
</quiz>
```

### `quiz_type`

Specifies the type of quiz. Valid values: `assignment` (default), `practice_quiz`, `graded_survey`.

```xml
<quiz
    title="Practice Quiz"
    quiz_type="practice_quiz">
...
</quiz>
```

### `points_possible`

Sets the total points for the quiz. If omitted, calculated from question points.

```xml
<quiz
    title="Quiz 1"
    points_possible="100">
...
</quiz>
```

### `scoring_policy`

Determines how multiple attempts are scored. Valid values: `keep_highest` (default), `keep_latest`, `keep_average`.

```xml
<quiz
    title="Quiz 1"
    allowed_attempts="3"
    scoring_policy="keep_highest">
...
</quiz>
```

### `show_correct_answers_at`

Date/time when correct answers become visible to students. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<quiz
    title="Quiz 1"
    show_correct_answers_at="Jan 20, 2025, 12:00 PM">
...
</quiz>
```

## Children

### `<description>`

Describes the quiz. Supports Markdown or HTML formatting.

```xml
<description>
    # Welcome to the Quiz

    Please read all instructions before starting.
</description>
```

### `<questions>`

Required. Contains one or more `<question>` tags.

Each question must define a `type` and may include `<correct>`, `<incorrect>`, `<pair>`, and other tags based on the question type.

See [quiz question types](quiz_question_types.md) for full documentation of supported types and examples.

## Section-Specific Dates

You can specify different due dates for different course sections using the `<overrides>` container with `<override>` tags.

```xml
<quiz title="Midterm Exam" due_at="Feb 15, 2025, 11:59 PM">
  <overrides>
    <override section_id="12345" due_at="Feb 20, 2025, 11:59 PM" />
    <override section_id="67890" due_at="Feb 22, 2025, 11:59 PM" />
  </overrides>

  <description>
    Complete the midterm exam...
  </description>

  <questions>
    ...
  </questions>
</quiz>
```

See the [`<override>` tag documentation](override_tag.md) for more details on section-specific dates.

## Example

```xml
<quiz
    title="Example Quiz"
    due_at="Jan 1, 2025, 11:59 PM"
    available_from="Jan 1, 2025, 9:00 AM"
    available_to="Jan 1, 2025, 11:59 PM"
    assignment_group="Quizzes"
    shuffle_answers="true"
    time_limit="30"
    allowed_attempts="3"
    scoring_policy="keep_highest"
    points_possible="100">

    <description>
        This quiz includes various question types.
    </description>

    <questions>
        <question type="true-false" answer="true">
            Is the sky blue?
        </question>

        <question type="multiple-choice">
            What is the capital of France?

            <correct>Paris</correct>
            <incorrect>London</incorrect>
            <incorrect>Berlin</incorrect>
            <incorrect>Madrid</incorrect>
        </question>
    </questions>
</quiz>
```
