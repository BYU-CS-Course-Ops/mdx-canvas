# Content Author Role Research: Onboarding Instructions

## Task

Create or revise a standalone **MDXCanvas Content Author** role document.

The role should teach an agent to write and safely edit Canvas resources from MD/XML/Jinja source. Ground it in MDXCanvas's reference skills and in representative examples from the three real course repositories. Do not turn it into a generic instructional-design guide or a deployment runbook.

The finished role should cover:

- Content Author responsibilities and boundaries relative to Course Architect and Deployment Engineer;
- how source files flow from an entry point through includes, Jinja templates, args/metadata, Markdown bodies, and assets into Canvas resources;
- Canvas resource tags and helper tags, including their important attributes;
- stable resource identity (`id` versus `title`) and safe update/rename behavior;
- dates, course/term args, section overrides, links, uploads, zips, images, and generated pages;
- static resources versus repeated Jinja templates and args-file formats;
- how assignments, quizzes/questions, pages, modules/items, announcements, syllabi, and files are represented;
- how to inspect an existing course before making a change;
- what to validate and what to hand off for deployment;
- concrete examples and cautionary lessons from the reference courses.

Write working files only under `.agents/scratch/`.

## Working Method

1. Read the role descriptions first and preserve their scope boundaries.
2. Load this repository's `.myteam/mdxcanvas-roster/` reference and update-resource guidance, then verify important claims against the current `./mdxcanvas/` implementation. Treat the local roster as author-facing guidance and the source as the authority on what this checkout actually accepts; the course repositories are examples and may contain old, inconsistent, or questionable patterns.
3. For each course, trace the main entry point into representative includes, templates, args, Markdown, and assets. Do not read every course resource.
4. Compare three distinct authoring patterns:
   - **CS 110:** one large discovery-driven template generates repeated day/lecture/lab/homework/project resources from folders and day metadata;
   - **CS 312:** explicit unit modules plus shared catalog templates driven by Markdown tables;
   - **CS 301R:** lecture-outline MarkdownData documents act as rich per-lecture source records consumed by one global template.
5. Collect examples by feature rather than trying to summarize all course content: identity, dates, include behavior, question types, module links, file packaging, Jinja data loading, and conditional resources.
6. Record both useful patterns and hazards. In particular, look for title-based references, duplicate includes, hard-coded dates, filename/path assumptions, generated or archived files, solution packaging, and content that exists on disk but is not included in the deployed graph.
7. Explain safe authoring behavior as rules, while labeling repository-specific conventions as examples rather than universal requirements.
8. Keep deployment credentials, dry-run commands, and destructive cleanup in the Deployment Engineer role. The Content Author should prepare and validate deployable source, then hand it off.
9. Before finishing, check that the role contains concrete paths, an edit workflow, syntax/reference routing, identity safeguards, validation guidance, and a concise handoff contract.

## Required Project Files

Read these first:

- `.agents/scratch/mdxcanvas-roles.md`
- `.agents/scratch/mdxcanvas-content-author-role.md` if revising an existing draft
- `.agents/scratch/course-architect-onboarding.md` for format and role-boundary context

## Authoritative MDXCanvas Guidance

Use this repository's roster, not the copy embedded in the CS 312 repository. Load roster skills through `myteam`; do not open their `skill.md` files manually:

```bash
myteam load .myteam/mdxcanvas-roster/skill.md
myteam load .myteam/mdxcanvas-roster/reference/skill.md
myteam load .myteam/mdxcanvas-roster/workflows/update-resource/skill.md
```

From the local reference hub, load every sub-skill needed by the role document:

```bash
myteam load .myteam/mdxcanvas-roster/reference/course-setup/skill.md
myteam load .myteam/mdxcanvas-roster/reference/canvas-tags/skill.md
myteam load .myteam/mdxcanvas-roster/reference/helper-tags/skill.md
myteam load .myteam/mdxcanvas-roster/reference/jinja/skill.md
myteam load .myteam/mdxcanvas-roster/reference/organization-patterns/skill.md
```

