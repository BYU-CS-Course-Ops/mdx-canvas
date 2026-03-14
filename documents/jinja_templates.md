# Jinja Templates

A powerful feature of MDXCanvas is the ability to use **Jinja templates** to generate dynamic course content. This is especially useful for homeworks, projects, or other assignments with shared structure but varying details — such as due dates, names, or point values.

Templates allow you to define reusable structures, then fill in specific values using variables.

Each template begins with a content tag (e.g., `<assignment>`, `<quiz>`, `<page>`), and can include Jinja logic to generate variations.

## Global Arguments

Global arguments define course-wide variables (e.g., term, start date, grading weights). These are passed to MDXCanvas from two sources:

1. **`GLOBAL_ARGS` in `course_info` file** - Course-wide defaults
2. **`--global-args` CLI argument** - Runtime overrides/extensions

Both sources are **merged together** at deployment time, with CLI arguments taking precedence.

### Example: Multiple Course Instances

You can use this to deploy the same course content in different ways:

**File structure:**
```
course_info_fall.yaml          # Fall semester config
course_info_spring.yaml        # Spring semester config
global_args_fall.yaml          # Fall-specific variables
global_args_spring.yaml        # Spring-specific variables
content/course.canvas.md.xml   # Single content file
```

**`course_info_fall.yaml`:**
```yaml
CANVAS_API_URL: https://byu.instructure.com/
CANVAS_COURSE_ID: 12345
LOCAL_TIME_ZONE: America/Denver
DEPLOY_ROOT: ..
GLOBAL_ARGS:
  semester: Fall 2025
  start_date: Aug 25, 2025
  instructor_name: Dr. Smith
```

**`global_args_fall.yaml`:**
```yaml
# Overrides/extends GLOBAL_ARGS from course_info
semester: Fall 2025 (Section A)
syllabus_deadline: Aug 30, 2025, 11:59 PM
```

**Deploy fall semester:**
```bash
mdxcanvas --course-info course_info_fall.yaml \
          --global-args global_args_fall.yaml \
          content/course.canvas.md.xml
```

**Deploy spring semester with same content:**
```bash
mdxcanvas --course-info course_info_spring.yaml \
          --global-args global_args_spring.yaml \
          content/course.canvas.md.xml
```

The **CLI `--global-args` values override** `GLOBAL_ARGS` from `course_info` if there are conflicts, allowing you to:
- Keep semester-independent defaults in `course_info`
- Override them per deployment with CLI arguments
- Share a single content file across multiple course instances

### GLOBAL_ARGS Merging Priority

1. **Base**: `GLOBAL_ARGS` from `course_info` file
2. **Override**: Values from `--global-args` CLI file (these take precedence)

All merged keys are spread directly into every Jinja template context as top-level variables.

Example with merging:
```yaml
# course_info.yaml GLOBAL_ARGS
GLOBAL_ARGS:
  semester: Fall
  year: 2025
  instructor: Dr. Smith
```

```yaml
# global_args.yaml (CLI)
year: 2026  # OVERRIDES course_info
department: Computer Science  # NEW variable
```

**Result in templates**: `{{ semester }}` → "Fall", `{{ year }}` → "2026", `{{ department }}` → "Computer Science"

## Template Arguments

Template arguments define values specific to individual items (e.g., a list of assignments). These are loaded from a separate file and injected into the template as the `args` variable.

Run a Jinja template with arguments using:

```bash
mdxcanvas --course-info <course_info> --args <args_file> <template.jinja>
```

### Supported `--args` File Formats

| Extension | Format | `args` type |
|-----------|--------|-------------|
| `.json` | JSON | `dict` or `list` |
| `.csv` | CSV | `list[dict]` |
| `.yaml` / `.yml` | YAML | `dict` or `list` |
| `.md` / `.mdd` | MarkdownData (recommended) | `dict` or `list[dict]` |
| `.jinja` | Jinja template (rendered with `global_args` first, then parsed) | any of the above |

