# Course Organization

## Hierarchy Overview

MDXCanvas courses are organized hierarchically, mirroring how a course is taught:

```
Course
└── Units (major thematic blocks)
    └── Days (individual class sessions)
        └── Lectures (specific topics within a day)
            └── Canvas Modules (navigation containers)
                └── Items (pages, assignments, quizzes)
```

This hierarchy is reflected in the file system layout under `content/` and in the Canvas modules structure.

## File Organization

Content lives under `content/` organized by type:

```
content/
├── syllabus.md
├── assignments/
│   ├── homework.canvas.md.xml.jinja
│   └── homework_args.md
├── quizzes/
│   └── quiz1.canvas.md.xml
├── pages/
│   └── week1-intro.canvas.md.xml
└── announcements/
    └── welcome.canvas.md.xml
```

For larger courses with units, you may further organize by unit:

```
content/
├── unit1/
│   ├── days/
│   ├── quizzes/
│   └── assignments/
└── unit2/
    ├── days/
    ├── quizzes/
    └── assignments/
```

## How Structure Maps to Canvas

| MDXCanvas concept | Canvas result                                                 |
|-------------------|---------------------------------------------------------------|
| `<assignment>`    | Canvas assignment (visible in Assignments)                    |
| `<quiz>`          | Canvas quiz (visible in Quizzes)                              |
| `<page>`          | Canvas page (visible in Pages)                                |
| `<module>`        | Canvas module (visible in Modules navigation)                 |
| `<item>`          | Entry within a module linking to an assignment, quiz, or page |

Canvas modules provide the primary student-facing navigation. A module groups related content for a week, unit, or
topic. Students see modules in order and can track completion.

The entry point file (`course.canvas.md.xml.jinja`) is where modules are declared and `<item>` tags link to the content
files that have been included earlier in the same file.
