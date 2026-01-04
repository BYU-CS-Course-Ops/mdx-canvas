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

A configuration file specifying course deployment details. Supported formats:

- **YAML** (`.yaml`, `.yml`) - Recommended
- **JSON** (`.json`)
- **MarkdownData** (`.md`, `.mdd`)

The file must include:

- `CANVAS_API_URL`
- `CANVAS_COURSE_ID`
- `LOCAL_TIME_ZONE`

Example (YAML):

```yaml
CANVAS_API_URL: https://byu.instructure.com/
CANVAS_COURSE_ID: 12345
LOCAL_TIME_ZONE: America/Denver
```

For extended options like `COURSE_NAME`, `COURSE_IMAGE`, `GLOBAL_ARGS`, etc., see the
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

## Command-Line Options

The `mdxcanvas` command supports the following options:

- `--course-info <file>` - Path to course configuration file (YAML/JSON/MarkdownData)
- `--args <file>` - Path to template arguments file (for Jinja templates)
- `--global-args <file>` - Path to global arguments file (merged with `GLOBAL_ARGS` from course_info)
- `--templates <files>` - List of template files to import
- `--css <file>` - Path to CSS file for styling
- `--debug` - Enable debug logging
- `--dryrun` / `--dry-run` - Preview changes without deploying to Canvas
- `--output-file <file>` - Save deployment report to specified file

Example with options:

```bash
mdxcanvas --course-info course.yaml \
          --global-args globals.yaml \
          --css styles.css \
          --dryrun \
          content.xml
```

## Erasing Course Content

The `erasecanvas` command removes all content from a Canvas course.

**WARNING:** This is a destructive operation that cannot be undone.

Usage:

```bash
erasecanvas --course-info <course_info.yaml>
```

Options:

- `--course-info <file>` - Path to course configuration file (required)
- `-y` - Skip confirmation prompt (use with caution!)

The command will delete:

- Syllabus content
- All assignments and quizzes
- All pages
- All modules
- All files and folders
- All announcements

Without the `-y` flag, you will be prompted to confirm before deletion proceeds.

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

Explore the [`demo_course`](demo_course) folder to see MDXCanvas in action: