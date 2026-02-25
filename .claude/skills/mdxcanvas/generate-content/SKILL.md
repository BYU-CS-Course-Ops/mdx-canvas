---
name: mdxcanvas/generate-content
description: Generate Canvas resources — quizzes, assignments, pages, or full courses — with a mandatory confirm-before-write flow.
license: Complete terms in ../LICENSE.txt
---

[//]: # (TODO: Add more details on modules and supported item types)

# Generate Content

## What You Can Generate

Ask in plain language — describe what you need and I'll handle the details.

| Resource      | Example prompts                                                                        |
|---------------|----------------------------------------------------------------------------------------|
| **Quiz**      | "Generate a 10-question quiz on Python loops" / "Make a quiz from this topic list"     |
| **Assignment**| "Create a homework assignment on recursion, 100 points, due Friday"                    |
| **Page**      | "Write a Week 1 intro page covering variables and data types"                           |
| **Announcement** | "Draft an announcement welcoming students to the course"                            |
| **Full course** | "Build a full course structure from this syllabus" *(paste or attach your syllabus)* |

Before writing any files, I'll show you a plan like this so you can review and adjust:

```
Here's what I'll generate:

| Resource Type | Title             | File Path                                       | Notes                     |
|---------------|-------------------|-------------------------------------------------|---------------------------|
| Quiz          | Python Loops Quiz | content/quizzes/python-loops-quiz.canvas.md.xml | 10 questions, mixed types |
| Assignment    | Homework 1        | content/assignments/homework-1.canvas.md.xml    | 100 pts, due Jan 15       |
| Page          | Week 1 Intro      | content/pages/week-1-intro.canvas.md.xml        | Overview page             |

Shall I proceed?
```

Nothing is written until you confirm.

---

## How Generation Works

1. **I read your materials** — request, syllabus, topic list, or any context you provide.
2. **I show you a plan** — a confirmation table listing every file I intend to create with its path and key settings.
3. **You confirm** — say "yes", "looks good", or request changes. No files are written before this step.
4. **I write files** — one resource type at a time, showing a summary after each batch.
5. **I offer deployment** — after all files are written, I'll ask if you want to deploy to Canvas.

---

## Resource Reference

### Quizzes

Read `.claude/skills/mdxcanvas/generate-content/quizzes/references/quiz_tag.md` before generating.
Read `.claude/skills/mdxcanvas/generate-content/quizzes/references/quiz_question_types.md` for question syntax.

**Default settings** (use unless user specifies otherwise):

- `shuffle_answers="true"`
- `allowed_attempts="2"`
- `scoring_policy="keep_highest"`
- No time limit

**Question distribution** for N questions:

- 30–40% multiple-choice
- 20–30% true-false
- 10–20% matching or fill-in-the-blank
- 10–20% other types (numerical, multiple-answers, essay, etc.)

Avoid using the same question type consecutively.

**File naming:** `<topic>-quiz.canvas.md.xml`

**After generating:** Display a summary using
`.claude/skills/mdxcanvas/generate-content/quizzes/templates/quiz_summary.md`.

**Skeleton:** See `.claude/skills/mdxcanvas/generate-content/quizzes/templates/quiz_skeleton.xml`.

### Assignments

Read `documents/supported_tags/tags/assignment_tag.md` for full attribute reference.

**File naming:** `<topic>-assignment.canvas.md.xml` or `homework-<n>.canvas.md.xml`

If the user needs multiple similar assignments, suggest a Jinja template approach (see
`.claude/skills/mdxcanvas/templating/SKILL.md`).

**After generating:** Display a brief summary showing title, file path, points, and due date.

**Skeleton:** See `.claude/skills/mdxcanvas/generate-content/assignments/templates/assignment_skeleton.xml`.

### Pages

Read `documents/supported_tags/tags/page_tag.md` for full attribute reference.

**File naming:** `<topic>-page.canvas.md.xml`

**After generating:** Confirm the file path and offer to add it to a module.

**Skeleton:** See `.claude/skills/mdxcanvas/generate-content/pages/templates/page_skeleton.xml`.

### Full Courses

When generating a full course from a syllabus or course description:

1. Parse the material to identify: modules, assignments, quizzes, pages, announcements.
2. Present the full confirmation table before writing anything.
3. Generate in this order: `course.canvas.md.xml.jinja` entry point → content files.
4. Use skeletons from `.claude/skills/mdxcanvas/generate-content/courses/templates/`.

---

## File Placement Priority

Write generated files in the first location that exists:

1. `content/<type>/` subdirectory (e.g., `content/quizzes/`)
2. `content/` directory
3. Course root directory (alongside the entry point)
4. Working directory (last resort — note this to the user)

---

## After Generation

After all files are generated:

1. Show a summary table of everything created.
2. Ask: "Would you like to deploy this to Canvas?"
3. If yes, read `.claude/skills/mdxcanvas/deploy/SKILL.md`.

---

## Agent Instructions

*This section is for Claude. Users can skip it.*

When asked to generate any Canvas resource:

1. Read any provided materials (syllabus, topic description, etc.).
2. Build the confirmation table. Do NOT write files yet.
3. Present the table. Wait for "yes" or approval.
4. Generate files one resource type at a time, showing each output.
5. After all resources are generated, display total summary and offer deployment.

Always validate that generated XML has properly closed and nested tags before writing.
