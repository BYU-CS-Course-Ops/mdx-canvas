# Deployment Engineer Role Research: Onboarding Instructions

## Task

Create a standalone **MDXCanvas Deployment Engineer / Operations** role document.

The role should teach an agent to select the correct Canvas target, validate and diagnose a course, deploy it safely, inspect the result through `canvasapi`, and handle stale or destructive operations. Ground the guidance in the current implementation and the three real course repositories. Do not turn it into a content-authoring reference or assume that the roster's runbook matches this checkout.

The finished role should cover:

- responsibilities and boundaries relative to Course Architect and Content Author;
- target selection, with a strong distinction between test/scratch and live/active courses;
- course-info fields, deployment roots, global args, time zones, entry points, and local prerequisites;
- token handling and protection of secrets;
- parsing/rendering diagnostics and pre-deployment validation;
- what the current `--dry-run` implementation actually does;
- checksum-based change detection, dependency ordering, and update identity;
- default stale cleanup versus full `--cleanup`;
- quiz/submission safeguards and mandatory post-deploy review;
- use of `canvasapi` for read-only observation and debugging;
- deployment reports, failure handling, and operational handoff;
- safeguards for `erasecanvas` and every other destructive action.

Write working files only under `.agents/scratch/`.

## Critical Findings to Preserve

These findings are more important than the nominal roster procedure.

### `--dry-run` is not currently safe

In this checkout, `mdxcanvas/deploy/canvas_deploy.py` passes `dryrun` only to `log_to_deploy()`. That function prints `Dry run - no resources deployed`, but `_deploy_resources()` continues executing all deployers. Stale-resource removal also still runs, and `MD5Sums.__exit__()` uploads the checksum file.

Therefore, the eventual role must **not** describe `--dry-run` as non-mutating. Until the implementation is fixed and tested, run it only against a disposable test course, or do not run it at all. Treat the roster's “dry-run, then live deploy” procedure as unsafe for this version.

### Cleanup occurs without `--cleanup`

`mdxcanvas/deploy/canvas_deploy.py` defines default stale types as `quiz` and `module_item`. A normal deploy removes stale resources of those types. `--cleanup` expands deletion to all tracked stale resource types; it does not merely turn cleanup on. `tests/test_stale_cleanup.py` confirms this is intended current behavior.

An operator must review the complete rendered resource graph before any deploy, especially after changing entry points, includes, conditions, IDs, or target courses.

### The shared testing course is not isolated

These three configurations all target Canvas course ID `20736`:

- `../../teach/cs110/cs110-course-content/canvas/course-infos/cci_beanlab_testing.yaml`
- `../../teach/cs301r-agentic/canvas/course-info/testing-canvas.yaml`
- `../../teach/cs312/byu-cs312-content-private/canvas/course-info/cci_bean_testing.yaml`

Because the checksum ledger lives in Canvas and normal deploys prune stale quizzes/module items, one repository's test deployment can affect another repository's test content. A “testing” label alone is not sufficient evidence of isolation. Prefer a dedicated scratch target such as CS 110's `cci_cs110_ta_scratch.yaml`, or explicitly verify ownership and acceptable collateral deletion.

### Course-info files are target configuration, not token stores

The sampled committed YAML files contain API URL, course ID, time zone, deployment root, and injected global args. The API token comes only from `CANVAS_API_TOKEN`. The roster calls `course_info` credentials and says never to commit it, but these repositories intentionally commit non-secret target configurations. The eventual role should distinguish:

- **secret:** `CANVAS_API_TOKEN`, supplied at runtime and never displayed or committed;
- **sensitive operational target data:** course IDs and settings, which may be committed by project convention but must be reviewed carefully.

### Existing configurations can be stale or incompatible

`mdxcanvas/main.py` requires `DEPLOY_ROOT`, but these sampled files omit it:

