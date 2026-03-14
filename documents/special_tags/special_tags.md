# Special Tags

These tags provide advanced functionality like file inclusion, modular content reuse, and downloadable resources.

Click a tag below to view its full documentation and examples.

For legacy repositories that need explicit resource IDs added across course files and documentation examples, see the [AI migration prompt](../migrating_to_explicit_ids.md).

## Course Configuration

- [`<course-settings>`](tags/course_settings_tag.md)
  Set course metadata including name, course code, and course image.

## File Inclusion & Linking

- [`<include>`](tags/include_tag.md)
  Embeds external file content (e.g., `.md`) directly into another tag.

- [`<md-page>`](tags/md_page_tag.md)
  Creates a Canvas page from a markdown file with automatic title detection.

- [`<file>`](tags/file_tag.md)
  Uploads and links a single file (e.g., PDF, image, code sample).

- [`<img>`](tags/img_tag.md)
  Uploads and embeds images in Canvas content.

- [`<mermaid>`](tags/mermaid_tag.md)
  Renders Mermaid diagrams to PNG and uploads them to Canvas. Supports inline diagrams and external `.mmd` files.

- [`<zip>`](tags/zip_tag.md)
  Includes a `.zip` archive and manages its structure and filters.

- [`<quarto-slides>`](tags/quarto_slides_tag.md)
  Renders a `.qmd` file with Quarto and uploads the generated slide deck as a Canvas file link.

- [`<course-link>`](tags/course_link_tag.md)
  Link to other course items (pages, assignments, quizzes) using their type and title.