Follow the canvas-tag hub into the local resource-specific skills for assignments, quizzes/questions, pages, modules/items, announcements, and syllabi. Load `.myteam/mdxcanvas-roster/workflows/new-course/skill.md` only as supporting context; its broad scaffolding and course-design prescriptions should not override the narrower Content Author scope.

The critical update invariant is: **never change a resource's `title` without first giving it a stable `id` equal to its current title.** Without an explicit stable ID, a rename can create a duplicate rather than update the existing Canvas resource. Tags without the `id` attribute are widely deprecated, and any tag that supports the `id` attribute should use it as a future version of `mdxcanvas` will require it. Not only are IDs essentials for handling existing resources needing a title change, but all tags should be updated to include IDs. 

### Current implementation as a second authority

Use `./mdxcanvas/` to confirm what the installed checkout actually parses and how source maps to resources. Prefer these files:

- `mdxcanvas/xml_processing/xml_processing.py` — definitive registry of recognized Canvas resource tags and helper preprocessors.
- `mdxcanvas/xml_processing/attributes.py` — date, boolean, list, dictionary, required-attribute, and unknown-attribute behavior.
- `mdxcanvas/xml_processing/assignment_tags.py`, `quiz_tags.py`, `page_tags.py`, `module_tags.py`, `announcement_tags.py`, `group_tags.py`, and `syllabus_tags.py` — actual accepted attributes, required fields, resource IDs, nested overrides, and module-item reference behavior.
- `mdxcanvas/xml_processing/quiz_questions.py` — actual supported question types, answer child tags, comments, scoring defaults, blank/matching syntax, and question-ID requirements.
- `mdxcanvas/xml_processing/override_parsing.py` — assignment/quiz override attributes and identity.
- `mdxcanvas/xml_processing/tag_preprocessors.py` — exact behavior for `<include>`, `<md-page>`, `<file>`, `<img>`, `<zip>`, `<course-link>`, and `<course-settings>`, including relative-path resolution, `usediv`, line slices, fenced includes, zip precedence, and generated links.
- `mdxcanvas/xml_processing/quarto_slides_preprocessor.py` and `mermaid_preprocessor.py` — inspect only if the role documents those helpers.
- `mdxcanvas/text_processing/jinja_processing.py` — supported args formats and injected Jinja functions (`glob`, `load`, `read_file`, `exists`, `get_arg`, `search`, and others).
- `mdxcanvas/text_processing/markdown_processing.py` and `inline_math.py` — Markdown conversion details when relevant to author-visible behavior.
- `mdxcanvas/resources.py` — resource keys/placeholders and the identity/reference model connecting resources before Canvas IDs exist.
- `mdxcanvas/processing_context.py` and `error_helpers.py` — source-path context and diagnostics worth mentioning in author troubleshooting.

Read deployment modules only when needed to resolve how an authored field maps to Canvas; do not absorb deployment operations into the Content Author role. The most useful targeted files are `mdxcanvas/deploy/assignment.py`, `quiz.py`, `page.py`, `module.py`, `file.py`, `zip.py`, and `checksums.py`.

Do not inspect caches or `mdxcanvas/test.json`. If tests elsewhere in the repository cover a disputed behavior, prefer those focused tests over inference from course examples.

### Resolve documentation/implementation differences explicitly

Do not assume the roster and source are perfectly synchronized. For example, the local roster currently describes some resource IDs as optional/defaulting to titles, while the current processors mark IDs as required for assignments, quizzes, pages, modules, groups, announcements, and quiz questions. Record such mismatches in the role document instead of smoothing them over:

1. describe the safe authoring rule (use explicit, stable IDs);
2. state the current implementation requirement when relevant;
3. avoid teaching legacy title-only examples as recommended syntax;
4. treat course files that only work under older behavior as historical examples.

## CS 110: High-Value Files

