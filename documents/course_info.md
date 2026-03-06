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
