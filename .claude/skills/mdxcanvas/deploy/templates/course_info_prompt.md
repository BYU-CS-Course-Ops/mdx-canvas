# Course Info Prompt Template

When the `course_info` CONFIG file path has not been provided, use this exact prompt:

---

To deploy this content to Canvas, please provide the path to your `course_info.json` CONFIG file.

The CONFIG file should be a JSON file containing:

- `CANVAS_API_URL` - Your Canvas instance URL (e.g., `"https://byu.instructure.com/"`)
- `CANVAS_COURSE_ID` - The numeric course ID (found in the Canvas course URL)
- `LOCAL_TIME_ZONE` - Your timezone (e.g., `"America/Denver"`)

**Example `course_info.json`:**

```json
{
    "CANVAS_API_URL": "https://byu.instructure.com/",
    "CANVAS_COURSE_ID": 20736,
    "LOCAL_TIME_ZONE": "America/Denver"
}
```