Base path: `../../teach/cs110/cs110-course-content/canvas/`

### Read first

- `course.canvas.md.xml.jinja` — top-level resource graph; demonstrates syllabus, `COURSE_SETTINGS`, assignment groups, includes, announcements/exams, Jinja macros, modules, items, external URLs, subheaders, and `content_id` references.
- `content.canvas.md.xml.jinja` — richest end-to-end example of dynamic authoring. It discovers folders, loads MarkdownData, reads global args, conditionally emits resources, generates pages, links and zips assets, creates overrides, and authors assignments/quizzes/questions.
- `global-args.yaml` — shows term-wide dates and values consumed by templates. Use it to explain variable flow and why authors should not scatter term dates through content.
- `course-infos/cci_w26.yaml` — inspect only the `GLOBAL_ARGS`/`COURSE_SETTINGS` shape and section-specific injected content. It shows that some author-visible variables enter through course-instance configuration. Do not make credential or deployment management part of this role.

### Representative content and metadata

- `unit1-intro-to-bit/day1a-intro-to-bit/1a-info.md` — MarkdownData front matter plus table and embedded `<question>` elements; demonstrates a compact record consumed by `load()`.
- `unit1-intro-to-bit/day1a-intro-to-bit/lecture1a/guide/01-introduction-to-bit.md` — representative Markdown page whose H1 becomes a page title.
- `unit1-intro-to-bit/day1a-intro-to-bit/lab1a/instructions.md` — representative included assignment/quiz instructions.
- `unit1-intro-to-bit/day1a-intro-to-bit/homework1a/instructions.md` — representative homework body kept separate from resource metadata.
- `unit1-intro-to-bit/project1/instructions.md` — representative project instructions included in a generated assignment.
- `guide/guide.canvas.md.jinja` — automatic Markdown-page generation, filename-to-ID behavior, and a useful warning that file naming/H1 conventions become deployment behavior.

### Feature-specific examples

- `templates/surveys-and-quizzes/syllabus-quizzes.canvas.md.xml.jinja` — quizzes, reusable includes, announcements, publish dates, and `<course-link>`.
- `templates/surveys-and-quizzes/syllabus-descriptions-and-questions.canvas.md.xml.jinja` — shared quiz body/question source included with `usediv="false"`.
- `templates/announcements/weekly-survey-announcement.xml.canvas.md.jinja` and one adjacent args file — repeated announcements driven by tabular args.
- `final-exam/final.canvas.md.xml.jinja` — assignments and surveys, access codes, included instruction variants, external-tool submissions, and `<zip priority_path=...>` packaging.
- `guide/guide.canvas.md.jinja` and `content.canvas.md.xml.jinja` together — `<md-page>`, `<page>`, `<file>`, `<zip>`, `<quarto-slides>`, `<course-link>`, `glob`, `search`, `exists`, `load`, `read_file`, and `get_arg` in real use.

### What to sample, not exhaustively read

Inspect one complete day bundle and one project/progress-check bundle. The hundreds of sibling day folders repeat the same contract and do not need individual review. Sample source assets only to understand packaging boundaries (`assignment/`, `solutions/`, `for_class/`, guide images, transcripts); the educational code itself is not needed for the role prompt.

### Lessons and cautions

- The template's folder names, info filenames, H1 headings, and regex-derived IDs are contracts; renaming a source file can rename or orphan a Canvas page.
- Existence checks make resources appear or disappear based on directories. Authors must trace generated output, not assume every file deploys.
- `priority_path` allows starter files to replace same-named solution files in a zip; this is important for protecting solutions while packaging assignments.
- Global args and course-info args use similar but not identical naming/casing. Preserve the existing course's conventions rather than normalizing opportunistically.

## CS 312: High-Value Files

Base path: `../../teach/cs312/byu-cs312-content-private/canvas/`

### Read first

