# Content Design

## Understanding Inputs

Before creating any content, identify:

- **Topic and learning objectives** — what should students know or be able to do?
- **Existing course structure** — what modules, assignments, or pages already exist? Check `course.canvas.md.xml.jinja`
  and the `content/` directory.
- **Dates and constraints** — due dates, available-from windows, late policies

Extracting from lecture notes:

1. Find the main concept or skill (heading or first paragraph)
2. List subtopics — these become quiz questions or page sections
3. Find any deliverables (submittable work) — these become assignments
4. Note any linked resources (files, external URLs, starter code)

## Choosing Content Types

| Task                             | Content Type          | Why                               |
|----------------------------------|-----------------------|-----------------------------------|
| Explain a concept or show code   | `<page>`              | Static reference students revisit |
| Check comprehension              | `<quiz>`              | Low-stakes formative; auto-graded |
| Have students implement / submit | `<assignment>`        | Graded submission with due date   |
| Organize a week of content       | `<module>` + `<item>` | Canvas navigation container       |
| Distribute files / starter code  | `<file>` or `<zip>`   | Upload to Canvas files            |
| Course-wide notice               | `<announcement>`      | Pushed to students                |

## Typical Week Pattern

Recommended structure for a single week/topic:

1. **Prep quiz** — available the day before class, due at start of class
2. **Lecture page** — reference material for the week
3. **Assignment** — in-class activity or homework
4. **Module** — groups all three for Canvas navigation

Example skeleton:

```xml
<!-- In course.canvas.md.xml.jinja -->
<include path="content/quizzes/week3-prep.canvas.md.xml"/>
<include path="content/pages/week3-linked-lists.canvas.md.xml"/>
<include path="content/assignments/week3-lab.canvas.md.xml"/>

<module id="week-3" title="Week 3: Linked Lists">
    <item type="subheader" title="Preparation"/>
    <item type="quiz" content_id="week3-prep" indent="1"/>
    <item type="subheader" title="Lecture"/>
    <item type="page" content_id="week3-linked-lists" indent="1"/>
    <item type="subheader" title="Assignment"/>
    <item type="assignment" content_id="week3-lab" indent="1"/>
</module>
```

The prep quiz uses `available_from` (day before) and `due_at` (start of class):

```xml
<quiz id="week3-prep" title="Week 3 Prep Quiz"
      available_from="Jan 13, 2025, 12:00 PM"
      due_at="Jan 14, 2025, 9:00 AM"
      assignment_group="Quizzes">
    ...
</quiz>
```

## Linking Content Together

Three mechanisms for linking resources:

**1. Module items** — primary navigation; use `<item>` inside `<module>`:

```xml
<item type="page" content_id="week3-linked-lists" indent="1"/>
```

**2. `<course-link>`** — inline links from one resource to another:

```xml
<assignment title="Week 3 Lab">
    Before starting, review
    <course-link type="page" id="week3-linked-lists">the Linked Lists page</course-link>.
</assignment>
```

**3. Assignment descriptions referencing pages** — plain prose:

```md
See the [Week 3 intro page](#) for setup instructions before starting this lab.
```

(Use `<course-link>` instead of plain markdown links for automatic URL resolution.)

## When to Use Jinja

| Situation                                 | Decision                   |
|-------------------------------------------|----------------------------|
| >3 similar resources sharing structure    | Jinja template + args file |
| Course-wide variables (term, year, dates) | `global_args.yaml`         |
| Single one-off resource                   | Static `.canvas.md.xml`    |
| Conditional content per section or term   | Jinja `{% if %}`           |

See `jinja/skill.md` for full template patterns, function reference, and args file formats.

## Confirm-Before-Write Workflow

Always show a plan table before creating files:

```
| Resource Type | Title         | File Path                                       | Notes                     |
|---------------|---------------|-------------------------------------------------|---------------------------|
| Quiz          | Week 3 Prep   | content/quizzes/week3-prep.canvas.md.xml        | 8 Qs, MC + T/F            |
| Page          | Linked Lists  | content/pages/week3-linked-lists.canvas.md.xml  | code examples             |
| Module        | Week 3        | entry point                                     | links to both             |

Shall I proceed?
```

Workflow steps:

1. **Plan** — describe resources, titles, file paths, key settings
2. **Confirm** — show summary table and ask "Shall I proceed?"
3. **Write** — create the `.canvas.md.xml` or `.jinja` files
4. **Deploy** — run `mdxcanvas` to push to Canvas (requires `course_info` and `.env`)

## Validation Checklist

Before writing or after generating:

- [ ] Every `<item content_id>` matches an existing resource `id` (or `title` if no `id` was set)
- [ ] All date strings use `MMM d, yyyy, h:mm AM/PM` format (e.g., `Jan 15, 2025, 11:59 PM`)
- [ ] Every `assignment_group` value matches a `<group>` defined in `<assignment-groups>`
- [ ] Module items reference content that is included somewhere in the same entry point
- [ ] `.jinja` templates loop with correct access pattern for the args format used
- [ ] `course_info.json` and `.env` are NOT committed to source control
- [ ] When modifying an existing resource: if it has no `id`, set `id` = current `title` value and leave `title`
  unchanged before making any other edits (see "Modifying Existing Resources" below)

## Modifying Existing Resources

`id` is the stable identifier MDXCanvas uses to find and update a resource in Canvas. Without `id`, MDXCanvas uses
`title` as the lookup key — changing `title` without an `id` creates a new resource instead of updating the existing
one.

`id` will become required in a future version; add it now when you touch a resource.

**Rule:** When editing a resource that has no `id`, first add `id` equal to the current `title` (or `name` for
modules/groups), then make your changes — but do NOT change `title` in the same edit unless you intend a rename.

```xml
<!-- BEFORE (unsafe to rename) -->
<assignment title="Homework 1" due_at="...">

<!-- STEP 1: add id first, keep title the same -->
<assignment id="Homework 1" title="Homework 1" due_at="...">

<!-- STEP 2 (separate edit): now safe to rename title -->
<assignment id="Homework 1" title="Homework 1 (Updated)" due_at="...">
```

This pattern applies to `<assignment>`, `<quiz>`, `<page>`, `<module>`, and `<group>`.

## Quiz Design Guidelines

Question variety for a well-balanced quiz:

| Type                          | Target % |
|-------------------------------|----------|
| Multiple-choice               | 30–40%   |
| True/false                    | 20–30%   |
| Fill-in-the-blank or matching | 20–30%   |
| Multiple-answers or essay     | 10–20%   |

Additional guidelines:

- Cover the full breadth of the topic; avoid clustering all questions on one subtopic
- Use `shuffle_answers="true"` for multiple-choice quizzes to prevent answer sharing
- Prep quizzes: 5–10 questions, lower stakes (`assignment_group="Quizzes"`, `allowed_attempts="3"`)
- Midterms/finals: stricter settings (`time_limit`, `access_code`, `allowed_attempts="1"`)
