# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run unit tests (no Canvas connection needed)
poetry run pytest tests/test_quiz_question_parsing.py tests/test_post_processing.py tests/test_parallel.py tests/test_jinja_template.py tests/test_stale_cleanup.py

# Run a single test
poetry run pytest tests/test_quiz_question_parsing.py::test_multiple_choice_answer_comments_are_included

# Run integration tests (requires CANVAS_API_TOKEN and a live course in testing_course_info.json)
poetry run pytest tests/resource-id-tests/

# Deploy to Canvas (from repo root)
mdxcanvas --course-info <course_info.yaml> <content_file>

# Dry run (preview without deploying)
mdxcanvas --course-info <course_info.yaml> --dry-run <content_file>

# Erase all content from a Canvas course
erasecanvas --course-info <course_info.yaml>
```

The `CANVAS_API_TOKEN` environment variable must be set for any live Canvas operations.

## Architecture

### Pipeline Overview

A content file flows through three stages:

1. **Text processing** (`mdxcanvas/text_processing/`) — Jinja2 rendering → Markdown-to-HTML → XML preprocessing
2. **XML processing** (`mdxcanvas/xml_processing/`) — XML tags → `CanvasResource` objects in a `ResourceManager`
3. **Deployment** (`mdxcanvas/deploy/`) — dependency resolution → Canvas API calls

`main.py:main()` orchestrates all three stages and is the single entry point.

### Two-Pass XML Processing

`xml_processing.py` runs two distinct passes over the XML:

- **`preprocess_xml()`** — handles *content-modifying* tags that expand inline into raw HTML: `<include>`, `<img>`, `<file>`, `<zip>`, `<md-page>`, `<mermaid>`, `<quarto-slides>`, `<course-settings>`. These tags disappear and leave HTML in their place.
- **`process_canvas_xml()`** — handles *Canvas resource* tags that map to Canvas objects: `<module>`, `<assignment>`, `<quiz>`, `<page>`, `<group>`, `<announcement>`, `<syllabus>`. Each tag processor converts the tag into a `CanvasResource` and adds it to the `ResourceManager`.

### Cross-Resource Linking

Resources reference each other's Canvas IDs via sentinel strings of the form `__@@type||id||field@@__`, produced by `get_key()` in `resources.py`. These appear wherever a Canvas ID is needed (e.g., a module item's `page_url` referencing a page's Canvas page URL). They are resolved to real IDs just before each resource is deployed in `update_links()` (`canvas_deploy.py`).

### Dependency Ordering and Shell Deployments

`algorithms.py:linearize_dependencies()` topologically sorts all resources based on their sentinel-string dependencies. Cyclic references (e.g., a page referencing itself, or two pages cross-linking) are broken by "shell deployments": a stub is deployed first (with empty content) to get a Canvas ID, then the full deployment follows in topological order. Only `assignment`, `page`, and `quiz` support shell deployments (see `SHELL_DEPLOYERS` in `canvas_deploy.py`).

Module ordering uses a simpler mechanism: each `ModuleTagProcessor` stores the previous module's ID in `module_data['_comments']['previous_module']`, creating a dependency chain so modules are created in template order.

### Change Detection

`deploy/checksums.py` stores MD5 checksums and Canvas IDs in `_md5sums.json` in Canvas Files (folder `_md5s`). A resource is only deployed if its checksum has changed or it has no stored checksum (new resource). `canvas_id` from the cache is attached to `resource['data']` before deployment so each deployer can decide create-vs-update.

### Resource Data Model

All resource data is a `CanvasResource` TypedDict with four fields: `type`, `id` (user-assigned stable key), `data` (dict passed to Canvas API), and `content_path`. Canvas-returned IDs and metadata live in the checksum cache (`canvas_info` dict), not in `CanvasResource` itself.

### Adding a New Resource Attribute

The pattern for adding an attribute to an existing tag:

1. Add an `Attribute(...)` entry to the `fields` list in the relevant `*_tags.py` tag processor. Use `parse_int` for integers, `parse_bool` for booleans, `make_id_parser` for cross-resource references.
2. The parsed value flows into `module_data` / `item_data` and is passed as-is to the Canvas API deployer in `deploy/<type>.py`.
3. The deployer calls `canvas_module.edit(module=data)` / `course.create_module(module=data)` — any key in `data` that Canvas accepts will be honored.
4. Update `documents/supported_tags/tags/<tag>_tag.md` with the new attribute.

### Integration Tests

`tests/resource-id-tests/` contains live Canvas integration tests. They require:
- `tests/resource-id-tests/testing_course_info.json` with a real course ID (not committed; copy from `scratch/testing_course_info.json` and fill in)
- The `erasecanvas` command is called at the start of each test to get a clean slate

Unit tests in `tests/` (non-integration) mock nothing — they test pure parsing functions directly and need no Canvas access.
