---
type: workflow
description: Run this workflow if you need to do a general review of the code-base. 
output: 
    report_file: path to file containing findings from this review
---

Do a full review of the current codebase (`src/myteam/**`), looking for code-quality concerns. Approach this task as a senior dev would when looking at a junior dev's work, looking for opportunities to improve quality, style, design, etc.

As needed, read documents in `src/governing_docs/` to understand the intended design of the application.

Are we building tech debt? Is there logical duplication? Are there complex functions that should be decomposed?

Is the code organized intuitively? Packages, modules, functions.

Is there bloat? Over-engineering? Can you see a simpler way to solve the problems being addressed?

- *Does this need to exist at all?* (YAGNI)
- *Stdlib does it?
- *Native platform feature covers it?*
- *Already-installed dependency solves it?*
- *Available 3rd party dependency solves it?* 
- *Can it be done in less code (without become obtuse or clever)?* 

Write a report with your findings. Name it `spring-cleaning-report-<YYYY-MM-DD>.md`. 

For each concern identified, include:

- title: a brief title of the concern (h2)
- severity: how critical is this concern (bold)
- description: what should be addressed and why

Example:

```markdown
## Unnecessary indirection in `foo`
**Low**

Function `foo` in `foobar.py` simply calls `bar` with identical arguments. Calls to `foo` should be replaced with calls directly to `bar`. 
```
