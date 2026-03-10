# `<page>` Tag

The `<page>` tag creates a content page in the course. You can use Markdown, HTML, or plain text inside the tag body to define the content shown to students.

## Attributes

### `title` (required)

Sets the title of the page. This is how the page will appear in Canvas and how it should be referenced in `<item>` tags.

```xml
<page id="example_page" title="Example Page">
...
</page>
```

### `id` (required)

Unique identifier for the page. This must be unique across all pages in your course and is used to reference the page in module items.

```xml
<page
    id="intro_page"
    title="Introduction">
...
</page>
```

### `published` (optional, defaults to unpublished)

Whether the page is visible to students immediately. Set to `"true"` to publish.

```xml
<page id="synopsis" title="Course Synopsis" published="true">
...
</page>
```

### `front_page` (optional, defaults to false)

Set to `"true"` to make this the default landing page when students access the course.

```xml
<page id="home" title="Welcome" front_page="true">
...
</page>
```

### `student_todo_at` (optional)

Date when this page should appear in students' to-do list. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<page id="reading" title="Required Reading" student_todo_at="Jan 15, 2025, 9:00 AM">
...
</page>
```

### `publish_at` (optional)

Date and time when the page should automatically become visible to students. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<page id="midterm_review" title="Midterm Review" publish_at="Feb 1, 2025, 8:00 AM">
...
</page>
```

## Content

The body of a `<page>` tag can include:

- Markdown (`MD`)
- HTML
- Code blocks
- Tables
- Links

All standard Markdown and Canvas HTML formatting is supported.

## Example

```xml
<page id="example_page" title="Example Page">
    # Welcome to the Example Page

    Things like headers and `MD` formatting can be used here.

    ## Code Example

    ```python
    def example_function():
        print("This is an example function.")
    ```

    ## Links

    You can also include links to other resources, such as
    [Canvas Documentation](https://canvas.instructure.com/doc/api/).

    ## Table Example

    | Header 1 | Header 2 |
    | -------- | -------- |
    | Row 1    | Row 2    |
    | Row 3    | Row 4    |
</page>
```
