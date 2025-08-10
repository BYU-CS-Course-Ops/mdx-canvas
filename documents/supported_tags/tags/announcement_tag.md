# `<announcement>` Tag

The `<announcement>` tag is used to schedule or create immediate announcements within the course.

## Attributes

### `title`

Sets the title of the announcement. This is displayed prominently in the course announcements section.

```xml
<announcement title="Welcome to the Course!" />
```

### `publish_date`

Specifies when the announcement should be published. The date and time format is `MMM d, yyyy, h:mm AM/PM`. 
If not specified, the announcement is published immediately.

```xml
<announcement title="Important Update" publish_date="Jan 1, 2025, 8:00 AM" />
```


## Example

The content of the `<announcement>` tag can include text, links, and other HTML elements. 
Here’s an example of how to create an announcement:

```xml
<announcement title="Course Update" publish_date="Jan 1, 2025, 8:00 AM">
    Welcome to the course! Please check the syllabus for important dates.
    <course-link type="page" title="View Syllabus" />
</announcement>
```