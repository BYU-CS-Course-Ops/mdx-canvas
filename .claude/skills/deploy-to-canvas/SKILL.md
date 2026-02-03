---
name: deploy-to-canvas
description: Deploy the generated canvas content to a Canvas course when if the user agrees after generation. Should ask for the `course_info` CONFIG file path if not already provided.
license: Complete terms in LICENSE.txt
---

# Deploy to Canvas

## Overview

The `deploy-to-canvas` skill is designed to facilitate the deployment of generated Canvas content, such as quizzes,
assignments, and pages, to a specified Canvas course. This skill works in conjunction with content generation skills
like `generate-quiz` to streamline the process of publishing educational materials directly to the Canvas LMS.

## Templates

The `/templates/` folder contains standardized templates for consistent deployment messaging:

- **`deployment_success.md`** - Exact format for successful deployment summaries
- **`course_info_prompt.md`** - Standard prompt when course info is missing
- **`error_messages.md`** - Consistent error message formats for various failure scenarios

## Canvas API Token

The `deploy-to-canvas` skill requires a valid Canvas API token to deploy to a given course.
The API token is stored in `/references/.env` file under the key `CANVAS_API_TOKEN`.

**CRITICAL SECURITY REQUIREMENTS:**
- **NEVER** include the API token directly in any bash command
- **NEVER** output the token in responses, logs, or command arguments
- **ALWAYS** use the deployment script which sources the token internally
- The token must remain invisible to the user at all times

## Course Info

The `course_info` CONFIG file is essential for the deployment process. It contains necessary details about the Canvas
course:

| Field              | Description         | Example                        |
|--------------------|---------------------|--------------------------------|
| `CANVAS_API_URL`   | Canvas instance URL | `https://byu.instructure.com/` |
| `CANVAS_COURSE_ID` | Numeric course ID   | `20736`                        |
| `LOCAL_TIME_ZONE`  | Timezone for dates  | `America/Denver`               |

If the user has not provided this information, prompt them using the format in `/templates/course_info_prompt.md`.

## Deployment Command

The deployment uses the `mdxcanvas` CLI tool via the `/references/run_mdxcanvas.sh` script.

**IMPORTANT:** Always use the script to deploy. Never pass the token as a command argument.

```bash
bash /references/run_mdxcanvas.sh "/references/.env" "<course_info_path>" "<content_file_path>"
```

The script internally:
1. Sources the API token from the .env file
2. Exports it as an environment variable
3. Runs mdxcanvas with the provided paths

Note: Use `--course-info` with a hyphen, not an underscore.

## Instructions

When deploying content to Canvas, follow these steps:

1. **Confirm deployment** - Verify the user wants to proceed with deployment.
2. **Check course info** - If the `course_info` CONFIG file path has not been provided, prompt the user using
   `/templates/course_info_prompt.md`.
3. **Run deployment immediately** - Once the user confirms and provides course info, execute the deployment script
   **without asking for additional permission**. The user has already confirmed they want to deploy.
4. **Use the deployment script** - Always use `/references/run_mdxcanvas.sh` to run the deployment. This keeps the
   API token hidden from command output.
5. **Report success** - Display the result using the exact format in `/templates/deployment_success.md`.
6. **Handle errors** - Use the appropriate error template from `/templates/error_messages.md` for any failures.

**IMPORTANT:** Do NOT ask "Can I run this command?" or similar. Once deployment is confirmed, just run the script.

## Output Formats

### Success

Use the exact format from `/templates/deployment_success.md`:

```
**Deployment Successful!**

| Detail           | Value           |
|------------------|-----------------|
| **Content Type** | [type]          |
| **Name**         | [content title] |
| **Course**       | [course name]   |
| **Link**         | [Canvas URL]    |
```

### Errors

Use the appropriate template from `/templates/error_messages.md` based on the failure type.
