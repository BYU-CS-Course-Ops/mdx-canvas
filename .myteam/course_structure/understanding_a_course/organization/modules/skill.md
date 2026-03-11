# Canvas Modules

## `<module>` Tag

The `<module>` tag defines a Canvas module. Modules organize related content into structured sequences that students
navigate in Canvas.

### Attributes

#### `title` (required)

Sets the title of the module as it appears in Canvas.

```xml
<module title="Week 1: Introduction">
    ...
</module>
```

#### `id` (optional)

Unique identifier for the module. Defaults to `title` if omitted.

Use an explicit `id` when you need to change the title later without creating a new module, or when referencing the
module in `prerequisite_module_ids`.

```xml
<module id="week-1" title="Week 1: Introduction">
    ...
</module>
```

**Legacy rename:** If an existing module has no `id` and you want to rename it, first add `id` with the old title value,
then change `title`.

#### `prerequisite_module_ids` (optional)

Comma-separated list of module `id` values that must have all their completion requirements met before this module
unlocks.

```xml
<module id="week-3" title="Week 3: NP-Complete Problems" prerequisite_module_ids="week-1,week-2">
    ...
</module>
```

### Example

```xml
<module title="Example Module 1">
    <item type="page" title="Introduction to the Course" />
    <item type="assignment" title="First Assignment" indent="1" />
    <item type="quiz" title="Module Quiz" indent="1" />
</module>
```

---

## `<item>` Tag

The `<item>` tag defines individual items within a module. Items link to existing content or create structure (
subheaders, external links).

### Common Attributes

#### `type` (required)

Valid types:

- `page` — link to a course page
- `assignment` — link to an assignment
- `quiz` — link to a quiz
- `file` — link to a course file
- `subheader` — section divider with text
- `externalurl` — link to an external website
- `syllabus` — link to the course syllabus

#### `title` (optional)

Custom display name in the module. If omitted, uses the linked content's title.

```xml
<!-- Shows "Read the Introduction" in module, links to page with id "intro_page" -->
<item type="page" content_id="intro_page" title="Read the Introduction" />
```

#### `indent` (optional)

Visual indentation level within the module (integer).

```xml
<item type="assignment" content_id="hw1" indent="1" />
```

#### `completion_requirement` (optional)

Defines how the item must be completed. Uses comma-separated `key=value` pairs.

Common requirements:

- `type=must_view` — student must view the item
- `type=must_submit` — student must submit (assignments/quizzes)
- `type=min_score,min_score=80` — student must score at least 80

```xml
<item type="quiz" content_id="quiz1" completion_requirement="type=min_score,min_score=100" />
```

### Type-Specific Attributes

#### `content_id` — for `page`, `assignment`, `quiz`, `file`

The `id` of the content to link to. Must match the `id` attribute (or `title` if no `id` was set) of the target
resource.

```xml
<page id="intro_page" title="Introduction to the Course">
  ...
</page>

<module title="Week 1">
  <item type="page" content_id="intro_page" />
</module>
```

#### `title` — for `subheader`

Creates a text divider within the module.

```xml
<item type="subheader" title="Week 1 Readings" />
```

#### `external_url` — for `externalurl`

URL to link to.

```xml
<item type="externalurl" external_url="https://example.com" title="Example Website" />
```

### Examples

#### Basic module with various item types

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

#### With completion requirements and prerequisites

```xml
<module id="week-1" title="Week 1">
    <item type="page" content_id="intro" completion_requirement="type=must_view" />
    <item type="quiz" content_id="quiz1" completion_requirement="type=min_score,min_score=80" />
</module>

<module id="week-2" title="Week 2" prerequisite_module_ids="week-1">
    <!-- Unlocks after Week 1 completion requirements are met -->
    <item type="page" content_id="lesson2" />
</module>
```
