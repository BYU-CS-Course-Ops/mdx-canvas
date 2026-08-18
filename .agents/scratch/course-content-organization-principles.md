# Principles for Organizing Course Content

## Goal

A course repository should make the common work obvious and the unusual work possible.

Good organization helps an instructor answer these questions quickly:

- Where does this content belong?
- What else must change when I modify it?
- Which file is the authoritative source?
- What will students see, and in what order?
- Is this content reusable, term-specific, private, archived, or still proposed?

The best structure is not the most abstract or automated structure. It is the simplest structure that accurately represents how the course is taught.

## Core Principle: Organize by Instructional Ownership

Content that changes together should live together.

A lesson's outline, demonstrations, homework, rubric, images, and downloadable files usually form one instructional bundle. When the topic changes, several of these artifacts may change with it. Keeping them together makes that relationship visible and reduces the number of places an instructor must search.

For example:

```text
unit2-graphs/
├── lesson2a-depth-first-search/
│   ├── lesson-info.md
│   ├── lecture-outline.md
│   ├── homework.canvas.md.xml
│   ├── homework-key.md
│   ├── class-material/
│   └── images/
├── lesson2b-directed-graphs/
└── project-scc/
```

This principle is more important than whether the bundle is called a day, lesson, lecture, topic, or week.

Do not organize primarily by file format or Canvas resource type when doing so separates related instructional material. A top-level `quizzes/` directory may look tidy, but it can make one lesson span `lectures/`, `quizzes/`, `homework/`, `images/`, and a module file.

## Match the Hierarchy to the Course's Rhythm

Use the course's smallest meaningful recurring instructional unit.

### Day bundles

Use a day bundle when most class meetings have a predictable set of activities, such as:

```text
unit → day → lecture + lab + homework
```

This works well for a course like CS 110, where the teaching cadence is highly regular.

### Lesson or lecture bundles

Use a lesson bundle when the lecture topic is the main unit of authorship and related work varies by meeting:

```text
unit → lesson → outline + materials + optional quiz/homework
```

This works well for seminars, special-topics courses, and courses like CS 301R.

### Topic units

Use a topic unit when several meetings, readings, assignments, and projects collectively develop one concept:

```text
unit → lessons + homework + project
```

This fits a course like CS 312, provided each lesson still has a clear local home.

### Week bundles

Use weeks only when students and instructors genuinely think in weeks. Do not impose weeks merely because Canvas courses often use weekly modules.

The names should communicate meaning to course maintainers. Consistency matters more than choosing one universal vocabulary.

## Use a Shallow, Predictable Shape

Prefer a small number of meaningful levels:

```text
course → unit → lesson or major assessment
```

Add subdirectories only when they clarify ownership, such as:

- `assignment/` for distributed starter files;
- `solution/` for instructor or selectively published solutions;
- `images/` for locally owned media;
- `class-material/` for demonstrations and in-class files;
- `instructor-notes/` for material not intended for students.

Avoid deep trees that encode every possible distinction. A directory hierarchy is useful when a person can predict a path without consulting documentation.

## Give Every Fact One Authoritative Home

A course becomes difficult to maintain when the same fact appears in several places.

Common sources of duplication include:

- titles;
- stable IDs;
- lecture dates;
- due dates;
- readings;
- point values;
- assignment-group names;
- module order;
- policy language;
- links to shared services.

Choose one authoritative source for each fact and derive other representations from it when practical.

A small lesson metadata file can be useful:

```yaml
id: graph-dfs
code: 2a
title: Depth-First Search
lecture_date: Feb 3
reading: Chapter 3.1–3.3
homework:
  id: graph-homework-dfs
  due: Feb 5
```

The goal is not to move all content into metadata. Metadata should contain concise facts used in multiple places. Explanations, instructions, questions, and rubrics are usually more readable as Markdown or MDXCanvas content.

## Separate Curriculum from Course Offering

Stable curriculum and term-specific operations change for different reasons and should not be interwoven unnecessarily.

### Stable curriculum

Usually includes:

- learning outcomes;
- topic sequence;
- explanations and readings;
- assignment intent and instructions;
- quiz questions;
- rubrics;
- starter code and datasets;
- project structure;
- stable resource IDs.

### Offering-specific data

Usually includes:

- term and year;
- meeting and due dates;
- Canvas course ID;
- section IDs;
- instructors and TAs;
- room and office-hour information;
- Discord, survey, and temporary external links;
- exam windows;
- section-specific overrides.

