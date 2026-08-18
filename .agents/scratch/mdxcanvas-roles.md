# MDXCanvas Roles

## Course Architect

Plans new course content and its structure before authoring. Needs best practices for organizing content, possibly using concepts such as units, days, lectures, assignments, modules, and files; entry-point and folder conventions; and decisions about when to use static content versus templates. This role should discuss course material and needs with a human user (course instructor) to suggest possible project structures to fit the needs. This role looks for ways to help the instructor simplify or standardize course organization where possible. 

## Content Author

Writes and edits course resources. Needs Canvas and helper tag syntax, attributes, examples, IDs, dates, includes, links, file uploads, Jinja templates, and args-file formats. Must understand safe updates and how source changes map to Canvas resources.

## Deployment Engineer

Validates, diagnoses, and deploys courses. Needs parsing and rendering diagnostics, validation rules, dry-run procedures, course configuration, credential handling, deployment options, cleanup behavior, and safeguards for destructive operations. Must understand the concept of a test course vs live/active course. Should know how to use the `canvasapi` python package to observe deployments in order to test or debug them. 
