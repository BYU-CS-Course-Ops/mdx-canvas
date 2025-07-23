# Course Info

The `course_info` file is a JSON configuration file used to configure and define key settings for your Canvas course deployment via **MDXCanvas**.

In addition to required values (such as `CANVAS_API_URL` and `CANVAS_COURSE_ID`), you can include optional fields to further customize your course setup.

## Available Fields

### `COURSE_NAME`

Defines the full display name of the course as it will appear in Canvas.

```json
{
  "COURSE_NAME": "Example Course"
}
```

### `COURSE_CODE`

A concise identifier for the course.

```json
{
  "COURSE_CODE": "EXAMPLE 101"
}
```

### `COURSE_IMAGE`

Specifies the filename of the course thumbnail image shown on the Canvas dashboard.

```json
{
  "COURSE_IMAGE": "example_course_image.png"
}
```

## Full Example

A complete `course_info` file might look like the following:

```json
{
  "CANVAS_API_URL": "https://byu.instructure.com/",
  "CANVAS_COURSE_ID": 12345,
  "LOCAL_TIME_ZONE": "America/Denver",
  "COURSE_NAME": "Example Course",
  "COURSE_CODE": "EXAMPLE 101",
  "COURSE_IMAGE": "example_course_image.png"
}
```
