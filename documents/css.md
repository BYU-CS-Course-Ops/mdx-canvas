# CSS Styling Guide

MDXCanvas supports attaching a custom CSS file to apply consistent styling across your generated course content. CSS styles are "baked in" (embedded directly) to the rendered HTML, ensuring that styles are preserved when content is deployed to Canvas.

This is especially useful for controlling the appearance of:

- Headings, text, and typography
- Tables
- Code blocks
- Page spacing
- Colors and custom styling

## How to Use Custom CSS

To include a custom CSS file when running MDXCanvas, use the `--css` flag:

```bash
mdxcanvas --course-info <course_info.yaml> --css <path/to/style.css> <content.canvas.md.xml>
```

Your stylesheet will be processed and styles will be embedded directly into the rendered Canvas content.

## Notes

* The CSS file must be a valid `.css` file.
* Canvas allows most basic styles (colors, fonts, layout), but may strip some advanced selectors or animations.
* Your styles will apply globally unless scoped with classes or element selectors.

## Example CSS (`style.css`)

```css
body {
  font-family: "Helvetica Neue", sans-serif;
  line-height: 1.6;
  color: #333;
}

h1, h2, h3 {
  color: #003366;
  border-bottom: 1px solid #ccc;
  padding-bottom: 0.2em;
}

table {
  border-collapse: collapse;
  width: 100%;
}

table th, table td {
  border: 1px solid #999;
  padding: 0.5em;
}

code {
  background-color: #f4f4f4;
  padding: 0.2em 0.4em;
  font-family: monospace;
  border-radius: 3px;
}
```
