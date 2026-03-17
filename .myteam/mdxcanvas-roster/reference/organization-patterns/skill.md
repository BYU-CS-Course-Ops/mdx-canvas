---
skill: organization-patterns
---

# Course Organization

## When to Use This Reference

Use this reference whenever a request involves:

- Understanding how a course is organized (by days, units, lectures, or modules)
- Reading the file system layout under `content/`
- Mapping Canvas concepts (modules, items) to MDXCanvas organization patterns

Then route to the relevant sub-skill for the specific pattern in use:

- `days/skill.md` — day-based scheduling with `available_from` / `due_at`
- `lectures/skill.md` — lecture pages and `<md-page>` patterns
- `modules/skill.md` — `<module>` and `<item>` tag details
- `units/skill.md` — unit-level thematic grouping across multiple weeks

---

## Hierarchy Overview

MDXCanvas courses are organized hierarchically:

```
Course
└── Units (major thematic blocks)
    └── Days (individual class sessions)
        └── Lectures (specific topics within a day)
            └── Canvas Modules (navigation containers)
                └── Items (pages, assignments, quizzes)
```

---

## File Organization

Content lives under `content/` organized by type:

```
content/
├── syllabus.md
├── assignments/
├── quizzes/
├── pages/
└── announcements/
```

For larger courses with units, organize by unit:

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

---

## How Structure Maps to Canvas

| MDXCanvas concept | Canvas result                                 |
|-------------------|-----------------------------------------------|
| `<assignment>`    | Canvas assignment                             |
| `<quiz>`          | Canvas quiz                                   |
| `<page>`          | Canvas page                                   |
| `<module>`        | Canvas module (visible in Modules navigation) |
| `<item>`          | Entry within a module linking to content      |
