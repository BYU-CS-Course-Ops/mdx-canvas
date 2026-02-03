# Error Message Templates

Use these templates for consistent error messaging during deployment failures.

## Missing Course Info

```
**Deployment Error:** No course info provided.

Please provide the path to your `course_info` CONFIG file to proceed with deployment.
```

## Invalid Course Info

```
**Deployment Error:** Invalid course info file.

The CONFIG file must be a valid JSON containing:
- `CANVAS_API_URL`
- `CANVAS_COURSE_ID`
- `LOCAL_TIME_ZONE`
```

## API Token Missing

```
**Deployment Error:** Canvas API token not configured.

Please ensure the API token is set in the `.env` file.
```

## Deployment Command Failed

```
**Deployment Error:** The deployment command failed.

Error details:
[Include the actual error message from mdxcanvas]

Please check:
1. The content file exists and is valid
2. The course info is correct
3. The Canvas API token has proper permissions
```

## Content File Not Found

```
**Deployment Error:** Content file not found.

The specified file does not exist: [file path]

Please verify the file path and try again.
```
