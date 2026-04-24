---
id: canvas-tags-announcement
description: Syntax and attribute reference for the <announcement> tag.
---

# `<announcement>` Tag

## When to Use This Reference

Use this reference when working with:

- Creating course announcements
- Scheduling announcements for future publication

## Non-Negotiables

- Use `MMM d, yyyy, h:mm AM/PM` for `published_at`.

---

## Attributes

| Attribute      | Required | Description                                                        |
|----------------|----------|--------------------------------------------------------------------|
| `title`        | yes      | Announcement title shown in Canvas                                 |
| `id`           | no       | Stable identifier; defaults to `title`                             |
| `published_at` | no       | Date/time the announcement is published: `MMM d, yyyy, h:mm AM/PM` |

---

## Content

The body of the tag supports Markdown or HTML.

---

## Example

```xml
<announcement title="Welcome to the Course"
              published_at="Jan 13, 2025, 8:00 AM">
    # Welcome!

    Welcome to the course. Please review the syllabus and complete the orientation quiz before our first class.

    See you soon!
</announcement>
```

---

## Skeleton Template

```xml
<announcement title="[ANNOUNCEMENT TITLE]"
              published_at="[MMM d, yyyy, h:mm AM/PM]">
    # [ANNOUNCEMENT TITLE]

    [Announcement body here.]
</announcement>
```
