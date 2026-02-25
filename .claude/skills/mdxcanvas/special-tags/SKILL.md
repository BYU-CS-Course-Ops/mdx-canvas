---
name: mdxcanvas/special-tags
description: Reference for MDXCanvas special/helper tags — include, md-page, file, img, zip, course-link, and course-settings.
license: Complete terms in ../LICENSE.txt
---

# Special Tags

Special tags provide infrastructure-level functionality: embedding external files, uploading assets, linking between
course items, and configuring course settings. They are not Canvas resources themselves but are used alongside resource
tags.

For complete attribute documentation, read the tag files in `documents/special_tags/tags/`.

## Tag Overview

| Tag                 | Purpose                                              | Key Attributes          |
|---------------------|------------------------------------------------------|-------------------------|
| `<include>`         | Embed external file content inline                   | `path`, `fenced`, `lines`, `args` |
| `<md-page>`         | Create a page from a `.md` file (auto-detects title) | `path`                  |
| `<file>`            | Upload and link a single file                        | `path`, `title`         |
| `<img>`             | Upload and embed an image                            | `path`, `alt`           |
| `<zip>`             | Upload a zip archive                                 | `path`                  |
| `<course-link>`     | Link to another course item by type + title          | `type`, `title`         |
| `<course-settings>` | Set course metadata (name, code, image)              | `name`, `code`, `image` |

---

## `<include>`

Embeds the content of an external file directly at the point of inclusion. The file's content is inserted at the
location of the tag inside the parent element.

The `path` is always relative to the file that contains the `<include>` tag.

### Attributes

| Attribute          | Required | Default | Purpose                                                             |
|--------------------|----------|---------|---------------------------------------------------------------------|
| `path`             | yes      | —       | Path to the file to embed                                           |
| `fenced`           | no       | —       | Language name (e.g. `python`) — wraps content in a fenced code block |
| `include_filename` | no       | `false` | When `true`, adds a filename header above the fenced block          |
| `lines`            | no       | —       | Line range to include — `"start:end"` (1-based, inclusive)          |
| `args`             | no       | —       | Path to a YAML/JSON args file for `.jinja` template includes        |
| `usediv`           | no       | `true`  | When `false`, inserts content raw without wrapping in a `<div>`     |

### Examples

**Markdown file inclusion** — keep long descriptions in separate files:

```xml
<syllabus>
    <include path="content/syllabus.md"/>
</syllabus>

<assignment title="Homework 1">
    <include path="content/assignments/hw1.md"/>
</assignment>
```

**Code file as fenced block with filename header** — useful in pages and assignment descriptions:

```xml
<page title="Sorting Example">
    Here is the starter code for this week's lab:

    <include path="code/sort.py" fenced="python" include_filename="true"/>
</page>
```

Renders as a fenced code block with `sort.py` shown as the filename header above it.

**Line-specific snippet** — embed only part of a file (useful in quiz `<question type="text">`):

```xml
<quiz title="Code Reading Quiz">
    <question type="text" points="2">
        What does this function return?

        <include path="code/sort.py" fenced="python" lines="10:25"/>

        [your answer here]
    </question>
</quiz>
```

Lines are 1-based and inclusive. `lines="10:25"` includes lines 10 through 25.

**Jinja template with args file** — render a `.jinja` file with variable substitution:

```xml
<assignment title="Homework 3">
    <include path="templates/homework.md.jinja" args="content/hw3-args.yaml"/>
</assignment>
```

The args file is a YAML or JSON file whose keys are available as Jinja variables inside the template.

---

## `<md-page>`

Creates a Canvas page from a Markdown file. Automatically uses the first `# Heading` as the page title.

**Use case:** Writing page content in standalone `.md` files.

```xml

<md-page path="content/pages/week1-intro.md"/>
```

The resulting Canvas page title comes from the first `# Heading` in the file.

For complete documentation, read `documents/special_tags/tags/md_page_tag.md`.

---

## `<file>`

Uploads a file to Canvas course files and creates a link in the parent content.

**Use case:** Making PDFs, code samples, or other downloads available.

```xml

<assignment title="Project 1">
    Download the starter files:

    <file path="files/project1-starter.zip" title="Project 1 Starter Files"/>
</assignment>
```

For complete documentation, read `documents/special_tags/tags/file_tag.md`.

---

## `<img>`

Uploads an image to Canvas and embeds it inline in the parent content.

**Use case:** Adding diagrams, screenshots, or illustrations to pages or assignments.

```xml

<page title="Data Structures Overview">
    # Data Structures Overview

    <img path="images/tree-diagram.png" alt="Binary tree diagram"/>

    A binary tree is a hierarchical data structure...
</page>
```

For complete documentation, read `documents/special_tags/tags/img_tag.md`.

---

## `<zip>`

Uploads a `.zip` archive to Canvas course files, with control over which files are included.

**Use case:** Distributing project templates or datasets.

```xml

<file path="files/dataset.zip"/>
```

For complete documentation, read `documents/special_tags/tags/zip_tag.md`.

---

## `<course-link>`

Creates a link to another item in the same Canvas course (page, assignment, quiz) by specifying its type and title.

**Use case:** Cross-referencing items within course content without hardcoding URLs.

```xml

<page title="Week 2 Intro">
    Before proceeding, complete<course-link type="assignment" title="Homework 1"/>.
</page>
```

For complete documentation, read `documents/special_tags/tags/course_link_tag.md`.

---

## `<course-settings>`

Sets course-level metadata: display name, course code, and optional course image.

**Use case:** Configuring the course name and code at deploy time. Typically placed at the top of the entry point file.

```xml

<course-settings
        name="CS 312: Algorithm Design and Analysis"
        code="CS 312"
/>
```

With course image:

```xml

<course-settings
        name="CS 312: Algorithm Design and Analysis"
        code="CS 312"
        image="images/course-banner.png"
/>
```

For complete documentation, read `documents/special_tags/tags/course_settings_tag.md`.

---

## Combining Special Tags

A typical entry point file uses several of these together:

```xml

<div>
    <course-settings name="My Course" code="CS 101"/>

    <syllabus>
        <include path="content/syllabus.md"/>
    </syllabus>

    <assignment title="Project 1">
        <include path="content/assignments/project1.md"/>
        <file path="files/project1-starter.zip" title="Starter Files"/>
    </assignment>

    <module id="week-1" title="Week 1">
        <item type="assignment" content_id="Project 1" indent="1"/>
    </module>
</div>
```

---

## How This Works

When asked about special tags:

1. Provide the relevant snippet from this file for the 80% case.
2. For full attribute details, direct the user to `documents/special_tags/tags/<tag>_tag.md`.
3. When generating files that use special tags, ensure paths are relative to the file containing the tag.
