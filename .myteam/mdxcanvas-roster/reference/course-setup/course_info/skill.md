---
name: course_info Reference
description: Required fields, optional fields, and example for course_info.json / course_info.yaml.
---

# course_info

## When to Use This Reference

Use this reference when looking up:

- Fields in `course_info.json` or `course_info.yaml`
- How to connect MDXCanvas to a Canvas course (URL, course ID, timezone)
- How to pass credentials to `mdxcanvas`
- Using `GLOBAL_ARGS` in `course_info` instead of a separate `global_args.yaml`

## Non-Negotiables

- Never commit `course_info.json` or `.env` to source control. Add both to `.gitignore`.
- Never pass `CANVAS_API_TOKEN` as a command-line argument.
- Never echo or log the token value.
- Store `CANVAS_API_TOKEN` in `.env` only.

---

## Overview

`course_info` is the configuration file MDXCanvas uses to connect to Canvas and identify your course. It is required for
every deployment.

Pass it via the `--course-info` flag:

```bash
mdxcanvas --course-info course_info.json course.canvas.md.xml.jinja
```

**Supported formats:** YAML (`.yaml`, `.yml`), JSON (`.json`), or MarkdownData (`.md`, `.mdd`).

---

## Required Fields for Deployment

| Field              | Description             | Example                        |
|--------------------|-------------------------|--------------------------------|
| `CANVAS_API_URL`   | Canvas instance URL     | `https://byu.instructure.com/` |
| `CANVAS_COURSE_ID` | Numeric course ID       | `12345`                        |
| `LOCAL_TIME_ZONE`  | IANA timezone for dates | `America/Denver`               |

Find `CANVAS_COURSE_ID` in the Canvas course URL: `https://canvas.edu/courses/[COURSE_ID]`

Common `LOCAL_TIME_ZONE` values: `America/Denver`, `America/Chicago`, `America/New_York`, `America/Los_Angeles`

---

## Optional Fields

| Field          | Description                                              | Example                    |
|----------------|----------------------------------------------------------|----------------------------|
| `COURSE_NAME`  | Full display name shown in Canvas                        | `Example Course`           |
| `COURSE_CODE`  | Short course identifier                                  | `EXAMPLE 101`              |
| `COURSE_IMAGE` | Filename of the course thumbnail image                   | `example_course_image.png` |
| `GLOBAL_ARGS`  | Dictionary of Jinja variables available to all templates | see below                  |

`GLOBAL_ARGS` in `course_info` is a simpler alternative to a separate `global_args.yaml` for small variable sets:

```yaml
GLOBAL_ARGS:
  semester: Fall 2025
  instructor_name: Dr. Smith
  office_hours: "MWF 2-3 PM"
```

---

## Example

```yaml
CANVAS_API_URL: https://byu.instructure.com/
CANVAS_COURSE_ID: 12345
LOCAL_TIME_ZONE: America/Denver
COURSE_NAME: Example Course
COURSE_CODE: EXAMPLE 101
COURSE_IMAGE: example_course_image.png
GLOBAL_ARGS:
  semester: Fall 2025
  instructor_name: Dr. Smith
  office_hours: "MWF 2-3 PM"
```

JSON equivalent:

```json
{
  "CANVAS_API_URL": "https://YOUR_INSTITUTION.instructure.com/",
  "CANVAS_COURSE_ID": 12345,
  "LOCAL_TIME_ZONE": "America/Denver"
}
```

---

## Deploying to Canvas

For deployment workflow, see `../../workflows/deploy/skill.md`.
