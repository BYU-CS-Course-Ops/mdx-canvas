# Best-Practice Course Directory Layout

This is the recommended directory structure for an MDXCanvas course. Following this layout makes courses easier to
maintain, navigate, and deploy.

## Recommended Structure

```
my-course/
├── course_info.json              ← Canvas API credentials + course ID (NEVER commit this)
├── global_args.yaml              ← Course-wide Jinja variables (term, year, dates, weights)
├── style.css                     ← Optional: custom CSS applied to Canvas pages
├── course.canvas.md.xml.jinja   ← Main entry point — includes all content
│
├── content/
│   ├── syllabus.md               ← Syllabus content (included via <syllabus><include .../></syllabus>)
│   ├── assignments/
│   │   ├── homework.canvas.md.xml.jinja   ← Assignment template (loops over args)
│   │   └── homework_args.md               ← MarkdownData args table for homework
│   ├── quizzes/
│   │   └── quiz1.canvas.md.xml            ← Individual quiz
│   ├── pages/
│   │   └── week1.canvas.md.xml            ← Content pages
│   └── announcements/
│       └── welcome.canvas.md.xml          ← Announcements
│
├── images/                        ← Images uploaded via <img> tags
└── files/                         ← Files uploaded via <file> or <zip> tags
```

## Key Files Explained

### `course.canvas.md.xml.jinja` (Entry Point)

The entry point wraps everything in a `<div>` and uses `<include>` to pull in content files:

```xml
<div>
    <course-settings name="My Course" code="CS 101" />

    <syllabus> <include path="content/syllabus.md"/> </syllabus>

    <assignment-groups>
        <group name="Homework" weight="40" />
        <group name="Quizzes" weight="30" />
        <group name="Projects" weight="30" />
    </assignment-groups>

    <include path="content/assignments/homework.canvas.md.xml.jinja" />
    <include path="content/quizzes/quiz1.canvas.md.xml" />

    <module id="Week 1" title="Week 1: Introduction">
        <item type="page" content_id="Introduction" indent="1" />
        <item type="assignment" content_id="Homework 1" indent="1" />
    </module>
</div>
```

### `global_args.yaml` (Course-Wide Variables)

```yaml
term: fall2025
year: 2025
start_date: "Aug 25, 2025"
end_date: "Dec 12, 2025"
final_exam: "Dec 15, 2025, 11:00 AM"

Group_Weights:
  Homework: 40
  Quizzes: 20
  Projects: 30
  Final Exam: 10
```

### `course_info.json` (Deployment Config)

```json
{
    "CANVAS_API_URL": "https://byu.instructure.com/",
    "CANVAS_COURSE_ID": 12345,
    "LOCAL_TIME_ZONE": "America/Denver"
}
```

**Never commit `course_info.json` to source control.** Add it to `.gitignore`.

## Why This Layout

- **Separation of concerns**: entry point, content, assets are clearly separated
- **Reusable templates**: Jinja templates in `content/` loop over args tables
- **Easy deployment**: run `mdxcanvas --course-info course_info.json course.canvas.md.xml.jinja` from the course root
- **Scalable**: add new content types in their respective subdirectories
