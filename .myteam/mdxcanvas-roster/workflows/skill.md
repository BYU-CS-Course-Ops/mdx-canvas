---
name: workflows
description: Route to the correct end-to-end workflow for generating, updating, or deploying a Canvas course.
---

# Workflows

Determine which workflow applies before proceeding.

## Routing

If the user has no existing course directory and wants to build a course from source materials (outline, syllabus,
notes, or a plain description), read `new-course/skill.md`.

If the user has an existing course directory and wants to edit or add resources, read `update-resource/skill.md`.

If the user wants to push content to Canvas, read `deploy/skill.md`.

If the request involves both authoring and deploying, read `new-course/skill.md` first. It routes to `deploy/skill.md`
at Phase 6.
