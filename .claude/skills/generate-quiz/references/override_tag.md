# `<override>` Tag

The `<override>` tag specifies section-specific dates for assignments or quizzes. Use this when different course sections need different due dates or availability windows.

## Usage

Override tags must be placed inside an `<overrides>` container within an `<assignment>` or `<quiz>` tag.

## Attributes

### `section_id` (required)

The Canvas section ID. This determines which section the override applies to.

```xml
<override section_id="12345" due_at="Jan 20, 2025, 11:59 PM" />
```

### `due_at` (optional)

Override due date for this section. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<override section_id="12345" due_at="Jan 20, 2025, 11:59 PM" />
```

### `available_from` (optional)

When the assignment/quiz becomes available for this section. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<override section_id="12345" available_from="Jan 15, 2025, 9:00 AM" />
```

### `available_to` (optional)

When the assignment/quiz is no longer available for this section. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<override section_id="12345" available_to="Jan 25, 2025, 11:59 PM" />
```

### `late_due` (optional)

Latest date to accept late submissions for this section. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<override section_id="12345" late_due="Jan 22, 2025, 11:59 PM" />
```

## Examples

### Assignment with Section Overrides

```xml
<assignment
    title="Homework 1"
    due_at="Jan 15, 2025, 11:59 PM"
    available_from="Jan 8, 2025, 9:00 AM">

  <overrides>
    <!-- Section A gets extra time -->
    <override section_id="12345" due_at="Jan 20, 2025, 11:59 PM" />

    <!-- Section B gets even more time -->
    <override section_id="67890" due_at="Jan 22, 2025, 11:59 PM" />
  </overrides>

  Complete the homework assignment by the due date.
</assignment>
```

### Quiz with Different Availability Windows

```xml
<quiz
    title="Midterm Exam"
    due_at="Feb 15, 2025, 11:59 PM">

  <overrides>
    <!-- Morning section takes exam earlier -->
    <override
        section_id="11111"
        available_from="Feb 15, 2025, 8:00 AM"
        available_to="Feb 15, 2025, 10:00 AM"
        due_at="Feb 15, 2025, 10:00 AM" />

    <!-- Afternoon section takes exam later -->
    <override
        section_id="22222"
        available_from="Feb 15, 2025, 1:00 PM"
        available_to="Feb 15, 2025, 3:00 PM"
        due_at="Feb 15, 2025, 3:00 PM" />
  </overrides>

  <description>
    Complete the midterm exam during your section's time window.
  </description>

  <questions>
    ...
  </questions>
</quiz>
```

## Finding Section IDs

To find your Canvas section IDs:

1. Go to your course in Canvas
2. Navigate to **Settings** → **Sections**
3. Click on a section name
4. The section ID is in the URL: `.../courses/COURSE_ID/sections/SECTION_ID`
