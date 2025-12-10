# `<course_link>` Tag

The `<course_link>` tag  creates a link to a canvas item (like a page, assignment, or quiz) within a page or assignment.

This allows you to reference other course content without needing to hard-code URLs, making it easier to maintain 
links as your course evolves.

## Attributes

### `type`

Specifies the canvas item type you are linking to. Valid values include:

- `page` - Links to a page in the course.
- `assignment` - Links to an assignment.
- `quiz` - Links to a quiz.

### `title`

This is the title of the item you are linking to. It should match the title of the page, assignment, or quiz exactly.

## Example

If you have a page titled "Introduction" and you want to link to it, you would use:

```xml
<course-link type="page" title="Introduction" />
```

Another example can be found in the demo course [here](../../../demo_course/pages/module_overview_args.md)