- `../../teach/cs301r-agentic/canvas/course-info/winter2026.yaml`
- `../../teach/cs312/byu-cs312-content-private/canvas/course-info/cci_f25.yaml`
- `../../teach/cs312/byu-cs312-content-private/canvas/course-info/cci_f24.json`

Do not infer that every checked-in term config works with the current checkout. Validate required keys and resolve `DEPLOY_ROOT` from the config file's directory before connecting or deploying.

## Working Method

1. Read `.agents/scratch/mdxcanvas-roles.md` and preserve its role boundaries.
2. Load the local roster through `myteam`; do not read `skill.md` files manually.
3. Treat the current Python implementation as authoritative for behavior. Record roster/implementation mismatches explicitly.
4. Inventory all candidate entry points and course-info files. Do not choose a target from a filename alone.
5. For the selected config, report the API host, course ID, resolved deployment root, time zone, course-setting name/code, and whether the target is dedicated, shared test, or live.
6. Use `canvasapi` read-only calls to verify the connected Canvas course's actual ID/name before mutation.
7. Parse and render the full entry point before deployment. Validate references, IDs, dates, paths, generated files, and conditional resources.
8. Compare source resources with the Canvas-backed `_md5sums.json` ledger and understand what would be updated or considered stale. Do not delete based only on filenames or titles.
9. Because current `--dry-run` mutates Canvas, use a disposable/dedicated test course for rehearsal. Never use it as a safety check on a live course.
10. Before a live deploy, present one concise target-and-impact summary and obtain explicit user confirmation. Ask only one question at a time.
11. After deployment, inspect the report and Canvas state. Review quizzes flagged because they already have submissions, links, modules, publication state, dates, assignment groups, and uploaded files.
12. Require separate explicit confirmation for full cleanup. Require stronger typed confirmation for whole-course erasure; never pass `erasecanvas -y` on an agent's own initiative.
13. On failure, stop and preserve diagnostics. Do not immediately rerun against live Canvas until partial changes, checksum state, and stale deletions have been assessed.

## Authoritative Local Resources

Load with `myteam`:

```bash
myteam load .myteam/mdxcanvas-roster/skill.md
myteam load .myteam/mdxcanvas-roster/workflows/deploy/skill.md
myteam load .myteam/mdxcanvas-roster/reference/course-setup/skill.md
```

### Roster deployment workflow

- `.myteam/mdxcanvas-roster/workflows/deploy/skill.md` — useful intended workflow for target discovery, token secrecy, validation, confirmation, cleanup, and erasure.
- `.myteam/mdxcanvas-roster/reference/course-setup/skill.md` — entry-point patterns, config concepts, file extensions, and deployment-root context.

Use these as policy proposals, not behavioral authority. Important mismatches include the unsafe current dry-run, automatic default stale cleanup, and the fact that real repositories commit non-secret course-info YAML.

## Current Deployment Implementation

Base path: `mdxcanvas/deploy/`

### Read first

- `canvas_deploy.py` — central operational source. It defines supported deployers, date conversion, dependency extraction, link resolution, change detection, shell deployment, stale deletion, reporting, dry-run behavior, and cleanup scope.
- `checksums.py` — explains the Canvas-hosted `_md5sums.json` ledger, content/file hashing, Canvas object identity, version metadata, and why target reuse is dangerous.
- `quiz.py` — essential live-course safeguard material. It detects submissions, temporarily unpublishes only when there are no submissions, edits submitted quizzes anyway, and adds such quizzes to manual review.
- `migration.py` — version migrations can make API calls and delete stale quiz questions before ordinary deployment. This must be considered when changing MDXCanvas versions or targeting an older course ledger.
- `algorithms.py` — dependency order and cyclic-link handling through shell assignments/pages/quizzes. Useful for diagnosing surprising two-pass deployments.

### Resource-specific API mapping

Read these to understand exactly which `canvasapi` calls create, retrieve, edit, and delete resources:

- `assignment.py`
- `announcement.py`
- `course_settings.py`
- `file.py`
- `group.py`
- `module.py`
- `override.py`
- `page.py`
- `quiz.py`
- `syllabus.py`
- `zip.py`

