# Course Structure

## What is an MDXCanvas Course

An MDXCanvas course is a directory containing source files that MDXCanvas converts into Canvas LMS resources. The entry
point is a file matching the pattern `*.canvas.md.xml` or `*.canvas.md.xml.jinja` — typically named
`course.canvas.md.xml.jinja`.

**Root container:** Use `<div>` or `<course>` as the outermost wrapper (both work). Sub-files included via `<include>`
may use `<div>` or `<content>` as their root — these are ignored by the parser.

Required companion files:

- `course_info.json` (or `.yaml`) — Canvas API credentials and course ID; **never commit this file**
- `global_args.yaml` — course-wide Jinja2 variables (term, year, dates, grade weights); safe to commit

## Recommended Directory Layout

```
my-course/
├── course_info.json              ← Canvas credentials + course ID (NEVER commit)
├── global_args.yaml              ← Course-wide Jinja variables (commit OK)
├── style.css                     ← Optional: custom CSS for Canvas pages
├── course.canvas.md.xml.jinja   ← Main entry point — includes all content
│
├── content/
│   ├── syllabus.md               ← Syllabus content (pulled in via <include>)
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
├── images/                        ← Images uploaded via <img> tags
└── files/                         ← Files uploaded via <file> or <zip> tags
```

Key items:

- `course.canvas.md.xml.jinja` — entry point; wraps everything and uses `<include>` to pull in content files
- `content/` — all course content organized by type
- `global_args.yaml` — course-wide variables available in every `.jinja` template
- `course_info.json` — credentials; add to `.gitignore`

## File Extensions & Naming Conventions

MDXCanvas files use chained extensions that describe how the file is processed:

| Extension              | Meaning                                                       |
|------------------------|---------------------------------------------------------------|
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
| Course entry point    | `course.canvas.md.xml.jinja`               |
| Global args           | `global_args.yaml`                         |
| Per-template args     | `homework_args.md` or `homework_args.json` |

## Locating an Existing Course

Search for files matching `*.canvas.md.xml*` in the project root and subdirectories — this will find the entry point.
Then look alongside it for:

- `course_info.json` (or `.yaml`) — credentials
- `global_args.yaml` (or `.json`) — Jinja variables

## Scaffolding a New Course

1. Create the course directory: `my-course/`
2. Create `content/assignments/`, `content/quizzes/`, `content/pages/`, `content/announcements/`
3. Create `images/` and `files/` directories
4. Copy and fill in `course_info.json` (from the skeleton below) — add to `.gitignore`
5. Create `global_args.yaml` with term, year, start/end dates, and grade weights
6. Create `course.canvas.md.xml.jinja` as the entry point

Minimal `course.canvas.md.xml.jinja`:

```xml

<div>
    <course-settings name="My Course" code="CS 101"/>

    <syllabus>
        <include path="content/syllabus.md"/>
    </syllabus>

    <assignment-groups>
        <group name="Homework" weight="40"/>
        <group name="Quizzes" weight="30"/>
        <group name="Projects" weight="30"/>
    </assignment-groups>

    <include path="content/assignments/homework.canvas.md.xml.jinja"/>
    <include path="content/quizzes/quiz1.canvas.md.xml"/>

    <module id="week-1" title="Week 1: Introduction">
        <item type="page" content_id="week-1-intro" indent="1"/>
        <item type="assignment" content_id="Homework 1" indent="1"/>
    </module>
</div>
```

## Special Helper Tags

These tags provide infrastructure-level functionality used alongside resource tags.

| Tag                 | Purpose                                    | Key Attributes                                                 |
|---------------------|--------------------------------------------|----------------------------------------------------------------|
| `<include>`         | Embed external file content inline         | `path`, `fenced`, `lines`, `args`, `usediv`                    |
| `<md-page>`         | Create a Canvas page from a `.md` file     | `path`, `title`                                                |
| `<file>`            | Upload and link a single file to Canvas    | `path`, `title`, `canvas_folder`, `unlock_at`, `lock_at`       |
| `<img>`             | Upload and embed an image inline           | `src`, `canvas_folder`                                         |
| `<zip>`             | Upload a zip archive to Canvas             | `name`, `path`, `additional_files`, `exclude`, `canvas_folder` |
| `<course-link>`     | Link to another course item by type and id | `type`, `id`, `fragment`                                       |
| `<course-settings>` | Set course metadata (name, code, image)    | `name`, `code`, `image`                                        |

For full attribute tables and examples for all 7 tags, see `special_tags/skill.md`.
