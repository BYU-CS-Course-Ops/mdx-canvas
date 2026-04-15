---
skill: organization-patterns/modules
---

# Modules

## When to Use This Reference

Use this reference whenever a request involves:

- Organizing 14+ weekly modules in a semester course
- Understanding module naming conventions
- Setting prerequisite locks between modules
- Understanding how module items map to Canvas navigation

---

## Non-Negotiables

- Every module `<item content_id>` must match an existing resource `id` (or `title`).
- Set an explicit `id` on modules used as prerequisite targets.
- Do not rename a module's `title` without first adding `id` equal to the current title.

---

## Modules as Week Containers

In a semester course, each week typically gets one module. Modules are the primary student navigation in Canvas.
Students see modules listed in order on the Canvas Modules page and track their completion through them.

---

## Module Naming Conventions

| Pattern          | Example `id`       | Example `title`            |
|------------------|--------------------|----------------------------|
| Sequential weeks | `week-1`           | `Week 1: Introduction`     |
| Unit-prefixed    | `unit2-week3`      | `Week 3: Dictionaries`     |
| Topic-based      | `trees-and-graphs` | `Unit 4: Trees and Graphs` |

---

## Semester-Scale Module Example

```xml
<module id="week-1" title="Week 1: Getting Started">
    <item type="subheader" title="Preparation"/>
    <item type="quiz" content_id="week1-prep" indent="1"/>
    <item type="subheader" title="Lecture"/>
    <item type="page" content_id="week1-intro" indent="1"/>
    <item type="subheader" title="Assignment"/>
    <item type="assignment" content_id="homework-1" indent="1"/>
</module>

<module id="week-2" title="Week 2: Variables and Types" prerequisite_module_ids="week-1">
    <item type="subheader" title="Preparation"/>
    <item type="quiz" content_id="week2-prep" indent="1"/>
    <item type="subheader" title="Lecture"/>
    <item type="page" content_id="week2-variables" indent="1"/>
    <item type="subheader" title="Assignment"/>
    <item type="assignment" content_id="homework-2" indent="1"/>
</module>

<module id="week-3" title="Week 3: Control Flow" prerequisite_module_ids="week-2">
    <item type="subheader" title="Preparation"/>
    <item type="quiz" content_id="week3-prep" indent="1"/>
    <item type="subheader" title="Lecture"/>
    <item type="page" content_id="week3-control-flow" indent="1"/>
    <item type="subheader" title="Assignment"/>
    <item type="assignment" content_id="homework-3" indent="1"/>
</module>
```

---

## When to Use `prerequisite_module_ids`

Use `prerequisite_module_ids` sparingly. Lock a module when students must complete the prior week's work before
proceeding. Do not lock every module — it creates friction for students catching up.

---

## Module Items and Canvas Sidebar

Students see modules listed in order in the Canvas Modules page. Each module item appears as a clickable entry. Items
link to quizzes, assignments, and pages by `content_id` or `title`.

---

For full `<module>` and `<item>` attribute reference, see `../../canvas-tags/module/skill.md`.
