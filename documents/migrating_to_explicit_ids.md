# Migrating Legacy Content to Explicit `id` Attributes

This guide updates older MDXCanvas content to match the current repository behavior.

The current parser requires explicit `id` attributes on the main resource-defining tags, and module items must reference those ids explicitly. This is the behavior documented in the current tag docs and enforced in the parser code under `mdxcanvas/xml_processing/`.

## What the Current Repo Requires

These tags now require an explicit `id`:

- [`<page>`](supported_tags/tags/page_tag.md)
- [`<assignment>`](supported_tags/tags/assignment_tag.md)
- [`<quiz>`](supported_tags/tags/quiz_tag.md)
- [`<question>`](supported_tags/tags/quiz_question_types.md) inside `<quiz>`
- [`<module>`](supported_tags/tags/module_tag.md)
- [`<announcement>`](supported_tags/tags/announcement_tag.md)
- [`<group>`](supported_tags/tags/assignment_groups_tag.md)
- [`<md-page>`](special_tags/tags/md_page_tag.md)

Module items are also explicitly id-based now:

- [`<item>`](supported_tags/tags/item_tag.md) with `type="page"`, `type="assignment"`, `type="quiz"`, or `type="file"` must use `content_id="..."`, and that `content_id` must match the target resource id.
- `<item>` with `type="subheader"`, `type="externalurl"`, or `type="syllabus"` must have its own explicit `id`.
- For content items, `title` is only a display label. It is not a substitute for `content_id`.
- For `page`, `assignment`, `quiz`, and `file` items, you do not add a separate item-level source `id`; the current parser derives the module item identity from `content_id`.

The following tags still do not require a source-level `id` in the current code:

- `<file>`: identity is currently derived from the uploaded filename (`path.name`)
- `<zip>`: identity is currently derived from `name`, or from the generated zip filename when `name` is omitted
- `<quarto-slides>`: identity is currently derived from the rendered slide filename
- `<mermaid>`: identity is currently derived from `name` if present, otherwise from the diagram content hash

## Legacy Implicit ID Behavior

- `<page>`: if `id` was omitted, the resource id defaulted to `title`.
- `<assignment>`: if `id` was omitted, the resource id defaulted to the assignment title.
- `<quiz>`: if `id` was omitted, the resource id defaulted to `title`.
- `<question>`: if `id` was omitted, the parser generated `q` followed by the zero-based index of the question inside that quiz's `<questions>` block, such as `q0`, `q1`, `q2`.
- `<module>`: if `id` was omitted, the resource id defaulted to the visible module name.
- `<announcement>`: if `id` was omitted, the resource id defaulted to `title`.
- `<group>`: if `id` was omitted, the resource id defaulted to `name`.
- `<md-page>`: `id` used to be optional. When omitted, the generated `<page>` also had no explicit id, so the final page identity fell back to the resolved page title. That title came from the explicit `title` attribute when present, otherwise from the first markdown heading, otherwise from the markdown filename stem.
- `<item type="subheader">`: if `id` was omitted, the item id defaulted to `title`.
- `<item type="externalurl">`: if `id` was omitted, the item id defaulted to `title` when present, otherwise to `external_url`.
- `<item type="syllabus">`: if `id` was omitted, the item id defaulted to `title` when present, otherwise to the default title `Syllabus`.
- `<item type="page|assignment|quiz|file">`: these items did not auto-generate their own independent source ids. Their module-item identity was derived from `content_id`, so preserving or updating `content_id` correctly is the migration-sensitive part.

## Migration Rules

When backfilling missing ids, preserve the legacy identity whenever it was already implied by the old content:

