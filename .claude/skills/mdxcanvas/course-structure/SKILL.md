---
name: mdxcanvas/course-structure
description: Locate an existing MDXCanvas course directory or scaffold a new one. Covers finding course files, global args, course_info, CSS, and content structure.
license: Complete terms in ../LICENSE.txt
---

# Course Structure

This skill helps you locate an existing MDXCanvas course OR scaffold a new one from scratch.

## Locating an Existing Course

### Entry Point File

The main course file is typically named with a pattern like:

- `course.canvas.md.xml.jinja`
- `<course-name>.canvas.md.xml`
- `<course-name>.canvas.md.xml.jinja`

Search for files matching `*.canvas.md.xml*` in the project root or any subdirectory.

### Course Info File (`course_info.json`)

Required for deployment. Contains Canvas API credentials and course ID.

Search for files named `course_info.json` or `course_info*.json`. Common locations:

- Project root
- Alongside the main entry point file

Fields:

| Field              | Description               | Example                        |
|--------------------|---------------------------|--------------------------------|
| `CANVAS_API_URL`   | Canvas instance URL       | `https://byu.instructure.com/` |
| `CANVAS_COURSE_ID` | Numeric course ID         | `20736`                        |
| `LOCAL_TIME_ZONE`  | Timezone for date parsing | `America/Denver`               |

### Global Args File

Contains course-wide Jinja variables (term, year, dates, grade weights).

Search for files named `global_args.json`, `global_args.yaml`, `global-args.json`, or `global-args.yaml`. Common
locations:

- Project root
- Alongside the entry point file

Common fields to confirm identity:

| Field           | Description     | Example                  |
|-----------------|-----------------|--------------------------|
| `term` / `Term` | Semester + year | `fall2025`, `winter2026` |
| `year` / `Year` | Academic year   | `2025`                   |
| `start_date`    | Term start      | `Aug 25, 2025`           |
| `end_date`      | Term end        | `Dec 15, 2025`           |

If no global args file exists, ask the user if they want to create one (see `references/best_practice_layout.md` for
structure).

### CSS Style File

Optional. Applies custom styling to Canvas pages.

Search for `style.css` or `*.css` adjacent to the entry point file.

### Content Files

MDXCanvas content files follow the pattern `*.canvas.md.xml` or `*.canvas.md.xml.jinja`. They are commonly organized in
a `content/` subdirectory. See `references/best_practice_layout.md` for recommended layout.

## How This Works

When asked to locate course structure:

1. Search for `*.canvas.md.xml*` to find the entry point.
2. Search for `course_info*.json` to find deployment config.
3. Search for `global_args*` to find Jinja variables.
4. Report what was found and where. If items are missing, note them explicitly.
5. If the user wants to scaffold a new course, read `references/best_practice_layout.md` and create the structure
   described there.

## Scaffolding a New Course

Read `.claude/skills/mdxcanvas/course-structure/references/best_practice_layout.md` for the recommended directory
structure and file naming conventions.

Read `.claude/skills/mdxcanvas/course-structure/references/naming_conventions.md` for file extension and naming rules.

When scaffolding:

1. Create the directory structure from `best_practice_layout.md`
2. Use skeletons from `.claude/skills/mdxcanvas/generate-content/courses/templates/` for starter files
3. Present a summary of what was created and next steps

## Complete Reference

For full tag documentation on the tags used inside these files, read:

- `.claude/skills/mdxcanvas/canvas-resources/SKILL.md` — Canvas resource tags
- `.claude/skills/mdxcanvas/special-tags/SKILL.md` — Special/helper tags
