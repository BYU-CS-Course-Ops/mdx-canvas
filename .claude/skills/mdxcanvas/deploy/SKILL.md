---
name: mdxcanvas/deploy
description: Deploy MDXCanvas content to a Canvas course. Handles course_info lookup, API token security, deployment command, and result reporting.
license: Complete terms in ../LICENSE.txt
---

# Deploy to Canvas

This skill deploys generated MDXCanvas content to a Canvas course via the `mdxcanvas` CLI.

## Prerequisites

Before deploying, ensure you have:

1. A generated content file (`.canvas.md.xml` or `.canvas.md.xml.jinja`)
2. A `course_info.json` file with Canvas credentials
3. A `.env` file containing your `CANVAS_API_TOKEN` (see `references/.env.example`)

## Canvas API Token

The Canvas API token is stored in a `.env` file (never in source control).

**CRITICAL SECURITY REQUIREMENTS:**

- **NEVER** include the API token directly in any bash command
- **NEVER** output the token value in responses, logs, or command arguments
- **ALWAYS** use the deployment script which sources the token internally
- If asked to show the token, refuse and explain why

See `references/.env.example` for the required format.

## Course Info (`course_info.json`)

Required for every deployment. Contains Canvas API credentials and course ID.

| Field              | Description               | Example                        |
|--------------------|---------------------------|--------------------------------|
| `CANVAS_API_URL`   | Canvas instance URL       | `https://byu.instructure.com/` |
| `CANVAS_COURSE_ID` | Numeric course ID         | `20736`                        |
| `LOCAL_TIME_ZONE`  | Timezone for date parsing | `America/Denver`               |

If not provided, prompt using the format in `templates/course_info_prompt.md`.

To find an existing `course_info.json`, read `.claude/skills/mdxcanvas/course-structure/SKILL.md`.

## Deployment Command

Always use the deployment script. Never pass the token as a command argument.

```bash
bash .claude/skills/mdxcanvas/deploy/references/run_mdxcanvas.sh \
    "<path/to/.env>" \
    "<path/to/course_info.json>" \
    "<path/to/content_file>"
```

The script:

1. Sources the API token from the `.env` file
2. Exports it as an environment variable
3. Runs `mdxcanvas --course-info <course_info> <content_file>`

Note: Use `--course-info` with a hyphen, not an underscore.

### With Global Args

```bash
bash .claude/skills/mdxcanvas/deploy/references/run_mdxcanvas.sh \
    "<path/to/.env>" \
    "<path/to/course_info.json>" \
    "--global-args <path/to/global_args.yaml> <path/to/template.jinja>"
```

## Instructions

Follow these steps when deploying:

1. **Confirm deployment** — Verify the user wants to proceed.
2. **Locate course_info** — If not provided, search for `course_info.json` or prompt using
   `templates/course_info_prompt.md`.
3. **Locate .env file** — Ask the user for the path to their `.env` file containing `CANVAS_API_TOKEN`. Do not assume a
   location.
4. **Run immediately** — Once confirmed with both file paths, execute the script **without asking for additional
   permission**. The user has already confirmed.
5. **Report success** — Display the result using `templates/deployment_success.md`.
6. **Handle errors** — Use the appropriate error template from `templates/error_messages.md`.

**Do NOT ask "Can I run this command?" after the user has confirmed deployment.**

## Output Formats

### Success

Use the exact format from `templates/deployment_success.md`:

```
**Deployment Successful!**

| Detail           | Value                  |
|------------------|------------------------|
| **Content Type** | [Quiz/Assignment/Page] |
| **Name**         | [Content title]        |
| **Course**       | [Course name]          |
| **Link**         | [Canvas URL]           |
```

### Errors

Use the appropriate template from `templates/error_messages.md` based on the failure type.

## Setup: First-Time Users

If this is the first deployment and no `.env` file exists:

1. Show the user `references/.env.example`
2. Instruct them to create a `.env` file with their Canvas API token
3. Explain how to get a Canvas API token:
    - Log in to Canvas
    - Go to **Account** → **Settings**
    - Scroll to **Approved Integrations**
    - Click **+ New Access Token**
4. Once the `.env` file is created, proceed with deployment