Operational lessons include:

- tracked `canvas_id` determines update versus creation;
- uploaded files are uploaded again rather than edited in place;
- file folders are created hidden;
- adding a weighted assignment group enables course-wide assignment-group weighting;
- module publication is preserved on update when `published` is omitted;
- quiz overrides require translating a quiz ID to its assignment ID;
- whole-course settings and syllabus updates directly mutate the course object.

### Generated-resource prerequisites

- `quarto_slides.py` — invokes the external `quarto` executable, captures stdout/stderr, disables cache, and requires output to exist before upload.
- `mermaid.py` — may install Playwright Chromium with system dependencies and then renders in a headless browser. This is a significant first-run/environment side effect.
- `zip.py` — deterministic packaging, permissions, binary handling, and deployment-root path resolution.

These are useful for diagnosing local-tool failures separately from Canvas API failures.

## Essential Adjacent Sources Discovered

The requested `mdxcanvas/deploy/` directory does not contain the complete operational interface. A later synthesis agent should also read:

- `mdxcanvas/main.py` — actual CLI flags, required config keys, environment-token lookup, config-relative `DEPLOY_ROOT`, connection logging, parse/render/deploy flow, and exception handling.
- `mdxcanvas/deployment_report.py` — JSON/report fields for deployed content, manual review, and errors.
- `mdxcanvas/erasecanvas/main.py` — actual whole-course deletion behavior and confirmation. It deletes syllabus, quizzes, assignments, groups, pages, modules, files/folders, and announcements in parallel.
- `tests/test_stale_cleanup.py` — executable evidence for default versus full stale cleanup.

For parser/render diagnostics, also inspect the processing files identified in `.agents/scratch/content-author-onboarding.md`; deployment code only receives the already-built resource graph.

## Reference Course Targets and Entry Points

### CS 110

Base path: `../../teach/cs110/cs110-course-content/canvas/`

High-value files:

- `course.canvas.md.xml.jinja` — live resource graph and deployment entry point.
- `global-args.yaml` — term schedule consumed separately with `--global-args`.
- `course-infos/cci_beanlab_testing.yaml` — shared test target (`20736`).
- `course-infos/cci_cs110_ta_scratch.yaml` — dedicated-looking TA scratch target; preferable evidence for isolated rehearsal, subject to live verification.
- `course-infos/cci_w26.yaml`, `cci_sp26.yaml`, and `cci_su26.yaml` — multiple active/term targets; useful for target-selection safeguards and term-specific injected settings.
- `content.canvas.md.xml.jinja` — operationally important because discovery and existence checks can change the deployed graph and trigger stale cleanup.
- `final-exam/final.canvas.md.xml.jinja` and `final-exam/practice-final.canvas.md.xml.jinja` — sensitive, high-impact resources and generated zip deployment.

The course demonstrates why an operator must pair the correct term config with the correct `global-args.yaml`, inspect generated resources rather than just changed files, and treat final/exam deployment as higher risk.

### CS 301R

Base path: `../../teach/cs301r-agentic/canvas/`

High-value files:

- `course.canvas.md.xml.jinja` — entry point; duplicate midterm includes are a concrete graph-validation hazard.
- `content.canvas.md.xml.jinja` — glob- and condition-driven resource generation; omitted lecture sections can make quizzes/assignments stale.
- `global-args.yaml` — schedule and term variables.
- `course-info/testing-canvas.yaml` — shared test target (`20736`).
- `course-info/kevin-testing-canvas.yaml` — separate named testing target.
- `course-info/winter2026.yaml` — live/term target, but currently lacks the `DEPLOY_ROOT` required by `mdxcanvas/main.py`.
- `unit2.5-midterm/midterm.md.xml.jinja` and `unit5-final/final-exam/final.md.xml.jinja` — sensitive quiz updates where submissions and manual Canvas review matter.

