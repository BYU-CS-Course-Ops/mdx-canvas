# `<item>` Tag

The `<item>` tag is used to define individual content items within a module. Each item represents a unit of course material — such as a page, assignment, quiz, or file — and is rendered in the Canvas module structure.

## Attributes

### `type`

Specifies the type of the module item. Valid values include:

- `subheader`
- `externalurl`
- `page`
- `assignment`
- `quiz`
- `file`

```xml
<item type="page" title="Example Page" />
```

### `title`

Sets the display name for the item in the module. When referencing existing content (e.g., a page, assignment, or quiz), the title must match exactly — otherwise, MDXCanvas will not be able to locate and insert it into the module.

```xml
<item type="quiz" title="Midterm Quiz" />
```

### `indent` (optional)

Controls the indentation level (hierarchy) of the item within the module.

```xml
<item type="assignment" title="Homework 1" indent="1" />
```