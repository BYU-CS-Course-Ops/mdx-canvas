# `<course-settings>` Tag

The `<course-settings>` tag configures course metadata such as the course name, course code, and course image. This is useful for programmatically setting or updating course information.

## Attributes

At least one of `name`, `code`, or `image` must be specified.

### `name` (optional)

The display name of the course.

```xml
<course-settings name="Introduction to Computer Science" />
```

### `code` (optional)

The course code (e.g., CS 101, MATH 200).

```xml
<course-settings code="CS 101" />
```

### `image` (optional)

Relative path to an image file to use as the course banner/image.

```xml
<course-settings image="course_banner.png" />
```

### `canvas_folder` (optional)

Canvas folder path to upload the course image to. Only applies when `image` is specified.

```xml
<course-settings image="course_banner.png" canvas_folder="Course Assets" />
```

## Examples

### Set Course Name and Code

```xml
<course-settings
    name="Introduction to Computer Science"
    code="CS 101" />
```

### Set Course Image

```xml
<course-settings
    image="images/cs101_banner.png"
    canvas_folder="Branding" />
```

### Set All Course Metadata

```xml
<course-settings
    name="Data Structures and Algorithms"
    code="CS 235"
    image="images/cs235_banner.png"
    canvas_folder="Course Images" />
```
