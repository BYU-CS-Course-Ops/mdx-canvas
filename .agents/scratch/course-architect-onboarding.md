# Course Architect Role Research: Onboarding Instructions

## Task

Create or revise a standalone **MDXCanvas Course Architect** role document.

The role should explain how an agent helps an instructor organize a new course before detailed authoring or deployment. Ground the guidance in actual course repositories rather than generic instructional-design advice.

The finished role should cover:

- the purpose, responsibilities, and boundaries of the Course Architect;
- principles for selecting a course hierarchy such as units, weeks, days, lectures, activities, and projects;
- how learning outcomes, activities, assessments, feedback, workload, and Canvas navigation should align;
- entry-point, folder, resource-ID, asset, configuration, and archive conventions;
- when to use static content, templates, macros, metadata files, or tabular args;
- how stable curriculum should be separated from term-, section-, and deployment-specific information;
- how the agent should collaborate with the instructor;
- what questions it should ask, one at a time;
- what information and source materials it should gather;
- what plans and handoff artifacts it should produce;
- examples and cautionary lessons found in the reference courses.

Write working files only under `.agents/scratch/`.

## Working Method

1. Read the existing role descriptions to establish scope and avoid absorbing Content Author or Deployment Engineer responsibilities.
2. Inspect the three reference repositories at both the structural and content levels.
3. Identify each course's actual instructional rhythm before judging its source layout:
   - CS 110: repeated unit/day/lecture/lab/homework bundles;
   - CS 312: conceptual units with readings, homework catalogs, and substantial projects;
   - CS 301R: lecture bundles that combine outlines, questions, rubrics, homework, demonstrations, and instructor notes.
4. Trace each course from its main entry point through includes, templates, metadata/args, modules, and representative resources.
5. Compare stable course content with global args and Canvas course-instance configuration.
6. Review planning documents and meeting notes to understand how curriculum decisions, student feedback, policy, staffing, and unresolved work affect architecture.
7. Record both good patterns and maintenance hazards. Look especially for:
   - hard-coded dates mixed with global dates;
   - duplicate includes;
   - inconsistent naming or casing;
   - resources omitted from modules;
   - old or orphaned content without clear lifecycle rules;
   - global assets that should be local, or duplicated local assets;
   - policy, instructions, rubric, and automation drift;
   - abstractions with too many exceptions.
8. Synthesize principles rather than copying one repository's structure as a universal template.
9. Advise the agent to ask the instructor one question at a time, explain why it matters, offer reasonable options, and recommend one.
10. Keep the role architecture-focused. It may specify implementation contracts, but bulk content writing and deployment belong to other roles.
11. Before finishing, check that the document includes concrete reference paths, an intake process, information-gathering guidance, expected deliverables, and a review checklist.

## Required Project Files

Read these first:

- `.agents/scratch/mdxcanvas-roles.md`
- `.agents/scratch/mdxcanvas-course-architect-role.md` if revising the existing draft

## MDXCanvas Team Guidance

The reference repositories contain an MDXCanvas `myteam` resource. Use `myteam` rather than reading skill files manually.

From a reference repository with a working environment, load:

```bash
cd ../../teach/cs312/byu-cs312-content-private
venv/bin/python -m myteam get skill mdxcanvas
venv/bin/python -m myteam get skill mdxcanvas/workflows
venv/bin/python -m myteam get skill mdxcanvas/workflows/new-course
```

Use this material to understand existing MDXCanvas workflow expectations, but evaluate generic scaffold recommendations against the richer patterns in the three real courses.

## CS 110 Files

### Structure and entry points

- `../../teach/cs110/cs110-course-content/Readme.md`
- `../../teach/cs110/cs110-course-content/unit-preparation.md`
- `../../teach/cs110/cs110-course-content/canvas/course.canvas.md.xml.jinja`
- `../../teach/cs110/cs110-course-content/canvas/content.canvas.md.xml.jinja`
- `../../teach/cs110/cs110-course-content/canvas/global-args.yaml`
- `../../teach/cs110/cs110-course-content/canvas/course-infos/cci_w26.yaml`

### Representative metadata and shared-page conventions

- `../../teach/cs110/cs110-course-content/canvas/unit1-intro-to-bit/day1a-intro-to-bit/1a-info.md`
- `../../teach/cs110/cs110-course-content/canvas/guide/guide.canvas.md.jinja`

### Planning and operational feedback

- `../../teach/cs110/cs110-course-content/meetings/2026-06-04-1600.md`

Also inspect the directory tree under:

- `../../teach/cs110/cs110-course-content/canvas/unit0-introduction/`
- `../../teach/cs110/cs110-course-content/canvas/unit1-intro-to-bit/`
- `../../teach/cs110/cs110-course-content/canvas/templates/`
- `../../teach/cs110/cs110-course-content/canvas/final-exam/`

