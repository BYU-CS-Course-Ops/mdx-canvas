---
name: Course Setup Reference
description: Disk layout, file extensions, naming conventions, and entry point structure for MDXCanvas courses.
---

# Course Setup Reference

## When to Use This Reference

Use this reference when looking up:

- File extensions or naming conventions
- The entry point file pattern in an existing course
- How `<include>` connects files to the entry point
- Root container elements and required companion files
- Recommended directory layout

---

## What is an MDXCanvas Course

An MDXCanvas course is a directory containing source files that MDXCanvas converts into Canvas LMS resources. The entry
point is a file matching the pattern `*.canvas.md.xml` or `*.canvas.md.xml.jinja` — typically named
`course.canvas.md.xml.jinja`.

**Root container:** Use `<div>` or `<course>` as the outermost wrapper (both work). Sub-files included via `<include>`
may use `<div>` or `<content>` as their root — these are ignored by the parser.

Required companion files:

- `course_info.json` (or `.yaml`) — course credentials to connect to the correct Canvas course
- `global_args.yaml` — course-wide Jinja2 variables (term, year, dates, grade weights)

---

## Recommended Directory Layout

```
my-course/
├── course_info.json                       ← Canvas credentials + course ID (NEVER commit)
├── global_args.yaml                       ← Course-wide Jinja variables (commit OK)
├── style.css                              ← Optional: custom CSS for Canvas pages
├── course.canvas.md.xml.jinja             ← Main entry point — includes all content
│
├── content/
│   ├── syllabus.md                        ← Syllabus content (pulled in via <include>)
│   ├── assignments/
│   │   ├── homework.canvas.md.xml.jinja   ← Assignment template
│   │   └── homework_args.md               ← MarkdownData args table
│   ├── quizzes/
│   │   └── quiz1.canvas.md.xml
│   ├── pages/
│   │   └── week1.canvas.md.xml
│   └── announcements/
│       └── welcome.canvas.md.xml
│
├── images/                                ← Images uploaded via <img> tags
└── files/                                 ← Files uploaded via <file> or <zip> tags
```

Key items:

- `course.canvas.md.xml.jinja` — entry point; wraps everything and uses `<include>` to pull in content files
- `content/` — all course content organized by type
- `global_args.yaml` — course-wide variables available in every `.jinja` template
- `course_info.json` — course credentials

---

## File Extensions and Naming Conventions

MDXCanvas files use chained extensions that describe how the file is processed:

| Extension              | Meaning                                                       |
|------------------------|---------------------------------------------------------------|
| `.canvas.html`         | Static content: Pure HTML                                     |
| `.canvas.md`           | Static content: Pure markdown used with `<md-page/>` tags     |
| `.canvas.md.xml`       | Static content: XML tags wrapping Markdown, parsed directly   |
| `.canvas.md.xml.jinja` | Jinja template: rendered first, then parsed as XML + Markdown |

Use **kebab-case** for all content files.

| File Type             | Example Name                               |
|-----------------------|--------------------------------------------|
| Quiz (static)         | `python-loops-quiz.canvas.md.xml`          |
| Quiz (template)       | `weekly-quizzes.canvas.md.xml.jinja`       |
| Assignment (static)   | `homework-1.canvas.md.xml`                 |
| Assignment (template) | `homework.canvas.md.xml.jinja`             |
| Page                  | `week-1-intro.canvas.md.xml`               |
| MD Page               | `week-1-resources.canvas.md`               |
| Course entry point    | `course.canvas.md.xml.jinja`               |
| Global args           | `global_args.yaml`                         |
| Per-template args     | `homework_args.md` or `homework_args.json` |

Use `.jinja` as the final suffix for any file that uses Jinja templating.

---

## Locating an Existing Course

Search for files matching `*.canvas.md.xml*` in the project root and subdirectories — this finds the entry point. Look
alongside it for:

- `course_info.json` (or `.yaml`) — credentials
- `global_args.yaml` (or `.json`) — Jinja variables

---

## Sub-Skills

For `course_info` fields and deployment config, see `course_info/skill.md`.

For `global_args.yaml` format and usage, see `global_args/skill.md`.
