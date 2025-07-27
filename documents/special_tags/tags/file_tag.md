# `<file>` Tag

The `<file>` tag uploads a single file (e.g., PDF, image, document) and makes it downloadable for students inside pages, assignments, or quizzes.

It is most commonly used to attach supplementary resources directly to course content.

## Attributes

### `path`

Specifies the relative path to the file within your course content directory.

## Example

```xml
<assignment title="Example Assignment">
    <description>
        Please download the following file to complete the assignment:

        <file path="resources/starter_code.py" />
    </description>
</assignment>
```
