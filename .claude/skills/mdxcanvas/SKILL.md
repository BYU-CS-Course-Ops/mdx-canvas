---
name: mdxcanvas
description: MDXCanvas hub skill — understand course structure, generate Canvas resources, and deploy to Canvas. Routes to the right sub-skill for any MDXCanvas task.
license: Complete terms in LICENSE.txt
---

# MDXCanvas

MDXCanvas is a CLI tool that converts XML/Markdown/Jinja source files into Canvas LMS resources — quizzes, assignments,
pages, modules, announcements, and full courses — through a single `mdxcanvas` command.

## What MDXCanvas Does

- Reads `.canvas.md.xml` (or `.jinja`) files from your course directory
- Parses XML tags (`<quiz>`, `<assignment>`, `<page>`, `<module>`, etc.)
- Renders Markdown inside those tags
- Uploads everything to Canvas via the API

## Typical Workflow

```
1. Scaffold or locate course directory
2. Write (or generate) content files using MDXCanvas tags
3. Run: mdxcanvas --course-info <course_info.json> <entry_file>
```

## Sub-Skill Routing

When the user asks you to do something, **read the appropriate sub-skill file** before responding. Use the table below
to choose:

| User Goal                                                                    | Read This File                                       |
|------------------------------------------------------------------------------|------------------------------------------------------|
| Understand or scaffold course directory structure                            | `.claude/skills/mdxcanvas/course-structure/SKILL.md` |
| Learn about Canvas resource tags (quiz, assignment, page, module, etc.)      | `.claude/skills/mdxcanvas/canvas-resources/SKILL.md` |
| Learn about special/helper tags (include, file, img, zip, course-link, etc.) | `.claude/skills/mdxcanvas/special-tags/SKILL.md`     |
| Use Jinja templates or MarkdownData args files                               | `.claude/skills/mdxcanvas/templating/SKILL.md`       |
| Generate any Canvas resource (quiz, assignment, page, full course)           | `.claude/skills/mdxcanvas/generate-content/SKILL.md` |
| Deploy content to Canvas                                                     | `.claude/skills/mdxcanvas/deploy/SKILL.md`           |

All paths are repo-root-relative. Read the sub-skill file before taking any action.

## How This Works

When the user invokes this skill or asks a question that touches MDXCanvas:

1. Identify which sub-skill applies from the routing table above.
2. Read that sub-skill's `SKILL.md` using the Read tool.
3. Follow the instructions in that sub-skill.
4. If the task spans multiple sub-skills (e.g., generate then deploy), read each relevant sub-skill in order.

## Quick Reference

### File Extensions

| Extension                               | Purpose                                     |
|-----------------------------------------|---------------------------------------------|
| `.canvas.md.xml`                        | Static MDXCanvas content file               |
| `.canvas.md.xml.jinja`                  | Jinja template (rendered before processing) |
| `course_info.json`                      | Canvas API credentials + course ID          |
| `global_args.json` / `global_args.yaml` | Course-wide Jinja variables                 |

### CLI Flags

```bash
# Basic deploy
mdxcanvas --course-info <course_info.json> <content_file>

# With Jinja global args
mdxcanvas --course-info <course_info> --global-args <global_args.json> <template.jinja>

# With per-template args
mdxcanvas --course-info <course_info> --args <args_file> <template.jinja>
```

### Key Documents

For complete tag reference, read the documents in this repo:

- `documents/supported_tags/supported_tags.md` — all Canvas resource tags
- `documents/special_tags/special_tags.md` — all special/helper tags
- `documents/jinja_templates.md` — Jinja + MarkdownData reference
