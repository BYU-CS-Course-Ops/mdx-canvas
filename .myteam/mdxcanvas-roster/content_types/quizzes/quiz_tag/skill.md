# `<quiz>` Tag

The `<quiz>` tag defines a quiz in the course. It supports various attributes for settings like availability, time
limits, attempts, and access codes.

## Attributes

| Attribute                   | Required | Description                                                         |
|-----------------------------|----------|---------------------------------------------------------------------|
| `title`                     | yes      | Quiz title shown in Canvas                                          |
| `id`                        | no       | Stable identifier; defaults to `title`                              |
| `due_at`                    | no       | Due date: `MMM d, yyyy, h:mm AM/PM`                                 |
| `available_from`            | no       | Date when quiz becomes available                                    |
| `available_to`              | no       | Date when quiz closes                                               |
| `assignment_group`          | no       | Grade category name                                                 |
| `shuffle_answers`           | no       | `"true"` to randomize answer order per student                      |
| `time_limit`                | no       | Time limit in minutes; omit for no limit                            |
| `allowed_attempts`          | no       | Number of attempts; `-1` for unlimited                              |
| `scoring_policy`            | no       | `keep_highest` (default), `keep_latest`, `keep_average`             |
| `access_code`               | no       | Passcode students must enter to access the quiz                     |
| `quiz_type`                 | no       | `assignment` (default), `practice_quiz`, `graded_survey`            |
| `points_possible`           | no       | Total points; if omitted, calculated from question points           |
| `show_correct_answers_at`   | no       | Date when correct answers become visible: `MMM d, yyyy, h:mm AM/PM` |
| `only_visible_to_overrides` | no       | `"True"` — hide quiz from students not in an `<override>` section   |

### `id`

Use an explicit `id` when you need to rename the quiz later without creating a new resource. `id` will become required
in a future version; add it now when you touch a resource.

```xml
<quiz id="midterm_exam" title="Midterm Exam">
    ...
</quiz>
```

**When modifying a resource with no `id`:** first add `id` equal to the current `title` value and keep `title`
unchanged, then make your other edits. Changing `title` without an `id` creates a new resource instead of updating the
existing one.

### `shuffle_answers`

```xml
<quiz title="Quiz 1" shuffle_answers="true">
    ...
</quiz>
```

### `time_limit`

```xml
<quiz title="Quiz 1" time_limit="30">
    ...
</quiz>
```

### `allowed_attempts`

```xml
<quiz title="Quiz 1" allowed_attempts="3">
    ...
</quiz>
```

Use `-1` for unlimited attempts.

### `access_code`

```xml
<quiz title="Quiz 1" access_code="secure123">
    ...
</quiz>
```

### `quiz_type`

```xml
<quiz title="Practice Quiz" quiz_type="practice_quiz">
    ...
</quiz>
```

### `scoring_policy`

```xml
<quiz title="Quiz 1" allowed_attempts="3" scoring_policy="keep_highest">
    ...
</quiz>
```

### `show_correct_answers_at`

```xml
<quiz title="Quiz 1" show_correct_answers_at="Jan 20, 2025, 12:00 PM">
    ...
</quiz>
```

### `only_visible_to_overrides`

Hides the quiz from students who are not in any `<override>` section. Useful for password-locked quizzes that only
specific sections should see.

```xml
<quiz title="Lecture 3a Quiz"
      access_code="bit-is-cool"
      only_visible_to_overrides="True">
    <overrides>
        <override section_id="34280" due_at="Jan 13, 2026, 11:59 PM"/>
    </overrides>
    ...
</quiz>
```

## Children

### `<description>`

Optional instructions shown to students before they start. Supports Markdown or HTML.

```xml
<description>
    # Welcome to the Quiz

    Please read all instructions before starting.
</description>
```

### `<questions>` (required)

Contains one or more `<question>` tags. See `../quiz_questions/skill.md` for all supported question types.

## Section-Specific Dates

Use `<overrides>` to set different due dates per course section:

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

## Full Example

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