Keep offering data in a small number of configuration files. This makes term rollover safer and reveals accidental hard-coded dates.

Not every operational detail belongs in one global file. If a date is meaningful only to one lesson, it can remain in that lesson's term metadata. The important point is to avoid two competing sources of truth.

## Prefer Explicit Content; Generate Repeated Structure

Automation is most useful for predictable scaffolding, not for concealing instructional decisions.

Good candidates for templates or macros include:

- repeated module item groups;
- lecture/attendance/homework resources that consistently share a schema;
- standard assignment wrappers around unique instructions;
- resource catalogs with many genuinely uniform entries;
- repeated date and availability formatting.

Keep content explicit when it is:

- unique;
- pedagogically significant;
- easier to read in its final form;
- full of exceptions;
- likely to evolve independently.

A useful decision rule is:

> If instructors can describe the repeated contract in one short sentence, a template may help. If the description requires a list of exceptions, keep the resources explicit.

Templates should reduce editing locations, not merely reduce line count.

## Make the Normal Case Easy and Exceptions Obvious

Courses contain genuine irregularities:

- guest lectures;
- discussion days;
- reviews;
- holidays;
- project workshops;
- exams;
- asynchronous lessons;
- optional enrichment;
- section-specific activities;
- lessons without homework;
- projects spanning several units.

Do not force these into an ordinary lesson shape by creating empty or fake resources. A repeated bundle should allow optional components, while exceptional resources can be written explicitly.

A healthy architecture might generate ordinary lessons while placing special module items directly in a unit module:

```text
unit3-production/
├── lesson3a-hallucination/
├── lesson3b-rag/
├── guest-lecture/
├── project-workshop/
└── module.canvas.md.xml.jinja
```

Exceptions should be visible where the sequence is defined. They should not be hidden inside increasingly elaborate global template conditions.

## Keep Shared Content Shared—But Only When It Is Truly Shared

Course-wide directories are appropriate for resources owned by the entire course:

```text
shared/
├── pages/
│   ├── syllabus.md
│   ├── getting-help.md
│   └── accommodations.md
├── project-standards/
├── setup/
└── policies/
```

Content belongs locally when one lesson, unit, or project owns it. It belongs in `shared/` when several independent resources intentionally use the same canonical artifact.

Do not centralize content merely because files have the same extension. Do not duplicate shared content merely to make every bundle self-contained.

## Treat Projects and Major Assessments as First-Class Bundles

Projects, exams, and progress checks often span multiple lessons and should not be squeezed into a single lesson folder.

A project bundle can contain:

```text
project-scc/
├── project-info.md
├── instructions.md
├── rubric.md
├── assignment/
├── solution/
├── tests/
├── analysis/
└── images/
```

Shared project standards can remain course-wide, while project-specific requirements stay in the project bundle.

The architecture should also distinguish public student materials from private solutions, answer keys, and exam content. Repository location and deployment behavior should reflect those boundaries deliberately.

## Design Canvas Modules as a Student Path

The source tree serves maintainers; Canvas modules serve students. They should correspond, but they do not need to be identical.

A module should communicate a meaningful sequence:

1. orient to the topic;
2. prepare or read;
3. attend or study the lesson;
4. practice;
5. demonstrate learning;
6. review feedback or integrate the skill.

Include readings, subheaders, external resources, and ungraded pages when they help students understand what to do next. Do not let modules become an unordered mirror of graded assignments.

Module ordering should be easy to inspect. If it is generated, the source data should make the final order obvious without mentally executing a complex template.

## Use Stable IDs and Human-Readable Names

A resource has at least two identities:

- a stable machine identity used by module references and course links;
- a student-facing title that may improve over time.

Define IDs deliberately and do not derive long-term identity solely from mutable titles.

Good IDs are:

- stable;
- unique within the course;
- predictable;
- concise enough to use in references;
- independent of dates and term names.

For example:

```text
lesson: graph-dfs
homework: graph-dfs-homework
project: graph-scc-project
module: unit-graphs
```

Folder codes such as `2a` can communicate sequence, but topic words make paths resilient and searchable. Combining them often works well: `lesson2a-depth-first-search/`.

## Keep Active, Proposed, and Retired Content Distinct

A maintainer should be able to tell whether content is:

