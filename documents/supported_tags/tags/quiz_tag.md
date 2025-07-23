# `<quiz>` Tag

The `<quiz>` tag defines a quiz in the course. It supports various attributes for settings like availability, time limits, attempts, and access codes. Quizzes include a `<description>` and a `<questions>` block that defines individual quiz questions.

## Attributes

The following attributes are supported on the `<quiz>` tag. Several of them are shared with `<assignment>` and behave the same way.

### Shared Assignment Attributes

You may use these assignment-style attributes on quizzes:

- `title`
- `due_at`
- `available_from`
- `available_to`
- `assignment_group`

See the [assignment tag documentation](assignment_tag.md) for details on how these attributes work.

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
    allowed_attempts="3">

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

---

## See Also

* [`<question>` types](quiz_question_types.md)
* [`<assignment>` tag](assignment_tag.md) for shared quiz attributes