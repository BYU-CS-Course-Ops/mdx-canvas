# `<course-link>` Tag

The `<course-link>` tag creates a link to course content (pages, assignments, quizzes, etc.). The link automatically
resolves to the correct Canvas URL.

## Attributes

### `type` (required)

The type of content to link to. Valid values:

- `page`
- `assignment`
- `quiz`
- `announcement`
- `discussion`
- `module`
- `syllabus`

```xml
<course-link type="page" id="intro_page" />
```

### `id` (required)

The `id` of the content to link to. This must match the `id` attribute of the target resource.

**Important:** This is the `id` attribute, not the `title`. If a resource you are attempting to link to does not have
an `id` attribute, you would put the resources `title` attribute in its place.

```xml
<!-- Elsewhere: define the page -->
<page id="intro_page" title="Introduction to the Course">
  ...
</page>

<!-- Link to it using the id -->
<course-link type="page" id="intro_page" />
```

### `fragment` (optional)

Add a fragment to jump to on a course page.

```xml
<!-- Elsewhere: define the page -->
<page id="intro_page" title="Introduction to the Course">
  ...
  # My Fancy Title {: #my-fancy-title}
</page>

<!-- Link to it using the id -->
<course-link type="page" id="intro_page" fragment="my-fancy-title"/>
```

## Link Text

### Default Behavior

By default, the link text is automatically set to the **title** of the target content.

```xml
<!-- If the page has title="Introduction to the Course" -->
<course-link type="page" id="intro_page" />
<!-- Displays: "Introduction to the Course" -->
```

### Custom Link Text

Add text inside the tag to override the default link text:

```xml
<course-link type="page" id="intro_page">Click here to read the intro</course-link>
<!-- Displays: "Click here to read the intro" -->
```

## Examples

### Basic Links

```xml
<!-- Link to an assignment -->
<course-link type="assignment" id="hw1" />

<!-- Link to a quiz -->
<course-link type="quiz" id="midterm_exam" />
```

### Custom Link Text

```xml
<assignment title="Homework 1">
  Before starting, please review the
  <course-link type="page" id="style_guide">coding style guide</course-link>.

  Submit your work to <course-link type="assignment" id="hw1_submission">the submission page</course-link>.
</assignment>
```