- `../AGENTS.md` — mandatory repository instructions.
- `course.canvas.md.xml.jinja` — explicit top-level includes, groups, pages/files, exams, and module graph. It contrasts usefully with CS 110's discovery-heavy approach.
- `global_args.yaml` — the large term schedule consumed by args tables, modules, and resources.
- `course-info/cci_w26.yaml` — inspect only enough to understand `COURSE_SETTINGS` and course-instance `GLOBAL_ARGS` injection.

### Templates and args

Read these as connected pairs:

- `homework/quiz-homework-args.md.jinja` + `homework/quiz-homeworks.canvas.md.xml.jinja` — flat Markdown table args, nested include paths, booleans represented as strings, repeated quizzes, and optional upload questions.
- `homework/written-homework-args.md.jinja` + `homework/written-homeworks.canvas.md.xml.jinja` — repeated assignments whose bodies come from separate Markdown files.
- `general-project-info/project-args.md.jinja` + `general-project-info/projects.canvas.md.xml.jinja` — repeated projects, generated requirement quizzes, `read_file()`, and extracting checklist lines from human-facing instructions. This is a strong example of one source feeding both instructions and a checklist, but also shows how formatting changes can silently break generation.

### Modules, pages, and questions

- `Unit2-Graph/unit-graph-module.canvas.md.xml.jinja` — an explicit conceptual unit with dated subheaders, readings, quizzes, and projects. It shows module items referring to resources generated elsewhere.
- `general-project-info/project-information-module.canvas.md.xml.jinja` — explicit `<md-page>` resources and a module that links selected pages.
- `Unit2-Graph/graph-hw1-quiz-content-dfs.canvas.md.xml.jinja` — representative quiz question source showing `text`, `fill-in-multiple-blanks-filled-answers`, `matching`, `<pair>`, `<distractors>`, Markdown tables, and images.
- `Unit1-RSA/RSA-hw1-quiz-content-big-o.canvas.md.xml.jinja` — sample this for additional multiple-choice/answer syntax rather than reading every quiz bank.
- `Unit0-Setup/syllabus-quiz.canvas.md.xml.jinja` — a self-contained setup quiz and policy-check example.
- `pages/instructor-and-ta-information.md.jinja` — Markdown/Jinja page with local images, nested includes, `<course-link>`, global args, and raw HTML.
- `pages/syllabus.md` and `pages/submitting-feedback-regrading-and-resubmissions.md` — representative stable policy/reference pages.

### Projects and files

- One complete project, preferably `Unit2-Graph/project-scc/`: read `instructions.md`, inspect `assignment/`, and note (without reviewing all contents) `solution/`, `images/`, and report templates. This demonstrates how student instructions, starter code, solutions, images, and deliverable templates relate.
- `general-project-info/project-instructions/general-project-standards.md` — shared content consumed directly and parsed by a generator; useful for explaining dependency-sensitive edits.
- `homework/homework-keys-module.canvas.md.xml.jinja` — instructor-facing answer-key pages and module behavior; use it to discuss audience/sensitivity and ensuring keys are not accidentally exposed.

### Lessons and cautions

- Args files can contain paths relative to the consuming template; authors must reason about the include context.
- Several module items use titles as `content_id`. This works for resources whose IDs equal their titles, but underscores why stable explicit IDs matter before renaming.
- Static `.canvas.md.xml` and templated `.canvas.md.xml.jinja` coexist. Do not assume all deployable resources are Jinja files.
- Not every page created in `project-information-module` is added to its module. Resource existence and Canvas navigation visibility are separate concerns.
- Quiz content, homework wrappers, module placement, and answer keys are separate files; changing an assignment often requires tracing all four.

## CS 301R: High-Value Files

Base path: `../../teach/cs301r-agentic/canvas/`

### Read first