Focus on the ownership and repetition of day metadata, lecture guides/files, labs, homework, projects, progress checks, setup material, and finals.

## CS 312 Files

### Repository instructions and entry points

- `../../teach/cs312/byu-cs312-content-private/AGENTS.md`
- `../../teach/cs312/byu-cs312-content-private/canvas/course.canvas.md.xml.jinja`
- `../../teach/cs312/byu-cs312-content-private/canvas/global_args.yaml`
- `../../teach/cs312/byu-cs312-content-private/canvas/course-info/cci_w26.yaml`

Follow the repository's `AGENTS.md` instructions, including its `myteam` requirements.

### Representative unit and catalogs

- `../../teach/cs312/byu-cs312-content-private/canvas/Unit2-Graph/unit-graph-module.canvas.md.xml.jinja`
- `../../teach/cs312/byu-cs312-content-private/canvas/homework/quiz-homework-args.md.jinja`
- `../../teach/cs312/byu-cs312-content-private/canvas/homework/written-homework-args.md.jinja`
- `../../teach/cs312/byu-cs312-content-private/canvas/general-project-info/project-args.md.jinja`
- `../../teach/cs312/byu-cs312-content-private/canvas/general-project-info/projects.canvas.md.xml.jinja`
- `../../teach/cs312/byu-cs312-content-private/canvas/general-project-info/project-information-module.canvas.md.xml.jinja`

Also inspect the directory tree under:

- `../../teach/cs312/byu-cs312-content-private/canvas/Unit1-RSA/`
- `../../teach/cs312/byu-cs312-content-private/canvas/Unit2-Graph/`
- `../../teach/cs312/byu-cs312-content-private/canvas/general-project-info/`
- `../../teach/cs312/byu-cs312-content-private/canvas/homework/`
- `../../teach/cs312/byu-cs312-content-private/canvas/exams/`

Focus on conceptual sequencing, readings and subheaders, cross-unit resource catalogs, project-local starter/solution/analysis material, shared project standards, exams, keys, and archival content.

## CS 301R Files

### Entry points and term configuration

- `../../teach/cs301r-agentic/canvas/course.canvas.md.xml.jinja`
- `../../teach/cs301r-agentic/canvas/content.canvas.md.xml.jinja`
- `../../teach/cs301r-agentic/canvas/global-args.yaml`
- `../../teach/cs301r-agentic/canvas/course-info/winter2026.yaml`
- `../../teach/cs301r-agentic/canvas/course-info/_lecture_template.md.jinja`
- `../../teach/cs301r-agentic/canvas/pages/pages.canvas.md.jinja`

### Representative lecture bundle

- `../../teach/cs301r-agentic/canvas/unit1-agents/lecture1a-intro-to-completion/lecture-outline.md.jinja`

Inspect sibling lecture directories to see optional homework, discussion meetings, class materials, slides, and instructor notes.

### Curriculum planning and decisions

- `../../teach/cs301r-agentic/docs/fall2026-plan.md`
- `../../teach/cs301r-agentic/docs/backlog/course-outline-revision-for-fall.md`
- `../../teach/cs301r-agentic/docs/backlog/lecture-outline-rubric-support.md`
- `../../teach/cs301r-agentic/docs/backlog/homework-requirements-and-report-expectations.md`
- `../../teach/cs301r-agentic/docs/backlog/ai-policy-for-reports-and-final-projects.md`
- `../../teach/cs301r-agentic/docs/meetings/2026-04-22-1300-cs301r-staff-meeting.md`

Also inspect the directory tree under:

- `../../teach/cs301r-agentic/canvas/unit1-agents/`
- `../../teach/cs301r-agentic/canvas/unit2-harness/`
- `../../teach/cs301r-agentic/canvas/unit3-production-ready/`
- `../../teach/cs301r-agentic/canvas/orphaned-unit3-agents/`
- `../../teach/cs301r-agentic/docs/backlog/`

Focus on lecture-as-source patterns, questions and rubrics embedded near instruction, optional lecture components, rapidly changing curriculum, meeting decisions, policy timing, and explicit backlog scope.

## Useful Inspection Commands

Use directory listings to understand organization without indexing generated environments or repository internals:

```bash
find <repo>/canvas -maxdepth 3 -type d | sort
find <repo>/canvas -maxdepth 3 -type f | sort
```

Exclude noise such as:

- `.git/`
- virtual environments;
- `node_modules/`;
- generated Quarto or slide output;
- caches;
- IDE metadata.

Use targeted reads for entry points and representative resources rather than attempting to read every assignment or generated asset.

## Expected Output

Write the role document to:

- `.agents/scratch/mdxcanvas-course-architect-role.md`

The document should be useful as instructions to a future agent, not merely as a report describing the repositories. It should clearly distinguish:

- observed examples;
- recommended principles;
- required agent behavior;
- questions and information gathering;
- review and handoff criteria.
