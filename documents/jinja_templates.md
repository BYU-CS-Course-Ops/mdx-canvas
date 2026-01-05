# Jinja Templates

A powerful feature of MDXCanvas is the ability to use **Jinja templates** to generate dynamic course content. This is especially useful for homeworks, projects, or other assignments with shared structure but varying details — such as due dates, names, or point values.

Templates allow you to define reusable structures, then fill in specific values using variables.

Each template begins with a content tag (e.g., `<assignment>`, `<quiz>`, `<page>`), and can include Jinja logic to generate variations.

## Global Arguments

Global arguments define course-wide variables (e.g., term, start date, grading weights). These are passed to MDXCanvas via a JSON file.

**Example `global_args.json`:**

```json
{
  "term": "Fall",
  "year": 2025,
  "start_date": "Aug 1, 2025",
  "end_date": "Dec 15, 2025"
}
```

Run a Jinja template with global arguments using:

```bash
mdxcanvas --course-info <course_info> --global-args <global_args.json> <template.jinja>
```

### Assignment Group Weights

You can optionally include a `Group_Weights` key to define how much each assignment group contributes to the final grade.

```json
{
  "Group_Weights": {
    "Homework": 40,
    "Quizzes": 20,
    "Projects": 30,
    "Final Exam": 10
  }
}
```

MDXCanvas will apply these weights during course creation.

## Template Arguments

Template arguments define values specific to individual items (e.g., a list of assignments). These can be defined using:

* A separate **JSON** file
* Inline in the Jinja template
* A **MarkdownData table** (recommended)

Run a Jinja template with arguments using:

```bash
mdxcanvas --course-info <course_info> --args <args> <template.jinja>
```

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

You can then use `args.items()` to loop over each new obejct in a Jinja template.

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