# `<assignment>` Tag

The `<assignment>` tag is used to define an assignment in the course. It supports various attributes and a child `<description>` element.

## Attributes

### `title`

Sets the assignment title.

```xml
<assignment 
    title="Example Assignment">
...
</assignment>
```

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

## Description

The assignment body is contained within a `<description>` child tag. Markdown or HTML formatting is supported.

```xml
<assignment title="Example Assignment">

    <description>
        # Example Assignment

        This is an example assignment description. You can use **Markdown** or _HTML_.

        ## Instructions
        1. Read the assignment.
        2. Complete the tasks.
        3. Submit your work before the deadline.
    </description>
</assignment>
```

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
