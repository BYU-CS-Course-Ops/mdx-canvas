# `<announcement>` Tag

The `<announcement>` tag creates course-wide announcements. Announcements can be published immediately or scheduled for a future date.

## Attributes

### `title` (required)

The announcement title displayed in the course announcements section.

```xml
<announcement title="Welcome to the Course!">
  ...
</announcement>
```

### `id` (optional)

Unique identifier for the announcement. If not specified, defaults to the `title` value.

Use an explicit `id` when you need to change the announcement's title later without creating a new resource.

```xml
<announcement
    id="welcome_announcement"
    title="Welcome to the Course!">
  ...
</announcement>
```

### `publish_date` (optional, defaults to now)

When the announcement should be published. Format: `MMM d, yyyy, h:mm AM/PM`.

If omitted, the announcement is published immediately.

```xml
<!-- Scheduled for future -->
<announcement title="Important Update" publish_date="Jan 15, 2025, 8:00 AM">
  This update will appear on January 15th.
</announcement>

<!-- Published immediately -->
<announcement title="Immediate Announcement">
  This announcement is published right away.
</announcement>
```


## Content

The announcement body supports Markdown and HTML formatting. You can include text, links, and other elements.

```xml
<announcement title="Course Update" publish_date="Jan 1, 2025, 8:00 AM">
    Welcome to the course! Please check the syllabus for important dates.

    <course-link type="page" id="syllabus">View Syllabus</course-link>
</announcement>
```