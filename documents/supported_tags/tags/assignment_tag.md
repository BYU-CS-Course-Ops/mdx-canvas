# `<assignment>` Tag

The `<assignment>` tag is used to define an assignment in the course. It supports various attributes, and the assignment description can be placed directly inside the tag.

## Attributes

### `title`

Sets the assignment title (required).

```xml
<assignment
    title="Example Assignment">
...
</assignment>
```

### `id`

Optional unique identifier for the assignment. If not specified, defaults to the `title` value.

Use an explicit `id` when you need to change the assignment's title later without creating a new resource, or when you want a more stable identifier for referencing.

```xml
<assignment
    id="hw1"
    title="Homework 1">
...
</assignment>
```

**Legacy scenario:** If you have an existing assignment without an `id` and want to rename it, add an `id` attribute with the value of the old title before changing the title.

### `due_at`

Specifies the due date and time.

```xml
<assignment 
    title="Example Assignment" 
    due_at="Jan 1, 2025, 11:59 PM">
...
</assignment>
```

### `available_from`

Sets when the assignment becomes available to students.

```xml
<assignment 
    title="Example Assignment" 
    available_from="Jan 1, 2025, 9:00 AM">
...
</assignment>
```

### `available_to`

Sets when the assignment is no longer available.

```xml
<assignment 
    title="Example Assignment" 
    available_to="Jan 1, 2025, 11:59 PM">
...
</assignment>
```

### `points_possible`

Maximum points possible for the assignment.

```xml
<assignment 
    title="Example Assignment" 
    points_possible="100">
...
</assignment>
```

### `assignment_group`

Specifies the group the assignment belongs to.

```xml
<assignment
    title="Example Assignment"
    assignment_group="Example Group">
...
</assignment>
```

### `late_due`

Latest date and time to accept late submissions. Students can still submit after `due_at` but before `late_due`.

```xml
<assignment
    title="Example Assignment"
    due_at="Jan 15, 2025, 11:59 PM"
    late_due="Jan 17, 2025, 11:59 PM">
...
</assignment>
```

### `submission_types`

Specifies allowed submission types (e.g., `online_upload`, `external_tool`).

```xml
<assignment 
    title="Example Assignment" 
    submission_types="external_tool">
...
</assignment>
```

For a full list, see the [Canvas API documentation](https://canvas.instructure.com/doc/api/assignments.html#Assignment).

### `external_tool_tag_attributes`

Used with `submission_types="external_tool"` to specify external tool configuration.

```xml
<assignment
  title="Example Assignment"
  submission_types="external_tool"
  external_tool_tag_attributes="url=https://lti.int.turnitin.com/launch/gs-proxy">
...
</assignment>
```

## Assignment Content

The assignment description can be placed directly inside the `<assignment>` tag. Markdown or HTML formatting is supported.

```xml
<assignment title="Example Assignment">
    # Example Assignment

    This is an example assignment description. You can use **Markdown** or _HTML_.

    ## Instructions
    1. Read the assignment.
    2. Complete the tasks.
    3. Submit your work before the deadline.
</assignment>
```

**Note:** While you can still use a `<description>` child tag for backwards compatibility, it's not required. Content directly inside the assignment tag will be used as the description.

## Section-Specific Dates

You can specify different due dates for different course sections using the `<overrides>` container with `<override>` tags.

```xml
<assignment title="Homework 1" due_at="Jan 15, 2025, 11:59 PM">
  <overrides>
    <override section_id="12345" due_at="Jan 20, 2025, 11:59 PM" />
    <override section_id="67890" due_at="Jan 22, 2025, 11:59 PM" />
  </overrides>

  Complete the homework assignment...
</assignment>
```

See the [`<override>` tag documentation](override_tag.md) for more details on section-specific dates.

## Full Example

```xml
<assignment
    title="Example Homework"
    due_at="Jan 1, 2025, 11:59 PM"
    available_from="Jan 1, 2025, 9:00 AM"
    available_to="Jan 1, 2025, 11:59 PM"
    points_possible="30"
    assignment_group="Homework"
    submission_types="external_tool"
    external_tool_tag_attributes="url=https://lti.int.turnitin.com/launch/gs-proxy">

    <description>
        Complete the homework by following [these instructions](instructions).

        Then upload your `.py` files to Gradescope.
    </description>
</assignment>
```
