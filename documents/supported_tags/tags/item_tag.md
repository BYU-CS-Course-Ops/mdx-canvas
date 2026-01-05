# `<item>` Tag

The `<item>` tag defines individual items within a module. Items can link to existing content (pages, assignments, 
quizzes, files) or create structure (subheaders, external links).

## Common Attributes

### `type` (required)

Specifies the type of module item:

- `page` - Link to a course page
- `assignment` - Link to an assignment
- `quiz` - Link to a quiz
- `file` - Link to a course file
- `subheader` - Section divider with text
- `externalurl` - Link to external website

```xml
<item type="page" content_id="intro_page" />
```

### `title` (optional)

Custom display name for the item in the module. If omitted, uses the linked content's title.

**Use this when you want the module item to display differently than the actual content's title.**

```xml
<!-- Shows "Read the Introduction" in module, links to page titled "intro_page" -->
<item type="page" content_id="intro_page" title="Read the Introduction" />
```

### `indent` (optional)

Controls indentation level (visual hierarchy) within the module.

```xml
<item type="assignment" content_id="hw1" indent="1" />
```

### `completion_requirement` (optional)

Defines how the item must be completed. Uses comma-separated `key=value` pairs.

Common requirements:
- `type=must_view` - Student must view the item
- `type=must_submit` - Student must submit (assignments/quizzes)
- `type=min_score,min_score=80` - Student must score at least 80%

```xml
<item type="quiz" content_id="quiz1" completion_requirement="type=min_score,min_score=100" />
```

See [Canvas API documentation](https://canvas.instructure.com/doc/api/modules.html) for full list of completion types.

---

## Type-Specific Attributes

### For `page`, `assignment`, `quiz`, `file` Items

#### `content_id` (required)

The `id` of the existing content to link to. This must match the `id` attribute of a `<page>`, `<assignment>`, 
`<quiz>`, or `<file>` tag defined elsewhere.

```xml
<!-- Elsewhere in your content -->
<page id="intro_page" title="Introduction to the Course">
  ...
</page>

<!-- In your module -->
<module title="Week 1">
  <item type="page" content_id="intro_page" />
</module>
```

**Note:** The `content_id` references the content's `id` attribute, not its `title`.

---

### For `subheader` Items

Creates a text divider within the module. Uses `title` for the header text.

```xml
<item type="subheader" title="Week 1 Readings" />
```

---

### For `externalurl` Items

#### `external_url` (required)

URL to link to. Can be any valid web address.

```xml
<item type="externalurl" external_url="https://example.com" title="Example Website" />
```

If `title` is omitted, uses the URL as the display text.

---

## Examples

### Basic Module with Various Item Types

```xml
<module title="Week 1: Getting Started">
  <item type="subheader" title="Introduction" />
  <item type="page" content_id="welcome_page" />
  <item type="page" content_id="syllabus_page" title="Read the Syllabus" />

  <item type="subheader" title="Assignments" />
  <item type="assignment" content_id="hw1" indent="1" />
  <item type="quiz" content_id="week1_quiz" indent="1" />

  <item type="subheader" title="Resources" />
  <item type="file" content_id="lecture_notes.pdf" indent="1" />
  <item type="externalurl" external_url="https://docs.example.com" title="External Documentation" indent="1" />
</module>
```

### With Completion Requirements

```xml
<module id="week-1" title="Week 1">
  <item type="page" content_id="intro" completion_requirement="type=must_view" />
  <item type="quiz" content_id="quiz1" completion_requirement="type=min_score,min_score=80" />
</module>

<module id="week-2" title="Week 2" prerequisite_module_ids="week-1">
  <!-- This module unlocks after week-1 completion requirements are met -->
  <item type="page" content_id="lesson2" />
</module>
```
