---
skill: jinja
---

# Jinja Templating

## When to Use This Reference

Use this reference whenever a request involves:

- Writing or editing a `.jinja` template file
- Creating an args file (MarkdownData, YAML, JSON)
- Using Jinja variables, macros, loops, or filters in MDXCanvas
- Understanding `global_args` vs per-template `args`
- Using MDXCanvas-injected functions (`glob`, `load`, `search`, `read_file`, etc.)
- Passing `--global-args` or `--args` to the CLI

If a file has `.jinja` in its extension, read this reference before editing it.

## Non-Negotiables

- Use a Jinja template when the same tag structure would be copy-pasted more than 3 times with only data changing.
- Always call `.group()` on the result of `search()` — it returns a match object, not a string.
- Use `| indent()` filter when inserting multi-line content into a template.
- Do not mix `--global-args` and `--args` up. Global args are course-wide; template args are per-run.

---

## Building a Template from Scratch

Use this pattern whenever the same tag structure repeats more than 3 times with only data changing.

**Example:** 14 weekly prep quizzes that share the same structure.

**Step 1 — Create the args file** (`content/quizzes/prep-quiz-args.md`):

```md
| Title              | Due_At                  | Available_From          |
|--------------------|-------------------------|-------------------------|
| Week 1 Prep Quiz   | Jan 14, 2025, 9:00 AM   | Jan 13, 2025, 12:00 PM  |
| Week 2 Prep Quiz   | Jan 21, 2025, 9:00 AM   | Jan 20, 2025, 12:00 PM  |
| Week 3 Prep Quiz   | Jan 28, 2025, 9:00 AM   | Jan 27, 2025, 12:00 PM  |
```

Each row becomes one quiz. Column headers become dict keys.

**Step 2 — Write the template** (`content/quizzes/prep-quizzes.canvas.md.xml.jinja`):

```xml
{% for row in args %}
<quiz id="{{ row['Title'] | lower | replace(' ', '-') }}"
      title="{{ row['Title'] }}"
      due_at="{{ row['Due_At'] }}"
      available_from="{{ row['Available_From'] }}"
      assignment_group="Quizzes"
      shuffle_answers="true"
      allowed_attempts="3"
      scoring_policy="keep_highest">

    <description>
        Complete before class.
    </description>

    <questions>
        <question type="multiple-choice">
            [Question text here]
            <correct>[Correct answer]</correct>
            <incorrect>[Wrong answer]</incorrect>
        </question>
    </questions>
</quiz>
{% endfor %}
```

**Step 3 — Include the template in the entry point** (`course.canvas.md.xml.jinja`):

```xml
<include path="content/quizzes/prep-quizzes.canvas.md.xml.jinja"
         args="content/quizzes/prep-quiz-args.md"/>
```

**Step 4 — Reference each quiz in modules** using the `id` you generated in the template:

```xml
<module id="week-1" title="Week 1">
    <item type="quiz" content_id="week-1-prep-quiz" indent="1"/>
</module>
```

**If the args file needs global variables** (e.g., dates defined in `global_args.yaml`), rename it to `prep-quiz-args.md.jinja`. The file will be rendered with global args before being parsed as a table.

---

## How Jinja Processing Works

Files with the `.jinja` extension are rendered through Jinja2 first, then parsed as XML/Markdown.

Processing order:

1. Global args are loaded from `global_args.yaml` (or `.json`)
2. Template args are loaded from the `--args` file (if provided)
3. The `.jinja` file is rendered with all args in context
4. The rendered output is parsed as normal MDXCanvas XML

When a file is included via `<include path="file.jinja" args="args.md"/>`, the same rendering happens inline.

---

## Global Args vs Template Args

| Type          | Flag                             | Scope                          | Variable in Template                             |
|---------------|----------------------------------|--------------------------------|--------------------------------------------------|
| Global args   | `--global-args global_args.yaml` | Every `.jinja` file in the run | Top-level variables (`{{ term }}`, `{{ year }}`) |
| Template args | `--args homework_args.md`        | Single template run            | `args` variable (`{{ args[0]['Title'] }}`)       |

Global args example (`global_args.yaml`):

```yaml
term: Fall
year: 2025
start_date: "Aug 25, 2025"
end_date: "Dec 12, 2025"
```

Use in any template: `{{ term }} {{ year }}`

Template args are passed as the `args` variable — a list of dicts (from a table) or a dict of dicts (from a keyed file).

---

## MDXCanvas Jinja Functions

These functions are injected into every template context automatically:

| Function     | Signature                 | Description                                                                                      |
|--------------|---------------------------|--------------------------------------------------------------------------------------------------|
| `zip`        | `zip(a, b)`               | Standard Python zip — parallel iteration over two lists                                          |
| `enumerate`  | `enumerate(seq)`          | Index + value pairs                                                                              |
| `split_list` | `split_list(x)`           | Split string on `";"` delimiter, returns list                                                    |
| `exists`     | `exists(path)`            | Check if file exists relative to template's parent folder                                        |
| `read_file`  | `read_file(path)`         | Read file contents as string (relative to template)                                              |
| `glob`       | `glob(pattern)`           | List files matching glob pattern; returns sorted relative paths                                  |
| `parent`     | `parent(path)`            | Parent directory of a path string                                                                |
| `load`       | `load(path)`              | Load JSON/YAML/CSV/MarkdownData file as Python dict or list                                      |
| `debug`      | `debug(msg)`              | Log a debug message (visible with `--debug` flag)                                                |
| `get_arg`    | `get_arg(key, default)`   | Get a global arg by key with optional fallback                                                   |
| `search`     | `search(pattern, string)` | Regex search (`re.search`) — returns a **match object**; use `.group(1)` for first capture group |

