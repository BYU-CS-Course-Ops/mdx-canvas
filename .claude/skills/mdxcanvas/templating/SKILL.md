---
name: mdxcanvas/templating
description: Use Jinja2 templates and MarkdownData args files to generate repeated Canvas resources (assignments, quizzes, pages) from a single template.
license: Complete terms in ../LICENSE.txt
---

# Templating with Jinja2 and MarkdownData

MDXCanvas supports Jinja2 templates for generating repeated content — e.g., 10 homework assignments that share the same
structure but have different titles, due dates, and point values. This eliminates manual duplication.

For the full reference, read `documents/jinja_templates.md`.

## How It Works

1. Write a `.jinja` template containing MDXCanvas tags with `{{ variable }}` placeholders
2. Write an args file (MarkdownData table or JSON) with values for each instance
3. Run: `mdxcanvas --course-info <course_info> --args <args_file> <template.jinja>`

MDXCanvas renders the Jinja template with the args, then processes the resulting XML.

---

## Args File Formats

### MarkdownData Table (Recommended)

A Markdown table where each row becomes one item. Column headers become variable names.

```md
| Title        | Due_At                | Points_Possible |
|--------------|-----------------------|-----------------|
| Homework 1   | Jan 15, 2025, 11:59 PM | 100            |
| Homework 2   | Jan 22, 2025, 11:59 PM | 100            |
| Homework 3   | Jan 29, 2025, 11:59 PM | 50             |
```

Access in template: `{% for item in args %}` → `{{ item['Title'] }}`, `{{ item['Due_At'] }}`

### MarkdownData Keyed File (For Rich Content)

A `.md` file where each `# Heading` is a key and `=== ... ===` blocks are metadata:

```md
# Homework 1

===
Due_At: Jan 15, 2025, 11:59 PM
Points_Possible: 100
===

## Instructions

Complete exercises 1-5 from Chapter 3.

# Homework 2

===
Due_At: Jan 22, 2025, 11:59 PM
Points_Possible: 100
===

## Instructions

Complete exercises 6-10 from Chapter 4.
```

Access in template: `{% for title, info in args.items() %}` → `{{ title }}`, `{{ info['content']['Due_At'] }}`

### JSON

```json
[
    {"title": "Homework 1", "due_at": "Jan 15, 2025, 11:59 PM", "points": 100},
    {"title": "Homework 2", "due_at": "Jan 22, 2025, 11:59 PM", "points": 100}
]
```

---

## Global Args

Global args define course-wide variables passed to every template. They use `--global-args` instead of `--args`.

```bash
mdxcanvas --course-info course_info.json --global-args global_args.yaml course.canvas.md.xml.jinja
```

Common global args fields (see `global_args.yaml` in course root):

```yaml
term: fall2025
year: 2025
start_date: "Aug 25, 2025"
end_date: "Dec 12, 2025"
```

Use in any template: `{{ term }}`, `{{ year }}`, `{{ start_date }}`

---

## Template Examples

### Simple: Loop Over Table Args

See `examples/assignments.jinja` for a complete example.

```xml
{% for hw in args %}
<assignment
    title="{{ hw['Title'] }}"
    due_at="{{ hw['Due_At'] }}"
    points_possible="{{ hw['Points_Possible'] }}"
    assignment_group="Homework">

    # {{ hw['Title'] }}

    Complete the assignment and submit by the due date.
</assignment>
{% endfor %}
```

With the args table in `examples/assignments_table.md`:

```md
| Title      | Due_At                 | Points_Possible |
|------------|------------------------|-----------------|
| Homework 1 | Jan 15, 2025, 11:59 PM | 100             |
| Homework 2 | Jan 22, 2025, 11:59 PM | 100             |
```

Run:

```bash
mdxcanvas --course-info course_info.json --args examples/assignments_table.md examples/assignments.jinja
```

### Using Global Args

```xml
<quiz title="Midterm Exam"
      due_at="{{ final_exam }}"
      assignment_group="Exams">
    <description>
        This exam covers material from {{ term }} {{ year }}.
    </description>
    ...
</quiz>
```

### Conditional Content

```xml
{% for hw in args %}
<assignment
    title="{{ hw['Title'] }}"
    due_at="{{ hw['Due_At'] }}"
    points_possible="{{ hw['Points_Possible'] }}"
    {% if hw.get('Submission_Type') %}submission_types="{{ hw['Submission_Type'] }}"{% endif %}
    assignment_group="Homework">

    {{ hw.get('Description', 'Complete the assignment by the due date.') }}
</assignment>
{% endfor %}
```

---

## File Naming Conventions

| File               | Pattern                                |
|--------------------|----------------------------------------|
| Jinja template     | `<topic>.canvas.md.xml.jinja`          |
| MarkdownData table | `<topic>_args.md` or `<topic>_args.md` |
| JSON args          | `<topic>_args.json`                    |

Keep template and args file together in the same directory.

---

## How This Works

When asked to create or explain a Jinja template:

1. Determine which resource type is being templated (assignment, quiz, page).
2. Ask for the args data (titles, dates, points) if not provided.
3. Create the `.jinja` template file.
4. Create the args file (prefer MarkdownData table format).
5. Show the `mdxcanvas` command to run them together.
6. Offer to include the template in the course entry point via `<include>`.

For complete Jinja + MarkdownData documentation, read `documents/jinja_templates.md`.