Similarly, the `--global-args` file accepts `.yaml`, `.yml`, `.json`, `.md`, and `.mdd` formats.

### Example using MarkdownData on a table

```md
| Title                | Due_At                 | Points_Possible |
|----------------------|------------------------|-----------------|
| Example Assignment 1 | Jan 1, 2025, 11:59 PM  | 100             |
| Example Assignment 2 | Jan 8, 2025, 11:59 PM  | 50              |
| Example Assignment 3 | Jan 15, 2025, 11:59 PM | 75              |
```

MDXCanvas (via [MarkdownData](https://github.com/BYU-CS-Course-Ops/markdowndata)) will convert this table into a list of dictionaries.

### Example using MarkdownData on a `.md` File

```md
# Homework 1

===
Due_At: Jan 1, 2025, 11:59 PM
Points_Possible: 100
===

## Description

This is the HW 1 instructions

# Homework 2

===
Due_At: Jan 8, 2025, 11:59 PM
Points_Possible: 50
===

## Description

This is the HW 2 instructions

# Homework 3

===
Due_At: Jan 15, 2025, 11:59 PM
Points_Possible: 75
===

## Description

This is the HW 3 instructions
```

MDXCanvas—which uses [MarkdownData](https://github.com/BYU-CS-Course-Ops/markdowndata)—interprets this file as the
following JSON:

```json
{
    "Homework 1": {
        "content": {
            "Due_At": "Jan 1, 2025, 11:59 PM",
            "Points_Possible": 100
        },
        "Description": "This is the HW 1 instructions"
    },
    ...
    "Homework 3": {
        "content": {
            "Due_At": "Jan 15, 2025, 11:59 PM",
            "Points_Possible": 75
        },
        "Description": "This is the HW 3 instructions"
    }
}
```

You can then use `args.items()` to loop over each entry in a Jinja template.

## Jinja Example

```xml
<assignment title="{{ assignment_name }}"
            due_at="{{ due_date }}"
            available_from="{{ available_from }}"
            available_to="{{ available_to }}"
            points_possible="{{ points_possible }}"
            assignment_group="{{ assignment_group }}">

    <description>
        # {{ assignment_name }}

        Please complete the assignment by the due date.

        ## Instructions

        {{ instructions }}
    </description>
</assignment>
```

## Advanced Features & Tips

### Template Context Functions

Every Jinja template has access to the following built-in functions in addition to all global args:

| Function | Description |
|----------|-------------|
| `read_file(path)` | Read a file's text content relative to the template's directory |
| `load(path)` | Load and parse a data file (`.json`, `.csv`, `.yaml`, `.md`) relative to the template's directory |
| `glob(pattern)` | Return a sorted list of file paths matching a glob pattern, relative to the template's directory |
| `exists(path)` | Return `True` if a file exists relative to the template's directory |
| `parent(path)` | Return the parent directory of a path as a string |
| `get_arg(key[, default])` | Look up a value from global args (equivalent to `global_args.get(key, default)`) |
| `split_list(s)` | Split a semicolon-delimited string into a list |
| `search(pattern, string)` | Run `re.search` — useful for conditional logic based on string content |
| `zip(...)` | Python built-in `zip` |
| `enumerate(...)` | Python built-in `enumerate` |
| `debug(msg)` | Log a debug message (visible with `--debug`) |

**Example — reading an external file into a page:**

```xml
<page title="Lecture Notes">
  <content>
    {{ read_file('notes/week1.md') }}
  </content>
</page>
```

**Example — loading a data file and looping over it:**

```xml
{% for hw in load('data/homeworks.yaml') %}
<assignment title="{{ hw['title'] }}" due_at="{{ hw['due_at'] }}">
  <description>{{ hw['description'] }}</description>
</assignment>
{% endfor %}
```

**Example — listing all `.qmd` slides files dynamically:**

```xml
{% for slide_file in glob('slides/*.qmd') %}
<page title="{{ parent(slide_file) }} Slides">
  <content>{{ read_file(slide_file) }}</content>
</page>
{% endfor %}
```

### Multi-Environment Deployments Using GLOBAL_ARGS

One powerful pattern is using `GLOBAL_ARGS` to conditionally deploy different content based on which course instance you're deploying to. Create a separate args file for each environment:

**`prod_args.yaml`:**
```yaml
environment: production
```

**`sandbox_args.yaml`:**
```yaml
environment: sandbox
```

**`content.jinja`:**
```xml
{% if environment == 'production' %}
<assignment title="Graded Assignment" points_possible="100" />
{% elif environment == 'sandbox' %}
<assignment title="Practice Assignment (AUTO-GRADED)" points_possible="0" />
{% endif %}
```

Then deploy with an environment-specific args file:
```bash
# Production deployment
mdxcanvas --course-info prod_course_info.yaml \
          --global-args prod_args.yaml \
          content.jinja

# Testing/sandbox deployment
mdxcanvas --course-info sandbox_course_info.yaml \
          --global-args sandbox_args.yaml \
          content.jinja
```

### Conditional Content Based on Course Instance

Another use case: deploy different due dates based on which semester/section:

```jinja
{% if semester == 'Fall' %}
  {% set assignment_due = due_date_fall %}
{% elif semester == 'Spring' %}
  {% set assignment_due = due_date_spring %}
{% endif %}

<assignment title="Homework 1" due_at="{{ assignment_due }}">
  ...
</assignment>
```

Define semester-specific defaults in `course_info` GLOBAL_ARGS, and they'll be available throughout all templates.

### Varying Assignment Group Weights Per Deployment

You can pass group weight values through `GLOBAL_ARGS` and reference them inside your `<assignment-groups>` template. This is just a naming convention — MDXCanvas does not process `Group_Weights` automatically; your template is responsible for reading it.

**`global_args_custom.yaml`:**
```yaml
Group_Weights:
  Homework: 40
  Quizzes: 20
  Projects: 30
  Final Exam: 10
```

**`course.canvas.md.xml.jinja`:**
```xml
<assignment-groups>
  <group id="hw"    name="Homework"   weight="{{ Group_Weights['Homework']   | default(40) }}" />
  <group id="quiz" name="Quizzes"    weight="{{ Group_Weights['Quizzes']    | default(20) }}" />
  <group id="proj" name="Projects"   weight="{{ Group_Weights['Projects']   | default(30) }}" />
  <group id="exam" name="Final Exam" weight="{{ Group_Weights['Final Exam'] | default(10) }}" />
</assignment-groups>
```

```bash
mdxcanvas --course-info course_info.yaml \
          --global-args global_args_custom.yaml \
          course.canvas.md.xml.jinja
```

### Tips for Template Development

1. **Use descriptive argument names**: Instead of `var1`, `var2`, use `assignment_title`, `due_date`
2. **Provide defaults**: Use Jinja `{{ variable | default('Default Value') }}` for optional template arguments
3. **Validate in templates**: Use conditional checks to ensure required variables are present
4. **Keep templates modular**: Create separate `.jinja` files for different content types

## Looping Over Template Args

### From MarkdownData (or a list of dicts)

```xml
{% for assignment in args %}

<assignment title="{{ assignment['Title'] }}"
            due_at="{{ assignment['Due_At'] }}"
            points_possible="{{ assignment['Points_Possible'] }}">

    <description>
        # {{ assignment["Title"] }}

        Please complete the assignment by the due date.
    </description>
</assignment>

{% endfor %}
```

### From JSON (keyed by assignment name)

```xml
{% for assignment_title, assignment_info in args.items() %}

<assignment title="{{ assignment_title }}"
            due_at="{{ assignment_info['due_at'] }}"
            points_possible="{{ assignment_info['points_possible'] }}">

    <description>
        # {{ assignment_title }}

        Please complete the assignment by the due date.
    </description>
</assignment>

{% endfor %}
```
