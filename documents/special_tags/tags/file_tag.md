# `<file>` Tag

The `<file>` tag uploads a single file (e.g., PDF, image, document) and makes it downloadable for students inside pages, assignments, or quizzes.

It is most commonly used to attach supplementary resources directly to course content.

## Attributes

### `name`

Sets the display name for the file in Canvas. This is how students will see it.

```xml
<file name="example_file.pdf" path="files/example_file.pdf" />
```

### `path`

Specifies the relative path to the file within your course content directory.

## Example

```xml
<assignment title="Example Assignment">
    <description>
        Please download the following file to complete the assignment:

        <file name="starter_code.py" path="resources/starter_code.py" />
    </description>
</assignment>
```
