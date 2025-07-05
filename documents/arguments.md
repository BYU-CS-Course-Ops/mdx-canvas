# `--course-info`: Path to a JSON file containing course information.

- Required: `True` 
- Type: `JSON`

A possible `course_info.json` file should look like this:

```json
{
  "CANVAS_API_URL": "https://byu.instructure.com/",
  "CANVAS_COURSE_ID": 12345,
  "LOCAL_TIME_ZONE": "America/Denver"
}
```

Where the `CANVAS_API_URL` is the base URL for the Canvas API, `CANVAS_COURSE_ID` 
is the ID of the course in Canvas, and `LOCAL_TIME_ZONE` is the time zone for 
scheduling events.

With the following additional keys:

```json
{
  "COURSE_NAME" : "Testing Course",
  "COURSE_CODE" : "Testing",
  "COURSE_IMAGE" : "image.png"
}
```

Which are used to set the course name, code, and image in Canvas.

# `<file>`: Path to the file to be processed, which can be a Jinja2 template file or a Markdown file.

- Required: `True`
- Type: `Markdown`, `XML`, `HTML`, or `Jinja2`

## Markdown

Pure Markdown files will be processed as a Canvas page. Which can be uploaded in an `xml` file 
format to Canvas.

```xml
<md-page title="Example Page" path="example_page.md" />
```

## XML

XML files can be used to generate Canvas pages, assignments, quizzes, modules, syllabus, and announcements.

### Assignment

```xml
<assignment
        title="Example Assignment"
        due_at="Jan 02, 2025, 11:59 PM"
        available_from="Jan 01, 2025, 12:00 AM"
        available_to="Jan 02, 2025, 11:59 PM"
        points_possible="100"
        assignment_group="Assignments">

<description>
    This is an example assignment description.
</description>

</assignment>
```

### Quiz

```xml
```

- `--args`: Path to a file containing arguments for the template.
  - Required: `False`
  - Type: `Jinja2`, `MarkdownData`, `JSON`, or `CSV`
  - Notes: _fill_
- `--global-args`: Path to a JSON file containing global arguments.
  - Required: `False`
  - Type: `JSON`
  - Notes: _fill_
- `--css`: Path to a CSS file for styling the canvas objects.
  - Required: `False`
  - Type: `CSS`
  - Notes: _fill_
- `--debug`: Enable debug mode for detailed logging.
  - Required: `False`
  - Type: `Boolean`
  - Notes: _fill_
- `--dry-run`: Outputs a list of items what would be uploaded to canvas
  - Required: `False`
  - Type: `Boolean`
  - Notes: _fill_
- `---output-file`: Generates a detailed report of the outcome of MDXCanvas execution.
  - Required: `False`
  - Type: `PATH`
  - Notes: _fill_