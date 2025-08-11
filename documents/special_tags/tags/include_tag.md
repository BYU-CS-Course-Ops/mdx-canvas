# `<include>` Tag

The `<include>` tag allows you to embed content from another file into the current file. This enables content reuse, modular organization, and easier long-term maintenance.

## Attributes

### `path`

Specifies the relative path to the file to be included.

```xml
<include path="instructions/example.md" />
```

The included file can contain Markdown, HTML, or plain text.

### `fenced` (optional)

Wraps the included content in triple backticks for code formatting.

```xml
<include path="hello_world.py" fenced="True" />
```

### `lines` (optional)

Includes only specific lines from the source file. Use the format `"start:end"` (1-based, inclusive).

```xml
<include path="hello_world.py" lines="1:2" fenced="True" />
```

This is useful when including only a portion of a script or document.

## Examples

### Markdown Inclusion

```md
<!-- contents of intro.md -->
# Welcome

This is reusable content.
```

```xml
<page title="Intro Page">
    <include path="intro.md" />
</page>
```

### Fenced Code Snippet

```python
# hello_world.py
print("Hello, world!")
print("Another line.")
```

```xml
<question type="text">
    This is Python code:

    <include path="hello_world.py" fenced="True" />

    Good stuff.
</question>
```

### Line-Specific Snippet

```xml
<question type="text">
    Here's the first line of the script:

    <include path="hello_world.py" lines="1:1" fenced="True" />
</question>
```

An example of this can be found in the demo course [here](../../../demo_course/course.canvas.md.xml).