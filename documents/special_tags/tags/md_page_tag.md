# `<md-page>` Tag

The `<md-page>` tag creates a Canvas page from a markdown file. This is a convenience tag that combines page creation with content inclusion from an external markdown file.

## Attributes

### `path` (required)

Relative path to the markdown file to use as the page content.

```xml
<md-page path="lectures/introduction.md" />
```

### `title` (optional)

The page title. If not specified, the title is automatically detected:

1. **From markdown heading**: If the first line of the file is a markdown heading (starts with `# `), that heading becomes the title
2. **From filename**: If no heading is found, the filename (without extension) is used as the title

```xml
<!-- Explicit title -->
<md-page path="lectures/intro.md" title="Course Introduction" />

<!-- Auto-detected from first line: "# Welcome to CS 101" becomes "Welcome to CS 101" -->
<md-page path="lectures/intro.md" />

<!-- Auto-detected from filename: "intro.md" becomes "intro" -->
<md-page path="lectures/intro.md" />
```

## Examples

### Basic Page from Markdown File

```xml
<!-- lectures/introduction.md contains:
# Introduction to Computer Science

Welcome to the course!
-->

<md-page path="lectures/introduction.md" />
```

This creates a Canvas page titled "Introduction to Computer Science" with the markdown content.

### Override Auto-Detected Title

```xml
<!-- Use custom title instead of the one in the markdown file -->
<md-page
    path="lectures/week1.md"
    title="Week 1: Getting Started" />
```

## Notes

- The markdown file is processed using the same logic as the `<include>` tag
- All standard markdown formatting is supported
- Other MDXCanvas tags can be used within the markdown file
- If the file doesn't exist, an error will be raised during processing
