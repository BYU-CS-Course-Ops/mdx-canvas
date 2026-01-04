# `<page>` Tag

The `<page>` tag creates a content page in the course. You can use Markdown, HTML, or plain text inside the tag body to define the content shown to students.

## Attributes

### `title`

Sets the title of the page (required). This is how the page will appear in Canvas and how it should be referenced in `<item>` tags.

```xml
<page title="Example Page">
...
</page>
```

### `id`

Optional unique identifier for the page. If not specified, defaults to the `title` value.

Use an explicit `id` when you need to change the page's title later without creating a new resource, or when you want a more stable identifier for referencing.

```xml
<page
    id="intro_page"
    title="Introduction">
...
</page>
```

**Legacy scenario:** If you have an existing page without an `id` and want to rename it, add an `id` attribute with the value of the old title before changing the title.

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
<page title="Example Page">
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
