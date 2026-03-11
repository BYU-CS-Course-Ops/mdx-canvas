# Quizzes

## Quiz Overview

The `<quiz>` tag defines a Canvas quiz. A quiz contains two child elements:

- `<description>` — optional instructions shown to students before they begin
- `<questions>` — required; contains one or more `<question>` tags

```xml
<quiz title="Chapter 1 Quiz"
      due_at="Jan 20, 2025, 11:59 PM"
      shuffle_answers="true"
      allowed_attempts="2"
      scoring_policy="keep_highest">

    <description>
        Answer all questions. You have 2 attempts.
    </description>

    <questions>
        <question type="multiple-choice">
            What is 2 + 2?
            <correct>4</correct>
            <incorrect>3</incorrect>
            <incorrect>5</incorrect>
        </question>
    </questions>
</quiz>
```

## Default Settings

When not specified, MDXCanvas quizzes default to:

- `shuffle_answers="true"`
- `allowed_attempts="2"`
- `scoring_policy="keep_highest"`

## Quiz Generation Guidelines

When generating quizzes, aim for varied question types:

- 30–40% multiple-choice
- 20–30% true-false
- 20–30% fill-in-the-blank or matching
- 10–20% multiple-answers or essay (for higher-order thinking)

Distribute questions across the full topic; avoid clustering all questions on one subtopic.

## Quick Example

A minimal working quiz:

```xml
<quiz title="Python Basics Quiz"
      due_at="Jan 15, 2025, 11:59 PM"
      assignment_group="Quizzes"
      shuffle_answers="true"
      allowed_attempts="2"
      scoring_policy="keep_highest">

    <description>
        This quiz covers Python variables, data types, and basic operators.
    </description>

    <questions>
        <question type="true-false" answer="true">
            Python variable names are case-sensitive.
        </question>

        <question type="multiple-choice">
            Which of the following is a valid Python variable name?

            <correct>my_var</correct>
            <incorrect>2myvar</incorrect>
            <incorrect>my-var</incorrect>
            <incorrect>my var</incorrect>
        </question>

        <question type="fill-in-the-blank">
            The result of `type(3.14)` in Python is [blank].

            <correct text="float" />
            <correct text="&lt;class 'float'&gt;" />
        </question>
    </questions>
</quiz>
```

For the complete `<quiz>` attribute reference, see `quiz_tag/skill.md`.

For all question type syntax and examples, see `quiz_questions/skill.md`.
