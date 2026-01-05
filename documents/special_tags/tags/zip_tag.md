# `<zip>` Tag

The `<zip>` tag is used to upload and include a `.zip` file in the course. This is useful for bundling related resources — such as starter code, datasets, or reference documents — and distributing them as a single download.

## Attributes

### `name` (optional)

The name of the resulting zip file that students will download. If not specified, automatically uses the filename from the `path`.

```xml
<!-- Explicit name -->
<zip name="assignment_resources.zip" path="resources" />

<!-- Auto-generated name from path (uses "resources.zip") -->
<zip path="resources" />
```

### `path`

Specifies the source directory (relative path) to zip. All contents from this path will be included.

```xml
<zip name="lab1.zip" path="labs/lab1_files" />
```

### `additional_files` (optional)

A comma-separated list of additional files (outside the `path`) to include in the zip.

```xml
<zip name="lab1.zip" path="labs/lab1" additional_files="shared/utils.py,README.md" />
```

### `priority_path` (optional)

Specifies a folder inside the zip to prioritize.

```xml
<zip name="lab1.zip" path="labs/lab1" priority_path="labs/lab1/starter" />
```

### `exclude` (optional)

A regex pattern for excluding specific files or folders from the zip archive.

```xml
<zip name="lab1.zip" path="labs/lab1" exclude=".*\.tmp" />
```

This would exclude all `.tmp` files.

### `canvas_folder` (optional)

Canvas folder path to upload the zip file to. Organizes files in Canvas file storage.

```xml
<zip path="labs/lab1" canvas_folder="Lab Materials" />
```

## Example

```xml
<assignment title="Lab 1">
    <description>
        Download the zip file below to get the starter files for this lab.

        <zip 
            name="lab1_resources.zip"
            path="labs/lab1"
            additional_files="shared_utils.py"
            priority_path="labs/lab1/starter"
            exclude=".*\.log"
        />
    </description>
</assignment>
```

Another example can be found in the demo course [here](../../../demo_course/pages/syllabus.md.jinja).
