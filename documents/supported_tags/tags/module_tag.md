# `<module>` Tag

The `<module>` tag defines a course module. Modules organize related content into structured sequences on the Canvas platform. Each module contains one or more `<item>` tags representing pages, assignments, quizzes, files, etc.

## Attributes

### `title`

Sets the title of the module as it appears in Canvas.

```xml
<module title="Week 1: Introduction">
...
</module>
```

## Children

A `<module>` contains one or more `<item>` tags, each representing a piece of content within the module (e.g., page, quiz, assignment).

For details on valid item types and attributes, see the [`<item>` tag documentation](item_tag.md).

## Example

```xml
<module title="Example Module 1">
    <item type="page" title="Introduction to the Course" />
    <item type="assignment" title="First Assignment" indent="1" />
    <item type="quiz" title="Module Quiz" indent="1" />
</module>
```
