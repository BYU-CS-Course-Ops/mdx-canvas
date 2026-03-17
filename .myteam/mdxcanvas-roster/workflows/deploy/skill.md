---
name: deploy
description: Agentic deploy workflow — locate the course, validate it, run dry-run, then push to Canvas. Claude/Codex executes all commands.
---

# Deploy Workflow

## Non-Negotiables

- Never echo, log, print, or display `CANVAS_API_TOKEN` at any point.
- Never commit `course_info.json` or `.env` to source control.
- Never run `erasecanvas` without explicit user confirmation typed by the user.
- Run dry-run and confirm it is clean before running full deploy.
- Ask the user for the `.env` path — never assume or guess its location.

---

## Step 1: Locate the Course

Search the working directory for the entry point file:

```bash
find . -name "*.canvas.md.xml*" | head -20
```

If multiple entry points are found, ask the user which one to deploy.

Identify the course root directory (the directory containing the entry point).

Look for `course_info.json` or `course_info.yaml` in the course root:

```bash
find . -name "course_info.*" | head -10
```

If no `course_info` file exists: stop. Tell the user: "No `course_info` file found. Create one before deploying. See `reference/course-setup/course_info/skill.md`."

---

## Step 2: Get the .env Path

Ask the user: "What is the path to your `.env` file containing `CANVAS_API_TOKEN`?"

Do not attempt to locate or guess the `.env` file. Wait for the user to provide the path.

Verify the file exists:

```bash
test -f "<user-provided-path>" && echo "found" || echo "not found"
```

If not found: tell the user and stop. Do not proceed without a valid `.env` file.

Verify the file contains `CANVAS_API_TOKEN` without displaying the value:

```bash
grep -q "CANVAS_API_TOKEN" "<path-to-.env>" && echo "token present" || echo "token missing"
```

If the token is missing: stop. Tell the user to add `CANVAS_API_TOKEN=<your-token>` to the `.env` file.

---

## Step 3: Validate

Run the validation checklist before deploying. Check each item:

1. Every `<item content_id>` matches an existing resource `id` (or `title` if no `id` was set)
2. All date strings use `MMM d, yyyy, h:mm AM/PM` format
3. Every `assignment_group` value matches a `<group>` defined in `<assignment-groups>`
4. Module items reference content included in the same entry point
5. `.jinja` templates loop with the correct access pattern for their args format
6. `course_info.json` and `.env` are in `.gitignore`

```bash
grep -r "course_info\|\.env" .gitignore 2>/dev/null || echo ".gitignore missing entries"
```

Fix any failures before continuing.

---

## Step 4: Dry-Run

Load the token into the environment without echoing it, then run dry-run:

```bash
set -a && source <path-to-.env> && set +a
mdxcanvas --course-info <path/to/course_info.json> --dry-run <path/to/course.canvas.md.xml.jinja>
```

With global args (if `global_args.yaml` exists in the course root):

```bash
set -a && source <path-to-.env> && set +a
mdxcanvas --course-info <path/to/course_info.json> \
          --global-args <path/to/global_args.yaml> \
          --dry-run <path/to/course.canvas.md.xml.jinja>
```

Read the dry-run output. Check for:

- Parse errors or XML syntax errors
- Missing `content_id` references
- Unresolved `<item>` references
- Jinja rendering errors (`UndefinedError`, `TemplateNotFound`)

If the dry-run has errors:
- Fix the source files.
- Re-run the dry-run.
- Do not proceed to Step 5 until dry-run is clean.

Show the user a summary of what the dry-run would deploy (resource counts by type).

---

## Step 5: Confirm and Deploy

Tell the user: "Dry-run complete. Ready to deploy to Canvas. Shall I proceed?"

Wait for explicit confirmation before running the full deploy.

After confirmation, run:

```bash
set -a && source <path-to-.env> && set +a
mdxcanvas --course-info <path/to/course_info.json> <path/to/course.canvas.md.xml.jinja>
```

With global args:

```bash
set -a && source <path-to-.env> && set +a
mdxcanvas --course-info <path/to/course_info.json> \
          --global-args <path/to/global_args.yaml> \
          <path/to/course.canvas.md.xml.jinja>
```

With CSS:

```bash
mdxcanvas --course-info course_info.json --css style.css course.canvas.md.xml.jinja
```

Read the deploy output. Report success or failure to the user.

If the deploy fails: read the error message, diagnose the cause, fix the source, and offer to re-run.

---

## Step 6: Post-Deploy Check

Tell the user: "Deploy complete. Check Canvas to confirm the resources appear as expected."

Ask: "Do you want me to run cleanup to remove stale Canvas resources that are no longer in source?"

If yes, confirm once more ("This will delete Canvas resources not present in the source files."), then run:

```bash
set -a && source <path-to-.env> && set +a
mdxcanvas --course-info <path/to/course_info.json> --cleanup <path/to/course.canvas.md.xml.jinja>
```

---

## Step 7: Erase — DESTRUCTIVE

Only proceed here if the user explicitly asks to erase the course from Canvas.

Before running, ask the user to type "erase" to confirm. Do not proceed without this exact confirmation.

```bash
set -a && source <path-to-.env> && set +a
erasecanvas --course-info <path/to/course_info.json>
```

This permanently deletes all content from the Canvas course. It cannot be undone.

---

## Security Rules

- Load `CANVAS_API_TOKEN` via `source <.env>` only. Never via `echo`, `cat`, or command substitution that prints the value.
- Never display, log, or include the token in any output.
- Never commit `course_info.json` or `.env`. Verify `.gitignore` covers both before deploying.