- `course.canvas.md.xml.jinja` — top-level groups, includes, macros, modules, and item/resource relationships. Notice duplicate exam includes as a maintenance hazard, not a recommended pattern.
- `content.canvas.md.xml.jinja` — the core generator. It globs lecture outlines, loads rich MarkdownData sections, derives IDs, reads dates, and conditionally emits lecture assignments, attendance quizzes, interview quizzes, hours quizzes, and homework assignments.
- `global-args.yaml` — lecture/homework schedule and course-wide values.
- `course-info/winter2026.yaml` — inspect only the course-settings/global-args boundary.
- `course-info/_lecture_template.md.jinja` — intended lecture-source shape, but compare it to current real outlines before documenting it because the template is stale/incomplete in places.

### Representative lecture sources

- `unit1-agents/lecture1a-intro-to-completion/lecture-outline.md.jinja` — best full example of the rich source format: title, nested lecture outline, questions, per-question rubric tables, homework assignment, and rubric.
- `unit1-agents/lecture1d-discussion-relationships/lecture-outline.md.jinja` — useful variation with readings, ethics/discussion content, and inconsistent/extra rubric nesting. It demonstrates why authors must inspect loaded structure rather than assuming all sibling files are uniform.
- `unit2-harness/lecture2a-codex-vibecoding/lecture-outline.md.jinja` — sample a lecture with extensive class material and instructor notes, but do not descend into its generated `node_modules`.
- `unit5-final/lecture5a-demo-day-groups/lecture-outline.md.jinja` — sample a lecture that omits optional Quiz/Homework sections, showing conditional resource generation.

### Pages, exams, and helper tags

- `pages/pages.canvas.md.jinja` — globs Markdown pages and derives IDs from stems; a compact example of source naming becoming Canvas identity.
- `pages/homework-report-guidance.md` — shared body included into every generated homework assignment.
- `pages/instructor-and-ta-info.md.jinja` — section-specific page content and image use.
- `unit2.5-midterm/midterm-questions.md.jinja` + `unit2.5-midterm/midterm.md.xml.jinja` — keyed rich question data loaded into an exam; demonstrates nested iteration and generated question IDs.
- `unit5-final/final-exam/final-questions.md.jinja` + `final.md.xml.jinja` — second exam example; inspect to compare IDs and shared question-source behavior.
- `final-project.md.xml.jinja` — explicit assignment plus `<timestamp/>` and `<course-link>`.
- `unit0-intro/course-setup-quiz.canvas.md.xml.jinja` — quiz questions and setup instructions.

### Assets and authoring inputs

Inspect the directory names under one lecture (`class_material/`, `instructor_notes/`, slide deck) and how `content.canvas.md.xml.jinja` uses them:

- `class_material/` is zipped into the Canvas lecture when present;
- top-level `.pptx` files are uploaded and linked;
- `instructor_notes/` are generally author/reference inputs, not automatically deployed by the generator.

This distinction is important: proximity to a lecture file does not imply deployment.

### Lessons and cautions

- Rich MarkdownData can colocate instructional outline, assessment questions, rubrics, and homework, but structural drift is easy. The author must check actual `load()` keys and indentation.
- Optional sections drive whether Canvas resources exist; removing a `# Quiz` or `# Homework` section can invalidate module items that still reference it.
- Globs discover files by path patterns. Moving or renaming a lecture outline changes derived codes/IDs and may cause duplicate/orphaned Canvas resources.
- `course.canvas.md.xml.jinja` currently includes midterm files both in the misc section and again before the module; treat duplicate inclusion as a caution to detect, not copy.
- `course-info/_lecture_template.md.jinja` contains fields not consumed by the current global generator and uses an older question shape. Real consumers are the authority for the repository's current data contract.

## Files and Directories That Are Usually Not Important

Exclude these from role-document research unless a specific included source points to them:

- `node_modules/`, `.git/`, virtual environments, `.pytest_cache/`, `__pycache__/`, `.ipynb_checkpoints/`, `.DS_Store`, IDE metadata, and compiled caches — generated/environment noise.
- Generated Quarto/reveal output such as `*_files/`, bundled JS/CSS/fonts/maps, and rendered slide HTML — deployment artifacts, not useful MDXCanvas authoring examples. Read the source `.qmd` or the `<quarto-slides>` call instead.
- Large binary or generated data stores (`.bin`, `.sqlite3`, generated embedding databases) — class-demo runtime data, not Canvas source conventions.
- Every individual starter-code or solution file — inspect directory boundaries and packaging calls, then read only files needed to understand the student-facing instructions. The Content Author role is not a course-code review role.
- Every image, PDF, transcript, notebook, presentation, CSV, or ZIP — note how representative assets are referenced or uploaded; their substantive content is unnecessary.
- CS 110 `old-content/`, directories named `old-*`, and CS 301R `orphaned-unit3-agents/` — useful only as cautionary evidence that files outside the active include/discovery graph do not deploy. Do not use them as current syntax exemplars.
- CS 301R lecture `scratch/` directories and CS 110/CS 312 idea or draft files — author workspaces, not authoritative deployed resources unless the entry-point graph includes them.
- CS 312 `exams/create-questions/` prompts/scripts and generated exam assets — assessment-development tooling, not MDXCanvas resource syntax.
- CS 110 `canvas/scripts/convert_ipynb_slides_to_qmd.py` — content-production utility, outside the general Content Author role.
- Course-info images and most course-info values — one sample is enough to understand the boundary. API URLs, course IDs, credentials, validation commands, and deployment selection belong to Deployment Engineer guidance.

## Important Distinction: “Not Included” Is Not Always “Unimportant”

A file may be valuable authoring source without being directly deployed (for example instructor notes, a rubric source, a solution directory used to construct a zip, or a question data file loaded by another template). Determine relevance by tracing:

1. direct `<include>`, `<md-page>`, `<file>`, `<img>`, `<zip>`, or `<quarto-slides>` references;
2. Jinja `load()`, `read_file()`, `glob()`, `exists()`, and args-file references;
3. course/module `content_id` references to the generated resource;
4. conditional paths and naming conventions.

Do not equate “present under `canvas/`” with “deployed to Canvas.”

## Synthesis Topics for the Role Document

Use the files above to produce actionable guidance on:

- **Trace before edit:** start at the entry point, find the resource producer, data source, module item, assets, and shared consumers.
- **Identity before title:** explicit stable IDs; safe two-step rename procedure; IDs for resources, questions, groups, modules, and items; consequences for `content_id` and `<course-link>`.
- **Choose the smallest source of truth:** edit included Markdown for prose, args for repeated metadata/dates, question data for generated exams, and templates only for shared structure.
- **Understand include context:** path resolution, `args`, `usediv`, nested includes, and whether files are static, Jinja-rendered, or MarkdownData-loaded.
- **Preserve the resource graph:** a generated resource and its module placement are separate; ensure links/items still resolve after any edit.
- **Handle assets safely:** `<file>`, `<img>`, `<zip>`, `priority_path`, `exclude`, slide upload, filenames, relative paths, and solution leakage risks.
- **Author quizzes deliberately:** question IDs/types, answers, pairs/distractors, blank syntax, scoring, attempts, availability, access codes, surveys, and shared question banks.
- **Keep time/config data centralized:** global args, course-info-injected args, exact date formatting required by MDXCanvas, section overrides, and the danger of hard-coded dates.
- **Treat automation contracts as code:** globs, regex-derived IDs, heading names, table columns, Markdown indentation, and checklist parsing all require validation after prose/file renames.
- **Validate before handoff:** syntactic validity, unique/stable IDs, all includes and paths, all module/link targets, assignment-group references, dates, conditional resources, asset packaging, and absence of accidentally exposed keys/solutions.

## Expected Output

Write the eventual role document to:

- `.agents/scratch/mdxcanvas-content-author-role.md`

It should be instructions to a future Content Author agent, not merely a repository survey. Clearly distinguish:

- authoritative MDXCanvas rules;
- observed repository examples;
- repository-specific conventions;
- known hazards and anti-patterns;
- required author workflow and deployment handoff.