---

## Template Patterns

### Variables (`{% set %}`)

```jinja
{% set folder = parent(lecture_file) %}
{% set code = search('lecture(\d\w)', folder).group(1) %}
{% set title = code ~ " - " ~ data['content']['Title'] %}
```

Use `~` for string concatenation.

### Comments (`{# ... #}`)

```jinja
{# This module is disabled for W26 #}
{# <module id="unit4" title="Unit 4"> #}
```

### Macros (`{% macro %}`)

Macros avoid repetitive block construction. Define once, call many times:

```jinja
{% macro lecture_items(code) %}
    <item content_id="{{ code }}-lecture" type="assignment"/>
    <item content_id="{{ code }}-quiz" type="quiz" indent="1"/>
    <item content_id="{{ code }}-homework" type="assignment" indent="1"/>
{% endmacro %}

{{ lecture_items("1a") }}
{{ lecture_items("1b") }}
```

### Loop Variables

Inside any `{% for %}` loop, Jinja provides:

| Variable      | Value                       |
|---------------|-----------------------------|
| `loop.index`  | Current iteration (1-based) |
| `loop.index0` | Current iteration (0-based) |
| `loop.first`  | `True` on first iteration   |
| `loop.last`   | `True` on last iteration    |

```jinja
{% for heading, question in data['Quiz']['Questions'].items() %}
<question type="essay" id="midterm-q{{ loop.index0 }}">
    {{ question }}
</question>
{% endfor %}
```

### `| indent()` Filter

Preserves multi-line markdown formatting when inserting variable content:

```jinja
{{ data['Homework']['Assignment'] | indent(8) }}
{{ data['Lecture']['Outline'] | indent(16, blank=True) }}
```

`blank=True` also indents blank lines, which is needed to preserve markdown paragraph breaks.

### `search()` — Use `.group()` for Capture Groups

`search()` is `re.search` and returns a **match object**, not a string. Always call `.group()`:

```jinja
{% set code = search('unit(\\d+)/day(\\w+)/', path).group(2) %}
{% set id = search('/([^/\\.]+)\\.[^/]*$', filepath).group(1) %}
```

Use `.group(0)` for the full match, `.group(1)` for the first capture group.

---

## Common Loop Patterns

### For loop over MarkdownData table (list of dicts)

```xml
{% for hw in args %}
<assignment title="{{ hw['Title'] }}"
            due_at="{{ hw['Due_At'] }}"
            points_possible="{{ hw['Points_Possible'] }}"
            assignment_group="Homework">

    # {{ hw['Title'] }}

    Complete the assignment by the due date.
</assignment>
        {% endfor %}
```

### For loop over keyed MarkdownData file (dict of dicts)

```xml
{% for title, info in args.items() %}
<assignment title="{{ title }}"
            due_at="{{ info['content']['Due_At'] }}"
            points_possible="{{ info['content']['Points_Possible'] }}"
            assignment_group="Homework">

    # {{ title }}

    {{ info['Description'] }}
</assignment>
        {% endfor %}
```

### Conditional content

```xml
{% if get_arg('section') == 'online' %}
<page title="Online Section Info">
    This section meets asynchronously.
</page>
        {% endif %}
```

### Load an external args file inside a template

```xml
{% set items = load('content/data/topics.yaml') %}
        {% for item in items %}
<page title="{{ item['title'] }}">
    {{ item['description'] }}
</page>
        {% endfor %}
```

### Using `glob` to include all files in a directory

```xml
{% for path in glob('content/pages/*.md') %}
<md-page path="{{ path }}"/>
        {% endfor %}
```

---

## CLI Commands

```bash
# Run a template with global args
mdxcanvas --course-info course_info.json --global-args global_args.yaml course.canvas.md.xml.jinja

# Run a template with per-run args
mdxcanvas --course-info course_info.json --args homework_args.md homework.canvas.md.xml.jinja

# Specify additional template search paths
mdxcanvas --course-info course_info.json --templates templates/ course.canvas.md.xml.jinja
```

Args file formats supported: `.json`, `.yaml`, `.csv`, `.md`/`.mdd`

> **Args files can themselves be Jinja templates.** Add `.jinja` to their extension (e.g., `homework-args.md.jinja`).
> The file is rendered with global args before being parsed as MarkdownData/YAML/etc. This lets you use
`{{ RSA_HW_1_DUE_AT }}` and other global args inside date cells of an args table.

---

## Args File Formats

### MarkdownData Table (recommended for lists)

```md
| Title      | Due_At                 | Points_Possible |
|------------|------------------------|-----------------|
| Homework 1 | Jan 15, 2025, 11:59 PM | 100             |
| Homework 2 | Jan 22, 2025, 11:59 PM | 100             |
```

Access: `{% for hw in args %}` → `{{ hw['Title'] }}`, `{{ hw['Due_At'] }}`

### MarkdownData Keyed File (for rich content with multi-line text per item)

```md
# Homework 1

===
Due_At: Jan 15, 2025, 11:59 PM
Points_Possible: 100
===

Complete exercises 1-5 from Chapter 3.

# Homework 2

===
Due_At: Jan 22, 2025, 11:59 PM
Points_Possible: 100
===

Complete exercises 6-10 from Chapter 3.
```

Access: `{% for title, info in args.items() %}` → `{{ title }}`, `{{ info['content']['Due_At'] }}`,
`{{ info['Description'] }}`

### JSON

```json
[
  {
    "title": "Homework 1",
    "due_at": "Jan 15, 2025, 11:59 PM",
    "points": 100
  },
  {
    "title": "Homework 2",
    "due_at": "Jan 22, 2025, 11:59 PM",
    "points": 100
  }
]
```
