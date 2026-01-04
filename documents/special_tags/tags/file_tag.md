# `<file>` Tag

The `<file>` tag uploads a file to Canvas and creates a download link. Use this to attach PDFs, code files, documents, or other resources.

## Attributes

### `path` (required)

Relative path to the file within your course content directory.

```xml
<file path="resources/syllabus.pdf" />
```

### `canvas_folder` (optional)

Canvas folder path to upload the file to. Organizes files in Canvas file storage.

```xml
<file path="resources/syllabus.pdf" canvas_folder="Course Documents" />
```

### `unlock_at` (optional)

Date/time when the file becomes available to students. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<file path="exam_solutions.pdf" unlock_at="Dec 20, 2025, 12:00 PM" />
```

### `lock_at` (optional)

Date/time when the file is no longer available to students. Format: `MMM d, yyyy, h:mm AM/PM`.

```xml
<file path="exam.pdf" lock_at="Dec 15, 2025, 11:59 PM" />
```

## Examples

### Basic File Attachment

```xml
<assignment title="Example Assignment">
    Please download the starter code:

    <file path="resources/starter_code.py" />
</assignment>
```

### Organized in Canvas Folder

```xml
<page title="Resources">
    Course materials:

    <file path="syllabus.pdf" canvas_folder="Course Documents" />
    <file path="schedule.pdf" canvas_folder="Course Documents" />
</page>
```

### Time-Restricted File Access

```xml
<page title="Exam Materials">
    <!-- Exam available for 2 hours -->
    <file
        path="midterm_exam.pdf"
        unlock_at="Feb 15, 2025, 9:00 AM"
        lock_at="Feb 15, 2025, 11:00 AM"
        canvas_folder="Exams" />

    <!-- Solutions available after exam -->
    <file
        path="midterm_solutions.pdf"
        unlock_at="Feb 15, 2025, 2:00 PM"
        canvas_folder="Exams" />
</page>
```
