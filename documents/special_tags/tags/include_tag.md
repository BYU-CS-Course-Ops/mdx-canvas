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

### `include_filename` (optional)

Adds a filename header to fenced code blocks.

```xml
<include path="hello_world.py" fenced="True" include_filename="True" />
```

### `lines` (optional)

Includes only specific lines from the source file. Use the format `"start:end"` (1-based, inclusive).

```xml
<include path="hello_world.py" lines="1:2" fenced="True" />
```

This is useful when including only a portion of a script or document.

### `args` (optional)

Path to an arguments file for Jinja template processing. Use when including `.jinja` files that require variables.

```xml
<include path="template.jinja" args="arguments.json" />
```

### `usediv` (optional, defaults to `true`)

Controls whether the included content is wrapped in a `<div>` element.

- When `true` (default): Wraps content in `<div data-source="..." data-lines="...">`
- When `false`: Inserts content directly without wrapper

```xml
<!-- Include without wrapper div -->
<include path="content.md" usediv="false" />
```

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

## Advanced Features & Tips

### Conditional Includes Based on Environment

Use Jinja to include different files based on deployment environment:

```jinja
{% if environment == 'production' %}
<include path="content/real_api_settings.md" />
{% else %}
<include path="content/test_api_settings.md" />
{% endif %}
```

Deploy with different `--global-args` files to control which file is included:

**`prod_args.yaml`:**
```yaml
environment: production
```

**`test_args.yaml`:**
```yaml
environment: testing
```

```bash
# Production
mdxcanvas --course-info prod_course_info.yaml \
          --global-args prod_args.yaml \
          content.xml

# Testing
mdxcanvas --course-info test_course_info.yaml \
          --global-args test_args.yaml \
          content.xml
```

### Extracting Specific Code Sections

The `lines` attribute is powerful for extracting specific documentation or code sections without duplicating content:

**File: `src/solution.py`:**
```python
# Lines 1-10: Basic setup
def setup():
    ...

# Lines 11-25: Main algorithm
def solve():
    ...

# Lines 26-35: Output formatting
def format_result():
    ...
```

**In assignment description - show only the main algorithm:**
```xml
<assignment title="Algorithm Task">
    <include path="src/solution.py" lines="11:25" fenced="True" include_filename="True" />
</assignment>
```

This extracts just the `solve()` function without showing setup or formatting.

### Template-Driven Includes

Combine includes with Jinja template arguments to create dynamic content:

```jinja
{% for example in examples %}
<question type="text">
    Study this example:

    <include path="examples/{{ example }}.py" fenced="True" include_filename="True" />
</question>
{% endfor %}
```

Pass different example files via the `--args` argument, making your content highly reusable.

### Wrapper Div Control

By default, `<include>` wraps content in a `<div data-source="..." data-lines="...">` container. This is useful for styling but can be disabled:

```xml
<!-- Default: content wrapped in div -->
<include path="intro.md" />

<!-- Unwrapped: content inserted directly -->
<include path="intro.md" usediv="false" />
```

Use `usediv="false"` when including content that shouldn't be in a container (e.g., table rows, list items).