The `orphaned-unit3-agents/` tree is useful only as evidence that filesystem presence does not imply deployment. Do not index `node_modules`, generated slides, or lecture demo data.

### CS 312

Base path: `../../teach/cs312/byu-cs312-content-private/canvas/`

High-value files:

- `course.canvas.md.xml.jinja` — explicit entry point and module graph.
- `global_args.yaml` — large term schedule; date failures can have broad impact.
- `course-info/cci_bean_testing.yaml` — shared test target (`20736`).
- `course-info/cci_f24_testing.yaml` — another historical test target.
- `course-info/cci_w26.yaml` — live/term target.
- `course-info/cci_f25.yaml` and `cci_f24.json` — examples of legacy configs missing current required fields.
- `homework/homework-keys-module.canvas.md.xml.jinja` — sensitive answer-key content; post-deploy visibility must be checked.
- `general-project-info/projects.canvas.md.xml.jinja` — many generated assignments/quizzes and packaged files from one template.
- `Unit0-Setup/syllabus-quiz.canvas.md.xml.jinja` and representative homework quiz templates — useful submitted-quiz review cases.

The project `build_*.sh` scripts and solution code are generally not MDXCanvas deployment runbooks. Inspect only when diagnosing zip generation or accidental solution exposure.

## `canvasapi` Observation Guidance to Develop

The role should recommend read-only observation before and after mutation. Derive calls from the deploy modules rather than inventing wrappers. At minimum, document how to:

- connect using `Canvas(api_url, token).get_course(course_id)` and verify `course.id` and `course.name`;
- enumerate/get assignments, quizzes and submissions, pages, modules/items, assignment groups, files/folders, announcements, and overrides;
- compare Canvas IDs stored in `_md5sums.json` with the objects found in the selected course;
- inspect publication state, dates, group placement, module ordering, URLs, and quiz submission presence;
- handle `ResourceDoesNotExist` as a possible stale-ledger or partial-deployment symptom.

Observation should default to GET/list operations. Do not call `.edit()`, `.update()`, `.delete()`, `create_*()`, or upload methods during diagnosis unless the user has explicitly authorized repair.

## Validation and Review Topics

The eventual role should turn these into a concise operational checklist:

- exact API host, course ID, Canvas course name/code, and environment class;
- dedicated versus shared test target;
- required course-info keys and resolved `DEPLOY_ROOT`;
- token present without printing it;
- entry point and global args chosen explicitly;
- complete render/parse success with source-context diagnostics;
- unique stable IDs and resolvable dependencies/module items/course links;
- valid local paths and external prerequisites for Quarto/Mermaid;
- date parsing under the configured local time zone;
- expected changed resources and expected stale quizzes/module items;
- whether a version migration will run;
- whether quizzes have submissions and require browser review/save;
- whether sensitive exams, keys, solutions, or files become visible;
- deployment report saved and inspected;
- post-deploy Canvas verification completed.

## Files and Directories Usually Not Useful

Exclude unless a specific deployment failure points to them:

- `__pycache__/`, `.pytest_cache/`, `.DS_Store`, `.ipynb_checkpoints/`, virtual environments, and IDE files;
- CS 301R `node_modules/`, generated slide bundles, transcripts, and class-demo datasets;
- CS 110 `old-content/` and generated Reveal/Quarto support trees;
- CS 312 project solutions, analysis notebooks, generated data, and assessment-generation scripts;
- Docker build scripts for student assignments, except when validating a zip/package boundary;
- images and PDFs whose only significance is that an entry point uploads them.

## Expected Output

Write the eventual role document to:

- `.agents/scratch/mdxcanvas-deployment-engineer-role.md`

It should be instructions to a future deployment agent, not merely a repository survey. Clearly distinguish:

- intended roster policy;
- current implementation behavior;
- observed repository conventions;
- test versus live target evidence;
- non-mutating observation versus mutation;
- normal deployment, default stale cleanup, full cleanup, and whole-course erase;
- conditions that require stopping and asking the user one question at a time.
