# Migrating Legacy Content to Explicit `id` Attributes

This guide provides a reusable prompt for Codex or similar AI systems to migrate older MDXCanvas content to the explicit-`id` style.

Use this when updating a legacy course or documentation set that relied on older implicit resource identifiers.

## Purpose

Older MDXCanvas content sometimes omitted `id` attributes and relied on other fields such as `title`, `name`, or derived filenames.

The goal of this migration is to:

- add explicit `id` attributes wherever resource-defining tags are missing one
- preserve the resource identity those tags already implied before the migration
- avoid changing references that already work

## AI Migration Prompt

````text
You are migrating an MDXCanvas repository from legacy implicit resource identifiers to explicit `id` attributes.

Search the full repository for MDXCanvas tags, including:
- `*.canvas.md.xml`
- `*.canvas.md.xml.jinja`
- included markdown files
- demo content
- documentation examples
- any other files that embed MDXCanvas XML tags

Task:
- Find all MDXCanvas resource-defining tags that do not have an explicit `id`.
- Add an `id` that preserves the tag's current identity under the old behavior.
- Update example snippets in documentation so they match the new explicit-`id` style.
- Do not change any existing `id`.
- Do not rename titles, names, paths, or other visible content unless required to add the `id`.
- Do not change tag order, whitespace, or formatting more than necessary.
- If a tag already has an `id`, leave it alone.
- If a reference tag such as `<course-link>` or `<item content_id="...">` already points at an existing `id`, do not change that reference.
- Do not add new `id` attributes to `<mermaid>` tags or fenced Mermaid blocks just because they are missing.
- If a `<mermaid>` tag already has an `id`, leave it unchanged.

Use these migration rules:

1. `<page>`: if `id` is missing, set `id` equal to the current `title`.
2. `<assignment>`: if `id` is missing, set `id` equal to the current `title`.
3. `<quiz>`: if `id` is missing, set `id` equal to the current `title`.
4. `<module>`: if `id` is missing, set `id` equal to the current `title`.
5. `<announcement>`: if `id` is missing, set `id` equal to the current `title`.
6. `<group>`: if `id` is missing, set `id` equal to the current `name`.
7. `<md-page>`: if `id` is missing, set `id` equal to the intended page identifier used for references. Prefer the existing obvious page name from surrounding context or filename.
8. `<file>`:
    - do not add a new `id` when one is missing
    - if an `id` is already present, leave it unchanged
    - do not rewrite file examples just to add an `id`
9. `<zip>`:
    - do not add a new `id` when one is missing
    - if an `id` is already present, leave it unchanged
    - do not rewrite zip examples just to add an `id`
10. `<quarto-slides>`:
    - do not add a new `id` when one is missing
    - if an `id` is already present, leave it unchanged
    - do not rewrite quarto-slides examples just to add an `id`
11. `<mermaid>` and fenced Mermaid blocks:
    - do not add a new `id` when one is missing
    - if an `id` is already present, leave it unchanged
    - do not rewrite Mermaid examples just to add an `id`

Additional requirements:
- Preserve backward compatibility. The added `id` should match the legacy implicit identifier whenever that identifier was deterministic.
- When a tag's old identity came from `title` or `name`, copy that exact string into `id`.
- When inserting a new `id`, place it near the front of the attribute list, ideally before `title`, `name`, or `path`.
- Skip tags that are not resource-defining.
- Do not modify generated output files or unrelated prose except to update embedded MDXCanvas examples.

After editing:
- Summarize which files were changed.
- List any tags that could not be migrated confidently and require manual review.
````

## Notes

- Mermaid is intentionally excluded from required `id` backfills in this migration prompt. Leave Mermaid content alone unless it already has an `id`, in which case preserve it.
- For tags whose legacy ID came from `title` or `name`, keeping that exact value avoids accidental resource recreation during future deploys.
