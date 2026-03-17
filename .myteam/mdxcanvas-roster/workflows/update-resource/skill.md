---
name: update-resource
description: Workflow for editing existing Canvas course resources safely, without creating duplicates.
---

# Update Resource Workflow

## Non-Negotiables

- Never change a resource's `title` without first adding `id` equal to the current `title`. Changing `title` without
  `id` creates a new resource instead of updating the existing one.
- Never write files without user confirmation. Confirm-before-write applies here too.
- Never commit `course_info.json` or `.env` to source control.

## Workflow

### 1. Locate the Resource

Find the file containing the resource. Search for `*.canvas.md.xml*` files under the course directory.

### 2. Check for `id`

Inspect the resource tag.

- If the resource has an explicit `id` attribute: safe to edit `title` and other attributes.
- If the resource has no `id`: add `id` equal to the current `title` value first. Keep `title` unchanged in this edit.
  Then make content changes in a separate edit.

Follow this pattern for `<assignment>`, `<quiz>`, `<page>`, `<module>`, and `<group>`:

```xml
<!-- BEFORE (unsafe to rename) -->
<assignment title="Homework 1" due_at="...">

<!-- STEP 1: add id first, keep title unchanged -->
<assignment id="Homework 1" title="Homework 1" due_at="...">

<!-- STEP 2 (separate edit): now safe to rename title -->
<assignment id="Homework 1" title="Homework 1 (Updated)" due_at="...">
```

### 3. Identify the Change

Determine what needs to change: dates, content, title, points, availability windows, question text, etc.

### 4. Reference the Tag Skill

Read the appropriate sub-skill for the resource type before editing.

- Assignment changes → read `../reference/canvas-tags/assignment/skill.md`
- Quiz changes → read `../reference/canvas-tags/quiz/skill.md`
- Page changes → read `../reference/canvas-tags/page/skill.md`
- Module or item changes → read `../reference/canvas-tags/module/skill.md`

### 5. Show the Proposed Change

Describe what will be modified and where. Wait for user confirmation before writing.

### 6. Make the Edit

Apply the confirmed change.

### 7. Validate

Run the 7-item checklist from `workflows/new-course/skill.md`.

If any checklist item fails: stop and fix before continuing.

### 8. Deploy (Optional)

If the user wants to push changes to Canvas, route to `../deploy/skill.md`.
