# `<module>` Tag

The `<module>` tag defines a course module. Modules organize related content into structured sequences on the Canvas platform. Each module contains one or more `<item>` tags representing pages, assignments, quizzes, files, etc.

## Attributes

### `title`

Sets the title of the module as it appears in Canvas.

```xml
<module id="week-1" title="Week 1: Introduction">
...
</module>
```

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
<module title="Example Module 1">
    <item type="page" title="Introduction to the Course" />
    <item type="assignment" title="First Assignment" indent="1" />
    <item type="quiz" title="Module Quiz" indent="1" />
</module>
```