- currently deployed;
- planned but not adopted;
- an optional candidate;
- retained for historical reference;
- retired and safe to ignore;
- orphaned accidentally.

Use explicit locations and status documents, such as:

```text
docs/
├── plans/
├── decisions/
└── backlog/
archive/
```

Do not leave old folders interspersed with active units using names such as `_old`, `old2`, or `orphaned` indefinitely. Archive content with enough context to explain why it was retired, or delete it when history is already preserved in version control.

Proposals and meeting ideas should not silently become deployed curriculum. Record the transition from suggestion to decision to implementation.

## Optimize for Common Maintenance Tasks

Evaluate a proposed organization by walking through realistic changes:

- Move a lesson to another unit.
- Rename a lesson title without changing its identity.
- Change one homework deadline.
- Add a second section with a different schedule.
- Replace a reading.
- Add a project milestone.
- Remove homework from one discussion day.
- revise a rubric and its autograder;
- roll the course into a new term;
- locate every student-facing artifact for one lesson;
- archive a retired project.

A good architecture makes each task local and unsurprising. If a routine change requires searching unrelated global tables and templates, the design has split ownership incorrectly.

## A Practical Default Structure

The following is a useful starting point, not a mandatory scaffold:

```text
canvas/
├── course.canvas.md.xml.jinja
├── content.canvas.md.xml.jinja
├── global-args.yaml
├── course-info/
├── shared/
│   ├── pages/
│   ├── setup/
│   └── standards/
├── unit0-setup/
├── unit1-topic/
│   ├── unit-info.md
│   ├── lesson1a-topic/
│   │   ├── lesson-info.md
│   │   ├── lecture-outline.md
│   │   ├── class-material/
│   │   ├── images/
│   │   └── homework.canvas.md.xml
│   ├── lesson1b-topic/
│   ├── project-topic/
│   └── module.canvas.md.xml.jinja
├── unit2-topic/
├── exams/
└── final/
```

Adapt it according to the course:

- Add `lab/` when labs are a recurring owned component.
- Add `guide/` when each lesson has durable reference pages.
- Keep quizzes in lesson metadata or local files depending on their complexity.
- Place projects at the unit level when they integrate several lessons.
- Use a course-wide assessment catalog only when the assessments genuinely share one stable schema.
- Keep unusual modules or resources explicit.

## Decision Heuristics

When deciding where or how to represent content, ask in this order:

1. **Who owns it?** Course, unit, lesson, project, or offering?
2. **What changes with it?** Co-locate those artifacts.
3. **Is it part of a real recurring rhythm?** If yes, use the corresponding bundle.
4. **Is the repetition structurally stable?** If yes, consider a template.
5. **Is it reused by independent owners?** If yes, centralize the canonical copy.
6. **Is it an exception?** Represent it explicitly rather than distorting the normal model.
7. **Is it curriculum or offering data?** Put it in the appropriate source of truth.
8. **Can a maintainer predict where to find it?** If not, simplify.

## Signs the Organization Is Too Complex

Simplify when:

- a small content edit requires touching many unrelated files;
- maintainers routinely search the entire repository to find ownership;
- templates contain many course-specific branches;
- directory names encode implementation details rather than instructional meaning;
- the final student order is difficult to infer from source;
- the same title, date, or ID is repeated manually;
- special cases require fake resources;
- args tables contain long prose that is difficult to edit;
- shared directories have become dumping grounds;
- archives and active content are mixed;
- only the original author understands the generation process.

## Signs the Organization Is Too Loose

Add structure when:

- equivalent lessons use unrelated names and shapes;
- assets and solutions have no obvious owner;
- dates and section data are hard-coded throughout content;
- module references depend on mutable titles;
- repeated resource wrappers drift from one another;
- policies, rubrics, instructions, and grading automation disagree;
- term rollover relies on memory rather than a finite checklist.

## Final Standard

A well-organized course does not eliminate idiosyncrasies. It gives them clear, intuitive places to live.

The desired balance is:

- **locality** for related content;
- **consistency** for the common instructional rhythm;
- **explicitness** for exceptional resources;
- **one source of truth** for shared facts;
- **separation** between curriculum and course offerings;
- **modest automation** for stable repetition;
- **clear ownership** for shared, private, proposed, and archived material.

If an instructor can understand the structure, predict where content belongs, and make ordinary changes without tracing a web of templates and tables, the architecture is doing its job.
