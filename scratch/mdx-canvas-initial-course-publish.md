# MDX Canvas Initial Course Publish

Created on: 2026-04-29
Created by: Gordon

## Details

Add MDX Canvas support for publishing all initial course resources.

- What problem does the feature address?
  - A CS 110 student found that Lab Zero Windows instruction links
    were unauthorized because the corresponding Canvas pages had not
    been published.
  - The pages had to be published manually during the Duck Dev
    meeting on April 28, 2026.
- What is the intent of the feature?
  - Make the initial course setup process publish all required Canvas
    resources so students do not hit unpublished-page errors.
  - Reduce manual cleanup after a course is generated or deployed.
- What details exist so far about this feature?
  - The need was discovered from Lab Zero links in CS 110.
  - The feature should support an initial course publish across all
    resources managed by MDX Canvas.
  - The exact resource types and Canvas API calls still need to be
    identified during implementation planning.

## Out-of-scope

- Redesigning Lab Zero content.
- Changing the Rubber Duck bot behavior.
- Building a broader Canvas permissions audit unless a separate
  backlog item captures that work.

## Dependencies

None identified yet.
