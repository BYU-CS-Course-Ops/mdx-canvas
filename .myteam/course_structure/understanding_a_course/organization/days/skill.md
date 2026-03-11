# Days

## What Days Represent

A "day" in MDXCanvas represents a single class session or calendar day within a unit. Day-level organization is used
when you need to:

- Publish content or assignments on a specific date
- Schedule readings or preparatory materials before a class session
- Control when quizzes open and close around a lecture

## How Days Map to Content

Days are not a Canvas-native concept. In MDXCanvas, day-level granularity is expressed through date attributes on
assignments and quizzes:

```xml
<assignment
    title="Day 5 Reading Quiz"
    due_at="Sep 19, 2025, 11:59 PM"
    available_from="Sep 17, 2025, 12:00 AM"
    points_possible="10"
    assignment_group="Quizzes">

    Complete the reading on linked lists before class on Sep 19.
</assignment>
```

For Jinja-templated content, day-level data lives in the args file:

```md
| Title              | Due_At                  | Available_From          | Points_Possible |
|--------------------|-------------------------|-------------------------|-----------------|
| Day 1 Prep Quiz    | Aug 27, 2025, 11:59 PM  | Aug 25, 2025, 12:00 AM  | 10              |
| Day 2 Prep Quiz    | Aug 29, 2025, 11:59 PM  | Aug 27, 2025, 12:00 AM  | 10              |
| Day 3 Prep Quiz    | Sep 3, 2025, 11:59 PM   | Sep 1, 2025, 12:00 AM   | 10              |
```

## Date Format

All date/time attributes use this format: `MMM d, yyyy, h:mm AM/PM`

Examples: `Jan 15, 2025, 11:59 PM` · `Sep 19, 2025, 9:00 AM`

The timezone is set by `LOCAL_TIME_ZONE` in `course_info`.
