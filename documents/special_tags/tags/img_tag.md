# `<img>` Tag

The `<img>` tag uploads and embeds images in your Canvas content. Local image files are automatically uploaded to Canvas and referenced by their Canvas URL.

## Attributes

### `src` (required)

Path to the image file or URL.

- **Local files**: Relative path to an image file. The file will be uploaded to Canvas and the `src` will be replaced with the Canvas URL.
- **HTTP URLs**: External image URLs (e.g., `https://example.com/image.png`) are left unchanged.
- **Canvas plugin files**: URLs starting with `@@PLUGINFILE@@` are left unchanged.

```xml
<!-- Local file - will be uploaded -->
<img src="images/diagram.png" />

<!-- External URL - no upload -->
<img src="https://example.com/photo.jpg" />
```

### `canvas_folder` (optional)

Canvas folder path to upload the image to. Only applies to local files.

```xml
<img src="images/diagram.png" canvas_folder="Course Images" />
```

## Examples

### Embed Local Image

```xml
<page title="Introduction">
    Here's an overview diagram:

    <img src="diagrams/overview.png" alt="Course Overview" />
</page>
```

### Organize Images in Canvas Folder

```xml
<assignment title="Lab 1">
    <description>
        Follow the circuit diagram below:

        <img
            src="circuits/lab1_circuit.png"
            canvas_folder="Lab Diagrams"
            alt="Lab 1 Circuit" />
    </description>
</assignment>
```

### Use External Image

```xml
<page title="Resources">
    External reference material:

    <img src="https://example.com/reference_chart.png" alt="Reference Chart" />
</page>
```

## Notes

- Local image files are validated at build time - the file must exist at the specified path
- Uploaded images are given a Canvas URL in the format: `[canvas-url]/preview`
- Standard HTML `img` attributes like `alt`, `width`, and `height` can be used alongside MDXCanvas-specific attributes
