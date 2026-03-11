# Units

## What Units Are

Units are the top-level thematic groupings of a course. A unit typically spans multiple weeks and represents a major
topic area — for example:

- Unit 1: Introduction to Python
- Unit 2: Data Structures
- Unit 3: Algorithms

Units are a conceptual organizational layer, not a Canvas-native concept. In MDXCanvas, units map to groups of Canvas
modules.

## How Units Map to Canvas

Each unit typically corresponds to a set of Canvas modules. For example, "Unit 2: Data Structures" might contain modules
for Week 3, Week 4, and Week 5.

In the entry point file, units are represented by a sequence of `<module>` tags that belong to the same thematic block:

```xml
<!-- Unit 2: Data Structures -->
<module id="unit2-week3" title="Week 3: Lists and Tuples">
    <item type="page" content_id="lists-intro" indent="1" />
    <item type="quiz" content_id="Lists Quiz" indent="1" />
</module>

<module id="unit2-week4" title="Week 4: Dictionaries">
    <item type="page" content_id="dicts-intro" indent="1" />
    <item type="assignment" content_id="Homework 4" indent="1" />
</module>
```

## Naming Conventions for Units

Use kebab-case for file and directory names:

| Item                     | Example                              |
|--------------------------|--------------------------------------|
| Unit directory           | `content/unit2-data-structures/`     |
| Unit quiz file           | `unit2-quiz.canvas.md.xml`           |
| Unit assignment template | `unit2-homework.canvas.md.xml.jinja` |

For global args, you can define unit-level metadata:

```yaml
unit2_title: "Data Structures"
unit2_start: "Sep 15, 2025"
unit2_end: "Oct 3, 2025"
```
