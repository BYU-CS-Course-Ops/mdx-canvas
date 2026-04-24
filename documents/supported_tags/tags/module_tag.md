# `<module>` Tag

The `<module>` tag defines a course module. Modules organize related content into structured sequences on the Canvas platform. Each module contains one or more `<item>` tags representing pages, assignments, quizzes, files, etc.

## Attributes

### `title`

Sets the title of the module as it appears in Canvas (required).

```xml

<module id="week_1" title="Week 1: Introduction">
    ...
</module>
```

### `id`

Unique identifier for the module (required).

Use an explicit `id` when you need to:
- Change the module's title later without creating a new resource
- Have a more stable identifier for referencing

```xml
<module
    id="week-1"
    title="Week 1: Introduction">
...
</module>
```

**Legacy scenario:** If you have an existing module without an `id` and want to rename it, add an `id` attribute with the value of the old title before changing the title.

### `prerequisite_module_ids` (optional)

Takes a comma separated list module `id` tags that must have all of their items `completion_requirement` attributes met before this module will unlock.

For mor details on the `completion_requirement` attribute see the [`<item>` tag documentation](./item_tag.md#completion_requirement_optional)

```xml
<module id="week-3" title="Week 3: NP-Complete Problems" prerequisite_module_ids="week-1,week-2">
...
</module>
```

## Module Items

A `<module>` contains one or more `<item>` tags, each representing a piece of content within the module (e.g., page, quiz, assignment).

For details on valid item types and attributes, see the [`<item>` tag documentation](./item_tag.md).

## Example

```xml
<module id="example_module_1" title="Example Module 1">
    <item type="page" title="Introduction to the Course" />
    <item type="assignment" title="First Assignment" indent="1" />
    <item type="quiz" title="Module Quiz" indent="1" />
</module>
```

## Advanced Features

### Module Prerequisites

Create a prerequisite chain where students must complete earlier modules before unlocking later ones. Use the `prerequisite_module_ids` attribute with completion requirements:

```xml
<!-- Module 1: Foundation -->
<module id="module-1" title="Module 1: Foundations">
    <item type="page" content_id="intro" completion_requirement="type=must_view" />
</module>

<!-- Module 2: Requires Module 1 completion -->
<module id="module-2" title="Module 2: Advanced Topics" prerequisite_module_ids="module-1">
    <item type="page" content_id="advanced" />
</module>

<!-- Module 3: Requires both Module 1 and 2 -->
<module id="module-3" title="Module 3: Capstone" prerequisite_module_ids="module-1,module-2">
    <item type="assignment" content_id="capstone_project" />
</module>
```

**Rules:**
- The prerequisite module's completion requirements must be met before the dependent module unlocks
- Students see the module in the sidebar but cannot access its content until prerequisites are satisfied
- Multiple prerequisites can be specified as a comma-separated list

### Structured Completion Requirements

Design modules that enforce structured progression using completion requirements on items:

```xml
<module id="week-1" title="Week 1: Linear Algebra">
    <!-- Reading is required -->
    <item type="page" content_id="linear_algebra_intro"
          completion_requirement="type=must_view" />

    <!-- Quiz requires minimum score -->
    <item type="quiz" content_id="week1_quiz"
          completion_requirement="type=min_score,min_score=80" />

    <!-- Assignment requires submission -->
    <item type="assignment" content_id="linear_algebra_hw"
          completion_requirement="type=must_submit" />
</module>
```

**Completion types:**
- `type=must_view` - Student must open/view the item
- `type=must_submit` - Student must submit (assignments/quizzes only)
- `type=min_score,min_score=XX` - Student must score at least XX% (quizzes only)
