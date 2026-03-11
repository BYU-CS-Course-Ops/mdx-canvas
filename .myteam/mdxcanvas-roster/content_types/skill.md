# Content Types

## Overview

MDXCanvas can create the following Canvas resource types:

| Tag                   | Creates             | Key Attributes                                                               |
|-----------------------|---------------------|------------------------------------------------------------------------------|
| `<assignment>`        | Canvas assignment   | `title`, `due_at`, `points_possible`, `assignment_group`, `submission_types` |
| `<quiz>`              | Canvas quiz         | `title`, `due_at`, `shuffle_answers`, `allowed_attempts`, `scoring_policy`   |
| `<page>`              | Canvas page         | `title`, `id`                                                                |
| `<module>`            | Canvas module       | `id`, `title`, `prerequisite_module_ids`                                     |
| `<item>`              | Module item         | `type`, `content_id`, `indent`, `completion_requirement`                     |
| `<syllabus>`          | Course syllabus     | (no attributes — wraps content)                                              |
| `<announcement>`      | Course announcement | `title`, `published_at`                                                      |
| `<assignment-groups>` | Grade groups        | contains `<group name="..." weight="..."/>` children                         |

## Date Format

All date attributes across all content types use this format:

```
MMM d, yyyy, h:mm AM/PM
```

Examples: `Jan 15, 2025, 11:59 PM` · `Aug 25, 2025, 9:00 AM`

The timezone is determined by `LOCAL_TIME_ZONE` in `course_info`.

## Section-Specific Dates

Both `<assignment>` and `<quiz>` support different due dates per course section using `<overrides>`:

```xml

<assignment title="Homework 1" due_at="Jan 15, 2025, 11:59 PM">
    <overrides>
        <override section_id="12345" due_at="Jan 20, 2025, 11:59 PM"/>
        <override section_id="67890" due_at="Jan 22, 2025, 11:59 PM"/>
    </overrides>

    Assignment description here.
</assignment>
```

The `section_id` matches the numeric Canvas section ID. The `due_at` on the parent tag serves as the default for
sections not listed in `<overrides>`.
