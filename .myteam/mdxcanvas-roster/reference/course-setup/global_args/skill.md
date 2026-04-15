---
name: global_args Reference
description: Format, fields, and usage of global_args.yaml for course-wide Jinja variables.
---

# Global Args

## When to Use This Reference

Use this reference when looking up:

- Format and fields for `global_args.yaml`
- Course-wide Jinja variables like `{{ term }}`, `{{ year }}`, or `{{ start_date }}`
- The `--global-args` CLI flag
- The difference between global args and per-template args

## Non-Negotiables

- Do not put credentials in `global_args.yaml`. Credentials belong in `course_info.json` and `.env` only.
- `global_args.yaml` is safe to commit — it contains no secrets.
- Use `--global-args` for course-wide variables. Use `--args` for per-template data. Do not confuse the two.

---

## What Global Args Are

Global args are course-wide Jinja2 variables available in every `.jinja` template file in the course. They define things
like the term name, year, course start and end dates, and assignment group weights.

Unlike per-template args (which apply to one template), global args apply to all templates when passed via
`--global-args`.

---

## Naming

Both `global_args.yaml` and `global-args.yaml` are common. Either works — the filename is passed explicitly via
`--global-args`.

---

## global_args.yaml Format

```yaml
# global_args.yaml
# Course-wide Jinja variables. Committed to source control (no credentials here).

term: fall2025
year: 2025
start_date: "Aug 25, 2025"
end_date: "Dec 12, 2025"
final_exam: "Dec 15, 2025, 11:00 AM"

# Assignment group weights (used in <assignment-groups> or referenced in templates)
Group_Weights:
  Homework: 40
  Quizzes: 20
  Projects: 30
  Final Exam: 10
```

Common fields:

| Field           | Description                 | Example                  |
|-----------------|-----------------------------|--------------------------|
| `term`          | Semester + year slug        | `fall2025`               |
| `year`          | Academic year               | `2025`                   |
| `start_date`    | Course start date           | `Aug 25, 2025`           |
| `end_date`      | Course end date             | `Dec 12, 2025`           |
| `final_exam`    | Final exam date and time    | `Dec 15, 2025, 11:00 AM` |
| `Group_Weights` | Dict of grade group weights | see above                |

---

## Using Global Args in Templates

Reference any global arg with `{{ variable_name }}`:

```xml
<!-- In any .jinja file -->
<quiz title="Midterm Exam"
      due_at="{{ final_exam }}"
      assignment_group="Exams">
    <description>
        This exam covers material from {{ term }} {{ year }}.
        The course runs from {{ start_date }} to {{ end_date }}.
    </description>
    ...
</quiz>
```

Loop over group weights:

```xml
<assignment-groups>
    {% for group, weight in Group_Weights.items() %}
    <group name="{{ group }}" weight="{{ weight }}" />
    {% endfor %}
</assignment-groups>
```

---

## Passing Global Args via CLI

Use the `--global-args` flag:

```bash
mdxcanvas \
    --course-info course_info.json \
    --global-args global_args.yaml \
    course.canvas.md.xml.jinja
```

`--global-args` applies to the entire course entry point and all its `<include>` files. Use `--args` (not
`--global-args`) when running a single template with per-item data.
