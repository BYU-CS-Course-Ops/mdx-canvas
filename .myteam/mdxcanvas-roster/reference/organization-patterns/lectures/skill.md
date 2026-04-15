---
skill: organization-patterns/lectures
---

# Lectures

## When to Use This Reference

Use this reference whenever a request involves:

- Creating a Canvas page that presents lecture content
- Using `<md-page>` to generate a page from a `.md` file
- Embedding code examples in a lecture page via `<include>`
- Linking a lecture page into a Canvas module

---

## What Lectures Are in MDXCanvas

A "lecture" in MDXCanvas terms is a Canvas page that presents content for a specific topic or class session. Lecture
pages might contain:

- An overview of the topic
- Code examples or diagrams
- Links to readings or external resources
- Embedded images via `<img>`

---

## Creating a Lecture Page

### Inline in a `.canvas.md.xml` file

```xml
<page title="Week 3: Linked Lists">
    # Linked Lists

    A linked list is a linear data structure where each element points to the next.

    ## Key Operations

    - **Insert**: O(1) at head, O(n) at arbitrary position
    - **Delete**: O(1) with a reference, O(n) without
    - **Search**: O(n)
</page>
```

### From a Markdown file using `<md-page>`

Write lecture content in a standalone `.md` file and use `<md-page>` to create the Canvas page automatically. The first
`# Heading` becomes the page title.

```xml
<md-page path="content/pages/week3-linked-lists.md"/>
```

The `path` is relative to the file containing the `<md-page>` tag.

### Including a lecture in a module

Link the lecture page into a Canvas module using `<item>`. The `content_id` must match the `title` (or `id`) of the
`<page>` tag exactly.

```xml
<module id="week-3" title="Week 3: Data Structures">
    <item type="page" content_id="Week 3: Linked Lists" indent="1" />
    <item type="assignment" content_id="Homework 3" indent="1" />
</module>
```

---

## Embedding Code in Lectures

Use `<include>` to pull in a code file as a fenced block:

```xml
<page title="Sorting Example">
    Here is the starter code:

    <include path="code/sort.py" fenced="python" include_filename="true"/>
</page>
```

For full `<include>` attribute options, see `../../helper-tags/skill.md`.
