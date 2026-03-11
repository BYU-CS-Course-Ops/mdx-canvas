# Special / Helper Tags

These tags provide infrastructure-level functionality used alongside resource tags (`<assignment>`, `<quiz>`, `<page>`,
etc.).

## Overview

| Tag                 | Purpose                                    | Key Attributes                                                                  |
|---------------------|--------------------------------------------|---------------------------------------------------------------------------------|
| `<include>`         | Embed external file content inline         | `path`, `fenced`, `lines`, `args`, `usediv`                                     |
| `<md-page>`         | Create a Canvas page from a `.md` file     | `path`, `title`                                                                 |
| `<file>`            | Upload and link a single file to Canvas    | `path`, `title`, `canvas_folder`, `unlock_at`, `lock_at`                        |
| `<img>`             | Upload and embed an image inline           | `src`, `canvas_folder`                                                          |
| `<zip>`             | Upload a zip archive to Canvas             | `name`, `path`, `additional_files`, `priority_path`, `exclude`, `canvas_folder` |
| `<course-link>`     | Link to another course item by type and id | `type`, `id`, `fragment`                                                        |
| `<course-settings>` | Set course metadata (name, code, image)    | `name`, `code`, `image`                                                         |
| `<timestamp/>`      | Insert current date/time at deploy         | `format` (optional)                                                             |

---

## `<include>`

Embeds the content of another file at the point of inclusion. The `path` is relative to the file containing the
`<include>` tag.

### Attributes

| Attribute          | Required | Description                                                                          |
|--------------------|----------|--------------------------------------------------------------------------------------|
| `path`             | yes      | Relative path to the file to include                                                 |
| `fenced`           | no       | Wrap content in triple backticks; set to the language (e.g., `"python"`) or `"True"` |
| `include_filename` | no       | Add filename header to fenced code block (`"True"`)                                  |
| `lines`            | no       | Include only specific lines, format `"start:end"` (1-based, inclusive)               |
| `args`             | no       | Path to args file for Jinja template processing                                      |
| `usediv`           | no       | Wrap in `<div>` element (default `true`); set `"false"` to insert directly           |

### Examples

```xml
<!-- Embed a Markdown file -->
<assignment title="Homework 1">
    <include path="content/assignments/hw1.md"/>
</assignment>

<!-- Code file as fenced block with filename header -->
<page title="Sorting Example">
    <include path="code/sort.py" fenced="python" include_filename="true"/>
</page>

<!-- Include only lines 10–25 -->
<include path="code/sort.py" fenced="python" lines="10:25"/>

<!-- Render a Jinja template with an args file -->
<include path="templates/homework.md.jinja" args="content/hw3-args.yaml"/>

<!-- Include without wrapper div -->
<include path="content.md" usediv="false"/>
```

---

## `<md-page>`

Creates a Canvas page from a `.md` file. Title is auto-detected from the first `# Heading` in the file, or defaults to
the filename.

### Attributes

| Attribute | Required | Description                        |
|-----------|----------|------------------------------------|
| `path`    | yes      | Relative path to the markdown file |
| `title`   | no       | Override the auto-detected title   |

### Examples

```xml
<!-- Auto-detected title from first heading -->
<md-page path="content/pages/week1-intro.md"/>

<!-- Explicit title override -->
<md-page path="content/pages/week1.md" title="Week 1: Getting Started"/>
```

---

## `<file>`

Uploads a file to Canvas and creates a download link.

### Attributes

| Attribute       | Required | Description                                                      |
|-----------------|----------|------------------------------------------------------------------|
| `path`          | yes      | Relative path to the file                                        |
| `title`         | no       | Display name for the download link                               |
| `canvas_folder` | no       | Canvas folder path to upload the file to                         |
| `unlock_at`     | no       | Date when file becomes available: `MMM d, yyyy, h:mm AM/PM`      |
| `lock_at`       | no       | Date when file is no longer available: `MMM d, yyyy, h:mm AM/PM` |

### Examples

```xml
<!-- Basic file attachment -->
<assignment title="Project 1">
    Download the starter files:
    <file path="files/project1-starter.zip" title="Project 1 Starter Files"/>
</assignment>

<!-- Organized in Canvas folder -->
<file path="syllabus.pdf" canvas_folder="Course Documents"/>

<!-- Time-restricted access -->
<file
    path="midterm_exam.pdf"
    unlock_at="Feb 15, 2025, 9:00 AM"
    lock_at="Feb 15, 2025, 11:00 AM"
    canvas_folder="Exams"/>
```

