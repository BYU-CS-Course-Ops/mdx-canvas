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

### `completion_requirement` (optional)

Controls how a module item is marked complete. This can be paired with the module's `prerequisite_module_ids` to lock content behind completion requirements.

For more details on the `prerequisite_module_ids` attribute see [`<module>` tag documenetation](./module_tag.md#prerequisite_module_ids_optional)

The attribute takes a comma separated list of `key=value` pairs that are parsed into a dictionary.

For a full list of supported attributes and what they do, please reference the [Canvas API documentation](https://developerdocs.instructure.com/services/canvas/resources/modules#modules-api)

```xml
<module id="week-1"
    <item type="quiz" content_id="RQ_SYL" title="Syllabus Reading Quiz" completion_requirement="type=min_percentage,min_percentage=100"/>
</module>
```
