# Course Info

The `course_info` file is a configuration file used to define key settings for your Canvas course deployment via
**MDXCanvas**.

## Supported Formats

- **YAML** (`.yaml`, `.yml`) - Recommended format for readability
- **JSON** (`.json`) - Standard JSON format
- **MarkdownData** (`.md`, `.mdd`) - See [MarkdownData documentation](https://github.com/BYU-CS-Course-Ops/markdowndata) for details.

In addition to required values (such as `CANVAS_API_URL` and `CANVAS_COURSE_ID`), you can include optional fields to
further customize your course setup.

## Required Fields

### `CANVAS_API_URL`

The base URL of your Canvas instance. This is used to connect to the Canvas API for deploying course content.

```yaml
CANVAS_API_URL: https://byu.instructure.com/
```

### `CANVAS_COURSE_ID`

The numeric ID of the Canvas course where content will be deployed. You can find this in the course URL (e.g., `canvas.instructure.com/courses/12345` where `12345` is the course ID).

```yaml
CANVAS_COURSE_ID: 12345
```

### `LOCAL_TIME_ZONE`

The timezone for interpreting dates and times in your course. Use standard timezone identifiers (e.g., `America/Denver`, `America/Chicago`, `America/New_York`).

```yaml
LOCAL_TIME_ZONE: America/Denver
```

### `DEPLOY_ROOT`

This is the root of the project you are deploying relative to the `course_info` file.

```yaml
DEPLOY_ROOT: ..
```

## Additional Fields

### `GLOBAL_ARGS`

Optional dictionary of global template arguments available to all Jinja templates in your course content.

```yaml
GLOBAL_ARGS:
  semester: Fall 2025
  instructor_name: Dr. Smith
  course_website: https://example.com/course
```

These arguments can be referenced in any Jinja template throughout your course content.

## Full Example

A complete `course_info` file might look like the following:

```yaml
CANVAS_API_URL: https://byu.instructure.com/
CANVAS_COURSE_ID: 12345
LOCAL_TIME_ZONE: America/Denver
DEPLOY_ROOT: ..
GLOBAL_ARGS:
  semester: Fall 2025
  instructor_name: Dr. Smith
  office_hours: "MWF 2-3 PM"
```

## Advanced Patterns

### Multi-Version Course Deployments

A powerful pattern is using multiple `course_info` files to deploy the same content to different Canvas courses with different configurations:

**File structure:**
```
course_info_prod.yaml           # Production course
course_info_sandbox.yaml        # Testing/sandbox course
course_info_summer.yaml         # Summer session version
global_args_prod.yaml           # Production-specific variables
global_args_summer.yaml         # Summer-specific variables
course_content.xml              # Shared content
```

**Deploy to production:**
```bash
mdxcanvas --course-info course_info_prod.yaml \
          --global-args global_args_prod.yaml \
          course_content.xml
```

**Deploy to sandbox (testing):**
```bash
mdxcanvas --course-info course_info_sandbox.yaml \
          --global-args global_args_sandbox.yaml \
          course_content.xml
```

This allows you to:
- Maintain a **single source of truth** for course content
- Test changes in a sandbox before production
- Deploy to multiple course sections with different settings
- Version control your course configuration

### GLOBAL_ARGS for Dynamic Content

Define variables in `GLOBAL_ARGS` that can be used throughout your templates to control behavior:

```yaml
GLOBAL_ARGS:
  semester: Fall 2025
  start_date: Aug 25, 2025
  end_date: Dec 15, 2025

  # Environment-specific settings
  show_solutions: false
  enable_extra_credit: true

  # Instructor preferences
  late_policy: "10% per day"
  office_hours: "MWF 2-3 PM"

  # Course structure
  assignment_groups:
    - name: "Homework"
      weight: 40
    - name: "Quizzes"
      weight: 30
    - name: "Final Project"
      weight: 30
```

These values are accessible in your Jinja templates and can control:
- Which content appears
- Default values for assignments
- Course metadata
- Conditional functionality

### Timezone-Aware Date Deployments

The `LOCAL_TIME_ZONE` setting ensures all dates in your course are interpreted correctly:

```yaml
LOCAL_TIME_ZONE: America/Denver  # Mountain Time
```

When you specify `due_at="Jan 15, 2025, 11:59 PM"` in assignments, MDXCanvas converts it to the correct UTC time for the Canvas API using this timezone. This is especially important for:
- Courses spanning multiple time zones
- Teams deploying from different locations
- Ensuring students see consistent due dates

### Structured Deployment Root

The `DEPLOY_ROOT` defines where relative paths in your content are resolved from:

```yaml
DEPLOY_ROOT: ..
```

With this structure:
```
canvas_material/                  ← DEPLOY_ROOT (resolved via `..` from course_info/)
├── course_info/
│   ├── course_info_Winter26.json ← course_info file lives here
│   └── course_info_prod.json
├── global_args.json
├── main.css
├── course_outline.xml.jinja
├── homeworks/
│   ├── homeworks-args.md.jinja
│   └── homeworks.canvas.xml.jinja
└── pages/
    ├── syllabus.md.jinja
    └── assets/
```

All relative paths in your content (e.g., `<file id="course-logo" path="pages/assets/logo.png" />`) are resolved relative to `DEPLOY_ROOT` — in this case, `canvas_material/`.
