# `<md-page>` Tag

The `<md-page>` tag creates a Canvas page from a markdown file. This is a convenience tag that combines page creation with content inclusion from an external markdown file. It is converted internally into a `<page>` tag with a nested `<include>` tag.

## Attributes

### `path` (required)

Relative path to the markdown file to use as the page content.

```xml
<md-page id="intro_page" path="lectures/introduction.md" />
```

### `id` (required)

Unique identifier for the page. This is used to reference the page in module items and other tags.

```xml
<md-page id="chapter1" path="lectures/chapter1.md" />
```

### `title` (optional)

The page title displayed in Canvas. If not specified, the title is automatically detected:

1. **From markdown heading**: If the first line of the file is a markdown heading (starts with `# `), that heading becomes the title (stripped of `#` characters)
2. **From filename**: If no heading is found, the filename (without extension) is used as the title

```xml
<!-- Explicit title -->
<md-page id="intro_page" path="lectures/intro.md" title="Course Introduction" />

<!-- Auto-detected from first line: "# Welcome to CS 101" becomes "Welcome to CS 101" -->
<md-page id="intro_page" path="lectures/intro.md" />

<!-- Auto-detected from filename: "intro.md" becomes "intro" -->
<md-page id="intro_page" path="lectures/intro.md" />
```

## Examples

### Basic Page from Markdown File

```xml
<!-- lectures/introduction.md contains:
# Introduction to Computer Science

Welcome to the course!
-->

<md-page id="intro_page" path="lectures/introduction.md" />
```

This creates a Canvas page with `id="intro_page"` titled "Introduction to Computer Science" with the markdown content.

### Override Auto-Detected Title

```xml
<!-- Use custom title instead of the one in the markdown file -->
<md-page
    id="week1_page"
    path="lectures/week1.md"
    title="Week 1: Getting Started" />
```

### Using in a Module

```xml
<module id="week-1" title="Week 1">
  <item type="page" content_id="intro_page" />
  <item type="page" content_id="resources_page" title="Read the Resources" />
</module>

<!-- Markdown pages that populate the module items above -->
<md-page id="intro_page" path="lectures/intro.md" />
<md-page id="resources_page" path="lectures/resources.md" title="Course Resources" />
```

## Notes

- The markdown file is processed using the same logic as the `<include>` tag
- All standard markdown formatting is supported
- Other MDXCanvas tags can be used within the markdown file
- If the file doesn't exist, an error will be raised during processing