1. `<page>`: if `id` is missing, set `id` to the current `title`.
2. `<assignment>`: if `id` is missing, set `id` to the current `title`.
3. `<quiz>`: if `id` is missing, set `id` to the current `title`.
4. `<question>`: if `id` is missing, add the legacy-generated value when you can determine it confidently. Under the previous behavior this was `q` plus the zero-based question index within the quiz, such as `q0`, `q1`, `q2`. Do not renumber those ids later unless you intentionally want the questions treated as different resources.
5. `<module>`: if `id` is missing, set `id` to the current visible module name. In current docs this is `title`; in some older content it may still be stored as `name`.
6. `<announcement>`: if `id` is missing, set `id` to the current `title`.
7. `<group>`: if `id` is missing, set `id` to the current `name`.
8. `<md-page>`: if `id` is missing, set `id` to the page identifier already used by module items and course links. If there is no existing reference, use a stable file-based name and then update references to match it.
9. `<item type="page|assignment|quiz|file">`: if `content_id` is missing, add it. The value must equal the target resource's explicit `id`. For `file` items, use the deployed filename that the current code derives from the `<file path="...">` tag.
10. `<item type="subheader|externalurl|syllabus">`: if `id` is missing, add the value the old parser would have used: usually `title`, or `external_url` when an external URL item had no title.
11. If you change or add ids on resources, update all references that point at them. Common cases include `<item content_id="...">`, `<course-link id="...">`, `prerequisite_module_ids`, and `assignment_group`.
12. Do not add new `id` attributes to `<file>`, `<zip>`, `<quarto-slides>`, or `<mermaid>` just for this migration. The current code does not consume them as source-level ids.

## Minimal Example

Before:

```xml
<page title="Introduction">
    Welcome to the course.
</page>

<module title="Week 1">
    <item type="page" title="Introduction" />
</module>
```

After:

```xml
<page id="Introduction" title="Introduction">
    Welcome to the course.
</page>

<module id="Week 1" title="Week 1">
    <item type="page" content_id="Introduction" title="Introduction" />
</module>
```

## AI Migration Prompt

````text
You are migrating an MDXCanvas repository to the current explicit-id style required by the repo.

Search the full repository for MDXCanvas tags, including:
- `*.canvas.md.xml`
- `*.canvas.md.xml.jinja`
- included markdown files
- demo content
- documentation examples
- any other files that embed MDXCanvas XML tags

Task:
- Find all tags that now require explicit `id` values under the current repo behavior.
- Add missing `id` attributes while preserving the old resource identity whenever that identity was already implied.
- Update module items so they use explicit id-based references.
- Update embedded documentation examples so they match the current explicit-id style.
- Do not change any existing `id`.
- Do not rename visible titles, names, paths, URLs, or other user-facing content unless that is required to add the missing `id` or reference.
- Do not change formatting more than necessary.

Use these rules:

1. `<page>`: if `id` is missing, set `id` equal to `title`.
2. `<assignment>`: if `id` is missing, set `id` equal to `title`.
3. `<quiz>`: if `id` is missing, set `id` equal to `title`.
4. `<question>`: if `id` is missing, add the legacy-generated value when you can determine it confidently. Under the old behavior this was `q` plus the zero-based question index within the quiz, such as `q0`, `q1`, `q2`.
5. `<module>`: if `id` is missing, set `id` equal to the visible module name (`title` in current docs, sometimes `name` in older files).
6. `<announcement>`: if `id` is missing, set `id` equal to `title`.
7. `<group>`: if `id` is missing, set `id` equal to `name`.
8. `<md-page>`: if `id` is missing, set `id` to the existing page identifier used by references; otherwise use a stable file-based identifier and update references.
9. `<item type="page|assignment|quiz|file">`: ensure `content_id` is present and matches the target resource id. Do not add a separate item-level source `id` for these item types.
10. `<item type="subheader|externalurl|syllabus">`: ensure `id` is present, using the old implicit value when available (`title`, or `external_url` for untitled external URL items).
11. Update references such as `<item content_id="...">`, `<course-link id="...">`, `prerequisite_module_ids`, and `assignment_group` when their target ids change.
12. Do not add new source-level `id` attributes to `<file>`, `<zip>`, `<quarto-slides>`, or `<mermaid>`.

Additional requirements:
- Preserve backward compatibility. When the old identity came from `title` or `name`, copy that exact string into `id`.
- When inserting a new `id`, place it near the front of the attribute list when practical.
- Skip tags that are not resource-defining and are not id-based references.
- Do not modify generated files.

After editing:
- Summarize which files were changed.
- List anything that still needs manual review, especially ambiguous `<md-page>` ids or question ids.
````

## Notes

- The parser enforcement for these rules currently lives in `page_tags.py`, `assignment_tags.py`, `quiz_tags.py`, `quiz_questions.py`, `module_tags.py`, `announcement_tags.py`, `group_tags.py`, and `tag_preprocessors.py`.
