---
name: mdxcanvas/canvas-resources
description: Reference for all Canvas resource tags in MDXCanvas — quiz, assignment, page, module, syllabus, announcement, and overrides.
license: Complete terms in ../LICENSE.txt
---

# Canvas Resource Tags

These tags define the Canvas resources that MDXCanvas creates or updates. Each tag maps directly to a Canvas API object.

For complete attribute documentation, read the tag files in `documents/supported_tags/tags/`.

## Tag Overview

| Tag                   | Creates             | Key Attributes                                                               |
|-----------------------|---------------------|------------------------------------------------------------------------------|
| `<assignment>`        | Canvas assignment   | `title`, `due_at`, `points_possible`, `assignment_group`, `submission_types` |
| `<quiz>`              | Canvas quiz         | `title`, `due_at`, `shuffle_answers`, `allowed_attempts`, `scoring_policy`   |
| `<page>`              | Canvas page         | `title`, `published`                                                         |
| `<module>`            | Canvas module       | `id`, `title`                                                                |
| `<item>`              | Module item         | `type`, `content_id`, `indent`                                               |
| `<syllabus>`          | Course syllabus     | (no attributes — wraps content)                                              |
| `<announcement>`      | Course announcement | `title`, `published_at`                                                      |
| `<assignment-groups>` | Grade groups        | (contains `<group>` children)                                                |

---

## `<assignment>`

Creates a Canvas assignment. The assignment description goes directly inside the tag (Markdown supported).

```xml

<assignment
        title="Homework 1"
        due_at="Jan 15, 2025, 11:59 PM"
        available_from="Jan 8, 2025, 9:00 AM"
        points_possible="100"
        assignment_group="Homework">

    # Homework 1

    Complete the following exercises and submit via Gradescope.
</assignment>
```

Key attributes: `title` (required), `id`, `due_at`, `available_from`, `available_to`, `late_due`, `points_possible`,
`assignment_group`, `submission_types`, `external_tool_tag_attributes`.

For the complete attribute list, read `documents/supported_tags/tags/assignment_tag.md`.

---

## `<quiz>`

Defines a Canvas quiz with questions. Contains `<description>`, `<questions>`, and optionally `<overrides>`.

```xml

<quiz
        title="Chapter 1 Quiz"
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

Key attributes: `title` (required), `id`, `due_at`, `available_from`, `available_to`, `assignment_group`,
`shuffle_answers`, `time_limit`, `allowed_attempts`, `scoring_policy`, `access_code`, `quiz_type`, `points_possible`,
`show_correct_answers_at`.

For the complete attribute list, read `.claude/skills/mdxcanvas/generate-content/quizzes/references/quiz_tag.md`.

For question types, read `.claude/skills/mdxcanvas/generate-content/quizzes/references/quiz_question_types.md`.

---

## `<page>`

Creates a Canvas content page. Markdown inside the tag becomes the page body.

```xml

<page title="Week 1: Introduction">
    # Welcome to CS 101

    This week we cover the fundamentals of programming.

    ## Topics
    - Variables and data types
    - Control flow
    - Functions
</page>
```

For the complete attribute list, read `documents/supported_tags/tags/page_tag.md`.

---

## `<module>` and `<item>`

`<module>` creates a Canvas module. `<item>` adds content to a module.

```xml

<module id="week-1" title="Week 1: Introduction">
    <item type="page" content_id="Week 1: Introduction" indent="1"/>
    <item type="assignment" content_id="Homework 1" indent="1"/>
    <item type="quiz" content_id="Chapter 1 Quiz" indent="1"/>
    <item type="SubHeader" title="Resources" indent="0"/>
    <item type="ExternalURL" title="Documentation" external_url="https://docs.example.com" indent="1"/>
</module>
```

The `content_id` must match the `title` (or `id`) of the target resource exactly.

`<item>` `type` values: `page`, `assignment`, `quiz`, `SubHeader`, `ExternalURL`, `File`.

For complete documentation, read `documents/supported_tags/tags/module_tag.md` and
`documents/supported_tags/tags/item_tag.md`.

---

## `<syllabus>`

Sets the course syllabus body. Typically uses `<include>` to pull from a Markdown file.

```xml

<syllabus>
    <include path="content/syllabus.md"/>
</syllabus>
```

For complete documentation, read `documents/supported_tags/tags/syllabus_tag.md`.

---

## `<announcement>`

Posts a course-wide announcement.

```xml

<announcement title="Welcome to CS 101!" published_at="Aug 25, 2025, 9:00 AM">
    Welcome everyone! Please read the syllabus before our first class.
</announcement>
```

For complete documentation, read `documents/supported_tags/tags/announcement_tag.md`.

---

## `<assignment-groups>`

Defines Canvas assignment groups with weights for grade calculation.

```xml

<assignment-groups>
    <group name="Homework" weight="40"/>
    <group name="Quizzes" weight="20"/>
    <group name="Projects" weight="30"/>
    <group name="Final Exam" weight="10"/>
</assignment-groups>
```

Groups must be declared before assignments that reference them via `assignment_group`.

---

## `<overrides>`

Applies section-specific due dates to assignments or quizzes. Place inside `<assignment>` or `<quiz>`.

```xml

<assignment title="Homework 1" due_at="Jan 15, 2025, 11:59 PM">
    <overrides>
        <override section_id="12345" due_at="Jan 20, 2025, 11:59 PM"/>
        <override section_id="67890" due_at="Jan 22, 2025, 11:59 PM"/>
    </overrides>

    Assignment description here.
</assignment>
```

For complete documentation, read `.claude/skills/mdxcanvas/generate-content/quizzes/references/override_tag.md`.

---

## Date Format

All date attributes use this format: `MMM d, yyyy, h:mm AM/PM`

Examples: `Jan 15, 2025, 11:59 PM` · `Aug 25, 2025, 9:00 AM`

---

## How This Works

When asked about Canvas resource tags:

1. Provide the relevant snippet from this file for the 80% case.
2. For full attribute details, direct the user to the appropriate `documents/supported_tags/tags/` file.
3. When generating content, always read `.claude/skills/mdxcanvas/generate-content/SKILL.md` for the confirmation flow.