---

## `<img>`

Uploads a local image to Canvas and embeds it. External URLs and Canvas plugin URLs (`@@PLUGINFILE@@`) are left
unchanged.

### Attributes

| Attribute       | Required | Description                                             |
|-----------------|----------|---------------------------------------------------------|
| `src`           | yes      | Local file path or external URL                         |
| `canvas_folder` | no       | Canvas folder to upload the image to (local files only) |

Standard HTML `img` attributes (`alt`, `width`, `height`) can also be used.

### Examples

```xml
<!-- Local image — will be uploaded -->
<img src="images/diagram.png" alt="Course diagram"/>

<!-- With Canvas folder organization -->
<img src="images/circuit.png" canvas_folder="Lab Diagrams" alt="Lab 1 Circuit"/>

<!-- External URL — no upload -->
<img src="https://example.com/photo.jpg"/>
```

---

## `<zip>`

Uploads a zip archive to Canvas.

### Attributes

| Attribute          | Required | Description                                                         |
|--------------------|----------|---------------------------------------------------------------------|
| `path`             | yes      | Source directory to zip                                             |
| `name`             | no       | Name of the resulting zip file; defaults to directory name + `.zip` |
| `additional_files` | no       | Comma-separated list of additional files to include                 |
| `priority_path`    | no       | Folder inside the zip to prioritize                                 |
| `exclude`          | no       | Regex pattern for files/folders to exclude                          |
| `canvas_folder`    | no       | Canvas folder to upload the zip to                                  |

### Examples

```xml
<!-- Basic zip of a directory -->
<zip path="labs/lab1"/>

<!-- Full options -->
<zip
    name="lab1_resources.zip"
    path="labs/lab1"
    additional_files="shared/utils.py,README.md"
    priority_path="labs/lab1/starter"
    exclude=".*\.log"
    canvas_folder="Lab Materials"/>
```

---

## `<course-link>`

Creates a link to another course resource. The link resolves to the Canvas URL automatically at build time.

### Attributes

| Attribute  | Required | Description                                                                                     |
|------------|----------|-------------------------------------------------------------------------------------------------|
| `type`     | yes      | Resource type: `page`, `assignment`, `quiz`, `announcement`, `discussion`, `module`, `syllabus` |
| `id`       | yes      | The `id` of the target resource (or `title` if no `id` was set)                                 |
| `fragment` | no       | URL fragment to jump to a section on the target page                                            |

The tag body becomes custom link text. If the body is empty, the target resource's title is used.

### Examples

```xml
<!-- Default link text (uses target title) -->
<course-link type="assignment" id="hw1"/>

<!-- Custom link text -->
<page title="Week 2 Intro">
    Before proceeding, complete
    <course-link type="assignment" id="hw1">Homework 1</course-link>.
</page>

<!-- Link to a specific section on a page -->
<course-link type="page" id="intro_page" fragment="my-fancy-title"/>
```

**Note:** `id` here refers to the `id` attribute of the target resource, not its `title`. If the target has no `id`, use
the `title` value instead.

---

## `<timestamp/>`

Inserts the current date and time at **deploy time** (not Jinja render time). Both self-closing (`<timestamp/>`) and
paired (`<timestamp></timestamp>`) forms work.

### Attributes

| Attribute | Required | Description                                                                                            |
|-----------|----------|--------------------------------------------------------------------------------------------------------|
| `format`  | no       | Python `strftime` format string; default: `%B %d, %Y at %I:%M %p` (e.g., `March 11, 2026 at 02:30 PM`) |

### Examples

```xml
<!-- Default format -->
*Last updated: <timestamp/>*

<!-- Custom format -->
<timestamp format="%m/%d/%Y"/>
```

Use inside assignment or page descriptions to show when content was last deployed.

---

## `<course-settings>`

Sets course metadata. At least one attribute is required.

### Attributes

| Attribute | Required | Description                          |
|-----------|----------|--------------------------------------|
| `name`    | no*      | Display name of the course           |
| `code`    | no*      | Course code (e.g., `CS 101`)         |
| `image`   | no*      | Relative path to course banner image |

\* At least one of `name`, `code`, or `image` must be specified.

### Examples

```xml
<!-- Name and code -->
<course-settings name="CS 312: Algorithm Design" code="CS 312"/>

<!-- All metadata -->
<course-settings
    name="Data Structures and Algorithms"
    code="CS 235"
    image="images/cs235_banner.png"/>
```
