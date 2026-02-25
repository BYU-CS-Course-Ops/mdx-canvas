# MDXCanvas Naming Conventions

## File Extensions

MDXCanvas files use chained extensions that describe how the file is processed:

| Extension              | Meaning                                                          |
|------------------------|------------------------------------------------------------------|
| `.canvas.md.xml`       | Static content file: XML tags wrapping Markdown, parsed directly |
| `.canvas.md.xml.jinja` | Jinja template: rendered first, then parsed as XML+Markdown      |

The `.jinja` suffix tells MDXCanvas to render the file through Jinja2 before XML parsing.

## File Naming

Use **kebab-case** for all content files.

### Pattern: `<topic>-<type>.canvas.md.xml[.jinja]`

Examples:

| File Type             | Example Name                         |
|-----------------------|--------------------------------------|
| Quiz (static)         | `python-loops-quiz.canvas.md.xml`    |
| Quiz (template)       | `weekly-quizzes.canvas.md.xml.jinja` |
| Assignment (static)   | `homework-1.canvas.md.xml`           |
| Assignment (template) | `homework.canvas.md.xml.jinja`       |
| Page                  | `week-1-intro.canvas.md.xml`         |
| Announcement          | `welcome-announcement.canvas.md.xml` |
| Course entry point    | `course.canvas.md.xml.jinja`         |

## Configuration Files

| File                      | Naming                                   | Notes                              |
|---------------------------|------------------------------------------|------------------------------------|
| Canvas API config         | `course_info.json`                       | Never commit — add to `.gitignore` |
| Global Jinja args         | `global_args.yaml` or `global_args.json` | Committed — no credentials         |
| Per-template args (table) | `<template-name>_args.md`                | MarkdownData table                 |
| Per-template args (JSON)  | `<template-name>_args.json`              | JSON list or dict                  |
| CSS styles                | `style.css`                              | Optional, applied to Canvas pages  |

## Content ID Naming

The `content_id` used in `<item>` tags within `<module>` blocks must match the `title` (or `id`) attribute of the target
resource exactly.

```xml
<!-- This assignment... -->
<assignment title="Homework 1">...</assignment>

<!-- ...is referenced in a module like this -->
<item type="assignment" content_id="Homework 1" indent="1" />
```

If you set an explicit `id` on the resource, use that instead of the title:

```xml
<assignment id="hw1" title="Homework 1 (Updated)">...</assignment>
<item type="assignment" content_id="hw1" indent="1" />
```

## Args File Naming for Jinja Templates

When a Jinja template is paired with a MarkdownData args file, keep them together with matching names:

```
content/assignments/
├── homework.canvas.md.xml.jinja   ← template
└── homework_args.md               ← args (MarkdownData table)
```

Invoke together:

```bash
mdxcanvas --course-info course_info.json --args content/assignments/homework_args.md content/assignments/homework.canvas.md.xml.jinja
```
