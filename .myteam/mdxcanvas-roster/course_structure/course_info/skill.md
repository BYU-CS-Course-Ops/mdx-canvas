# course_info

The `course_info` file is the configuration file MDXCanvas uses to connect to Canvas and identify your course. It is
required for every deployment.

## Overview

`course_info` is passed to `mdxcanvas` via the `--course-info` flag:

```bash
mdxcanvas --course-info course_info.json course.canvas.md.xml.jinja
```

**Supported formats:** YAML (`.yaml`, `.yml`), JSON (`.json`), or MarkdownData (`.md`, `.mdd`).

**Security:** This file contains Canvas API credentials. **Never commit it to source control.** Add it to `.gitignore`.

## Required Fields for Deployment

| Field              | Description             | Example                        |
|--------------------|-------------------------|--------------------------------|
| `CANVAS_API_URL`   | Canvas instance URL     | `https://byu.instructure.com/` |
| `CANVAS_COURSE_ID` | Numeric course ID       | `12345`                        |
| `LOCAL_TIME_ZONE`  | IANA timezone for dates | `America/Denver`               |

Find the `CANVAS_COURSE_ID` in the Canvas course URL: `https://canvas.edu/courses/[COURSE_ID]`

Common `LOCAL_TIME_ZONE` values: `America/Denver`, `America/Chicago`, `America/New_York`, `America/Los_Angeles`

## Optional Fields

| Field          | Description                                              | Example                    |
|----------------|----------------------------------------------------------|----------------------------|
| `COURSE_NAME`  | Full display name shown in Canvas                        | `Example Course`           |
| `COURSE_CODE`  | Short course identifier                                  | `EXAMPLE 101`              |
| `COURSE_IMAGE` | Filename of the course thumbnail image                   | `example_course_image.png` |
| `GLOBAL_ARGS`  | Dictionary of Jinja variables available to all templates | see below                  |

`GLOBAL_ARGS` in `course_info` is a simpler alternative to a separate `global_args.yaml` file for small variable sets:

```yaml
GLOBAL_ARGS:
  semester: Fall 2025
  instructor_name: Dr. Smith
  office_hours: "MWF 2-3 PM"
```

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

## Deploying to Canvas

Once `course_info` is ready, deployment uses the `run_mdxcanvas.sh` script alongside a `.env` file containing
`CANVAS_API_TOKEN`.

```bash
bash .claude/skills/mdxcanvas/deploy/references/run_mdxcanvas.sh \
    "<path/to/.env>" \
    "<path/to/course_info.json>" \
    "<path/to/course.canvas.md.xml.jinja>"
```

With global args:

```bash
bash .claude/skills/mdxcanvas/deploy/references/run_mdxcanvas.sh \
    "<path/to/.env>" \
    "<path/to/course_info.json>" \
    "--global-args global_args.yaml course.canvas.md.xml.jinja"
```

**Security rules:**

- Store `CANVAS_API_TOKEN` in a `.env` file — never in source control
- Never pass the token as a command-line argument
- Never echo or log the token value
- Add both `course_info.json` and `.env` to `.gitignore`

To get a Canvas API token: log in to Canvas → **Account** → **Settings** → **Approved Integrations** → **+ New Access
Token**.
