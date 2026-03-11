# Understanding an MDXCanvas Course

## The Entry Point File

The main course file is typically named `course.canvas.md.xml.jinja`. It is the file passed directly to the `mdxcanvas`
CLI.

The entry point typically contains:

- `<course-settings>` — course name, code, and optional image
- `<assignment-groups>` — grade categories with weights
- `<include>` tags that pull in content files from `content/`
- `<module>` tags that define Canvas navigation

```xml
<div>
    <course-settings name="CS 101: Intro to Programming" code="CS 101" />

    <assignment-groups>
        <group name="Homework" weight="40" />
        <group name="Quizzes" weight="30" />
        <group name="Projects" weight="30" />
    </assignment-groups>

    <include path="content/assignments/homework.canvas.md.xml.jinja" />
    <include path="content/quizzes/quiz1.canvas.md.xml" />

    <module id="week-1" title="Week 1: Introduction">
        <item type="page" content_id="week-1-intro" indent="1" />
        <item type="assignment" content_id="Homework 1" indent="1" />
    </module>
</div>
```

## How Includes Work

`<include path="..."/>` embeds the content of another file at the point of inclusion. This keeps the entry point clean
and allows content files to be edited independently.

The `path` is always relative to the file containing the `<include>` tag.

```xml
<!-- In course.canvas.md.xml.jinja -->
<syllabus>
    <include path="content/syllabus.md"/>
</syllabus>

<include path="content/assignments/homework.canvas.md.xml.jinja" />
```

When the included file is a `.jinja` template, it is rendered with the same global args before being processed as XML.

## Jinja Templates

Files with the `.jinja` extension are rendered through Jinja2 before XML parsing. Use them to generate repeated
resources from one template or to inject course-wide variables (e.g., `{{ term }}`, `{{ year }}`).

For full Jinja usage — function reference, template patterns, args file formats, and CLI flags — see `jinja/skill.md`.

## Content Generation Workflow

Before writing any files, confirm the plan with the user:

1. **Plan** — describe what resources will be generated, their titles, file paths, and key settings
2. **Confirm** — show a summary table and ask "Shall I proceed?"
3. **Write** — create the `.canvas.md.xml` or `.jinja` files
4. **Deploy** — run `mdxcanvas` to push to Canvas (requires `course_info` and `.env`)

Example confirmation table:

| Resource Type | Title             | File Path                                       | Notes                     |
|---------------|-------------------|-------------------------------------------------|---------------------------|
| Quiz          | Python Loops Quiz | content/quizzes/python-loops-quiz.canvas.md.xml | 10 questions, mixed types |
| Assignment    | Homework 1        | content/assignments/homework-1.canvas.md.xml    | 100 pts, due Jan 15       |

## Args File Formats

Args files pass variable data to Jinja templates. Supported formats:

- **MarkdownData table** (`.md`) — each row becomes one loop iteration; access with `{{ item['Column'] }}`
- **MarkdownData keyed file** (`.md`) — keyed by section heading; access with `{{ title }}`,
  `{{ info['content']['Key'] }}`
- **JSON** (`.json`) — list of dicts or nested dict

For full format examples and access patterns, see `jinja/skill.md`.
