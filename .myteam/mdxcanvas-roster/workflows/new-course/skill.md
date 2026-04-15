---
name: new-course
description: Scaffold, design, and author a complete Canvas course from an outline, syllabus, lecture notes, or plain description.
---

# New Course Authoring

Use this workflow when the user has no existing course directory and wants to build a course from scratch.

## Non-Negotiables

- Do not create any files without first showing a plan table and receiving explicit user confirmation.
- Do not commit `course_info.json` or `.env` to source control.
- Do not change a resource's `title` without first setting `id` equal to the current title.
- Run the Validation Checklist (Step 5) before writing files and again after generating all content.

---

## Step 1: Intake

Ask the user the following questions. Wait for answers before proceeding.

- Do you have an existing course directory? If yes, stop — read `../update-resource/skill.md` instead.
- What are your source materials? (outline, syllabus, lecture notes, plain description, or a combination)
- What is the course start date and end date?
- How many weeks does the course run?
- What is the Canvas URL for your institution?

Do not proceed to Step 2 until all five questions are answered.

---

## Step 2: Scaffold

Create the following directory layout inside the new course directory:

```
<course-name>/
├── course_info.json
├── global_args.yaml
├── course.canvas.md.xml.jinja
├── content/
│   ├── assignments/
│   ├── quizzes/
│   ├── pages/
│   └── modules/
├── images/
└── files/
```

Create `course_info.json` with these placeholder fields:

```json
{
  "CANVAS_API_URL": "REPLACE_WITH_CANVAS_URL",
  "CANVAS_COURSE_ID": "REPLACE_WITH_COURSE_ID",
  "LOCAL_TIME_ZONE": "REPLACE_WITH_TIMEZONE"
}
```

Create `global_args.yaml` populated from the user's intake answers:

```yaml
term: REPLACE_WITH_TERM
year: REPLACE_WITH_YEAR
start_date: "REPLACE_WITH_START_DATE"
end_date: "REPLACE_WITH_END_DATE"
```

Create `course.canvas.md.xml.jinja` as a minimal entry point:

```xml
<div>
    <course-settings name="REPLACE_WITH_COURSE_NAME" code="REPLACE_WITH_COURSE_CODE"/>

    <syllabus>
        <include path="content/syllabus.md"/>
    </syllabus>

    <assignment-groups>
        <group name="Quizzes" weight="20"/>
        <group name="Assignments" weight="80"/>
    </assignment-groups>

    {# Content includes go here #}
</div>
```

Add `course_info.json` and `.env` to `.gitignore` if not already present.

---

## Step 3: Design

Read the user's source materials thoroughly before producing anything.

Apply the content type decision table to determine the correct tag for each piece of content:

| Task                              | Content Type          | Why                               |
|-----------------------------------|-----------------------|-----------------------------------|
| Explain a concept or show code    | `<page>`              | Static reference students revisit |
| Check comprehension               | `<quiz>`              | Low-stakes formative; auto-graded |
| Have students implement or submit | `<assignment>`        | Graded submission with due date   |
| Organize a week of content        | `<module>` + `<item>` | Canvas navigation container       |
| Distribute files or starter code  | `<file>` or `<zip>`   | Upload to Canvas files            |
| Course-wide notice                | `<announcement>`      | Pushed to students                |

Apply the Jinja decision rule to determine which resources need templates:

| Situation                                 | Approach                     |
|-------------------------------------------|------------------------------|
| >3 similar resources sharing structure    | Jinja template + args file   |
| Course-wide variables (term, year, dates) | `global_args.yaml`           |
| Single one-off resource                   | Static `.canvas.md.xml`      |
| Conditional content per section or term   | Jinja `{% if %}` in template |

Produce a plan table covering every resource to be created:

| Resource Type | Title | File Path | Notes |
|---------------|-------|-----------|-------|

Present the plan table to the user. Ask: "Shall I proceed?"

Do not write any files until the user confirms.

---

## Step 4: Author

Iterate through the confirmed plan table in order.

For each resource, read the appropriate reference sub-skill before writing:

- Quizzes → `../../reference/canvas-tags/quiz/skill.md`
- Assignments → `../../reference/canvas-tags/assignment/skill.md`
- Pages → `../../reference/canvas-tags/page/skill.md`
- Modules → `../../reference/canvas-tags/module/skill.md`

### When the plan table calls for a Jinja template

Read `../../reference/jinja/skill.md` before writing any `.jinja` file.

Follow these steps for every templated resource group:

1. **Create the args file first.** The args file defines the data; the template consumes it. Use a MarkdownData table (`.md`) for flat lists (e.g., 14 weekly quizzes with title and due date). Use a keyed MarkdownData file for rich per-item content (e.g., assignments with multi-line descriptions). Put the args file alongside the template (e.g., `content/quizzes/prep-quiz-args.md`).

2. **Write the template.** Name it `*.canvas.md.xml.jinja`. Loop over `args` using `{% for row in args %}`. Access columns by their header name: `{{ row['Title'] }}`, `{{ row['Due_At'] }}`. Use `| indent(8)` when inserting multi-line Markdown content.

3. **Include the template in the entry point.** In `course.canvas.md.xml.jinja`, add:
   ```xml
   <include path="content/quizzes/prep-quizzes.canvas.md.xml.jinja" args="content/quizzes/prep-quiz-args.md"/>
   ```

4. **Use global args for course-wide dates.** If the args file itself references term or date variables, give it a `.jinja` extension (e.g., `prep-quiz-args.md.jinja`) so global args are available inside it.

If a resource appears more than 3 times with the same structure and only data changing, it must use a template. Do not write it out statically.

### Apply the Typical Week Pattern for each week of the course:

1. Prep quiz — available the day before class, due at the start of class
2. Lecture page — reference material for the week
3. Assignment — in-class activity or homework, due later in the week
4. Module — groups all three items for Canvas navigation

Apply the quiz design guidelines when writing any quiz:

| Question Type                 | Target % |
|-------------------------------|----------|
| Multiple-choice               | 30–40%   |
| True/false                    | 20–30%   |
| Fill-in-the-blank or matching | 20–30%   |
| Multiple-answers or essay     | 10–20%   |

Additional quiz rules:

- Cover full topic breadth. Do not cluster on one subtopic.
- Use `shuffle_answers="true"` for all multiple-choice quizzes.
- Prep quizzes: 5–10 questions, `allowed_attempts="3"`, lower point value.
- Midterms and finals: use `time_limit`, `access_code`, and `allowed_attempts="1"`.

All date strings must use this exact format: `MMM d, yyyy, h:mm AM/PM`

Examples: `Jan 15, 2025, 11:59 PM` · `Aug 25, 2025, 9:00 AM`

No other date format is valid.

---

## Step 5: Validate

Run this checklist before writing files and again after all content is generated.

- [ ] Every `<item content_id>` matches an existing resource `id` (or `title` if no `id` was set)
- [ ] All date strings use `MMM d, yyyy, h:mm AM/PM` format
- [ ] Every `assignment_group` value matches a `<group>` defined in `<assignment-groups>`
- [ ] Module items reference content included somewhere in the same entry point
- [ ] `.jinja` templates loop with the correct access pattern for the args format used
- [ ] `course_info.json` and `.env` are not committed to source control
- [ ] When modifying an existing resource: if it has no `id`, set `id` equal to the current `title` before any other
  edits

Fix all checklist failures before proceeding to Step 6.

---

## Step 6: Deploy

Route to `../deploy/skill.md`.
