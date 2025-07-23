# MDXCanvas

**MDXCanvas** allows you to define Canvas course content using source files (`.md`, `.xml`, `.jinja`, etc.) and deploy it programmatically to a Canvas instance via the API.

## Installation

Install via pip:

```bash
pip install mdxcanvas
```

You must also create a **Canvas API Token** from your Canvas account settings and store it as an environment variable:

```bash
export CANVAS_API_TOKEN="your_token_here"
```

## Usage

To deploy content to Canvas, run:

```bash
mdxcanvas --course-info <course_info.json> <content_file>
```

### `course_info`

A JSON config file specifying course deployment details. It must include:

- `CANVAS_API_URL`
- `CANVAS_COURSE_ID`
- `LOCAL_TIME_ZONE`

Example:

```json
{
  "CANVAS_API_URL": "https://byu.instructure.com/",
  "CANVAS_COURSE_ID": 12345,
  "LOCAL_TIME_ZONE": "America/Denver"
}
```

For extended options like `COURSE_NAME`, `COURSE_IMAGE`, etc., see the
[Course Info Guide](documents/course_info.md).

### `content_file`

The content file defines what will be pushed to Canvas. Supported formats:

- `.md`
- `.xml`
- `.html`
- `.jinja`

Example (`.xml` quiz):

```xml
<quiz title="Example Quiz">

    <description>
        # Attention

        The following questions test your knowledge of the wizzarding world of **Harry Potter**.
    </description>

    <questions>
        <question type="multiple-choice">
            Who is the author of the Harry Potter series?

            <correct>J.K. Rowling</correct>
            <incorrect>J.R.R. Tolkien</incorrect>
            <incorrect>George R.R. Martin</incorrect>
            <incorrect>Stephen King</incorrect>
        </question>

        <question type="true-false" answer="true">
            Is Harry Potter a wizard?
        </question>
    </questions>
</quiz>
```

As shown above, Markdown formatting is supported within content.

See the [Demo Course](demo_course) for complete examples.

## Tutorials

These guides cover the full feature set of MDXCanvas:

### [Course Info](documents/course_info.md)

Configure course metadata such as name, code, and dashboard image.

### [Supported Tags](documents/supported_tags/supported_tags.md)

Full reference of standard content tags like `<assignment>`, `<quiz>`, `<page>`, and more.

### [Special Tags](documents/special_tags/special_tags.md)

Advanced features like `<include>`, `<file>`, and `<zip>` for modular, reusable content.

### [Jinja Templates](documents/jinja_templates.md)

Use variables and loops to dynamically generate content using `.jinja` templates.

### [CSS Styling](documents/css.md)

Apply custom styling across your content using external CSS files.

## Demo Course

Explore the `demo_course` folder to see MDXCanvas in action:

* All quiz question types
* Pages (including MD pages)
* Modules and module items
* Assignments (with and without Jinja)
* Syllabus
* Announcements
* Assignment weights
* Overrides
* Jinja template examples
* Header page

*Link to demo course folder content*