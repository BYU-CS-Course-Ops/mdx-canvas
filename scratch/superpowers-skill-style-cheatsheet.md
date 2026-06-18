# Superpowers Skill and Agent Writing Cheat Sheet

This document distills the recurring tone, grammar, and style conventions used in `obra/superpowers`, with emphasis on how the skills and agents *sound* and how their instructions *flow*.

## What the writing is optimizing for

The writing is built for execution, not explanation.

- It tells the model what to do in a strict sequence.
- It reduces ambiguity by naming rules, gates, and stop conditions.
- It prefers short imperative instructions over discussion.
- It treats quality as a process problem: follow the workflow, then verify.
- It assumes the reader is capable and busy, so wording stays direct and compact.

## Tone

### 1. Crisp, operational, and unsentimental

The dominant voice is that of a pragmatic senior operator:

- direct
- procedural
- low-fluff
- high-accountability
- mildly strict without sounding hostile

The prose rarely sounds conversational. It sounds like a field manual.

### 2. Calm authority

Instructions are written as settled practice, not suggestions:

- "Do this first."
- "Never skip this."
- "If X happens, stop and do Y."

The tone does not debate. It establishes defaults and constraints.

### 3. Discipline over encouragement

These files do not spend words motivating the reader. They assume compliance.

Use:

- clear rules
- concrete checks
- strong defaults
- explicit failure cases

Avoid:

- hype
- pep-talk phrasing
- vague "best practice" language
- soft hedging unless uncertainty is real

## Grammar and sentence style

### 1. Imperative verbs lead

Most lines begin with an action:

- Review
- Check
- Verify
- Stop
- Read
- Create
- Run
- Delegate

This gives the writing forward motion.

### 2. Short sentences win

The repo favors compact statements over long explanatory paragraphs.

Good pattern:

```md
Read the relevant files first.
Do not make assumptions from filenames alone.
Stop and gather evidence before proposing a fix.
```

Less common pattern:

```md
You should probably begin by looking through the relevant files so you can understand what is happening before trying to suggest changes.
```

### 3. Conditional branching is explicit

The skills often encode decision points in simple if/then language:

- If there are no tests, create a minimal one first.
- If the issue is unclear, reproduce it before editing.
- If the task needs deep investigation, hand it off.

This is one of the repo's strongest habits. It keeps workflows resilient.

### 4. Modal verbs are used sparingly

The writing prefers "do" over "should."

Use:

- "Run the tests."
- "Stop after reproducing the failure."
- "Delegate to the code-reviewer agent."

Use `should` only when a rule is a strong recommendation rather than a hard requirement.

### 5. Naming rules give structure

The repo often labels important concepts so they can be reused:

- named rules
- named phases
- named anti-patterns
- named handoff targets

This makes the guidance easier to scan and remember.

## Structural conventions

### 1. Frontmatter is minimal and functional

Skills commonly begin with compact metadata blocks:

- name
- description

That header is not decorative. It exists to make routing and selection easy.

### 2. Headings map to workflow

Headings usually track the working sequence, not a documentation taxonomy.

Typical pattern:

1. What this skill is for
2. Rules or non-negotiables
3. Step-by-step workflow
4. Branch conditions
5. When to delegate
6. Expected output

This is a key takeaway: structure around action order, not topic categories.

### 3. Lists do most of the work

Bullets and numbered steps carry the document. Paragraphs are short and transitional.

Use bullets for:

- constraints
- checks
- failure conditions
- handoff criteria
- output requirements

### 4. "Iron law" style rules are common

The repo likes memorable, non-negotiable rules with strong framing.

Examples of the pattern, not copied wording:

- one rule that must never be skipped
- one principle that overrides convenience
- one failure mode that invalidates the rest of the work

This is useful because it creates hierarchy inside the instructions.

## Flow conventions in skills

Skills usually move like this:

1. Define scope.
2. State the hard rule.
3. Require context gathering before action.
4. Execute the core method in ordered steps.
5. Add branch logic for edge cases.
6. Define what "done" looks like.
7. Delegate when the task crosses a boundary.

This gives the skill a procedural spine.

### Common skill-writing moves

- Start narrow. State exactly when the skill applies.
- Put the main constraint near the top.
- Break the work into phases.
- Include stop points so the model does not rush ahead.
- Tell the model what evidence to collect.
- Specify output shape, not just task intent.
- Include escalation rules when another agent or skill is better suited.

## Flow conventions in agents

Agents in the repo tend to behave like role-specific specialists.

Their prompts usually:

1. Define the role in one sentence.
2. State the specialty and what matters most.
3. Give a workflow for operating in that role.
4. Require a specific output format.
5. Constrain tone and scope.

### Agent voice pattern

Compared with skills, agents are often:

- slightly more persona-driven
- still strict
- focused on viewpoint and evaluation criteria

For example, a reviewer agent is not just told to review code. It is told *what kind of reviewer it is*, *what to prioritize*, and *how to present findings*.

## Style conventions worth copying

### Use hard-edged defaults

Write defaults as rules:

- "Assume X unless evidence shows otherwise."
- "Do not proceed until Y is true."
- "Prefer A over B."

This reduces drift.

### Make verification part of the instruction

Do not end at "make the change." End at:

- verify
- test
- inspect output
- confirm the result matches the requested shape

### Tell the model when to stop

Good skills prevent overreach:

- stop after collecting evidence if the diagnosis is still weak
- stop and delegate if the task changes category
- stop and report blockers instead of improvising past them

### Prefer specific nouns over abstract advice

Weak:

- "Use good judgment."

Stronger:

- "Check the failing test, the touched files, and the call site before editing."

## Things these files usually avoid

- long theory sections
- motivational writing
- excessive caveats
- broad philosophical framing
- large examples unless needed for execution
- bloated prose between steps

The pattern is: brief context, then operational guidance.

## Reusable writing template

Use this when drafting a new skill or agent in a similar style.

```md
---
name: short-hyphenated-name
description: One-sentence explanation of when this is useful and what it helps do.
---

# Purpose

Use this when [clear trigger condition].

## Non-Negotiables

- Do not [common failure mode].
- Always [required verification or evidence-gathering step].
- Stop if [boundary condition].

## Workflow

1. Gather the minimum context required to act.
2. Identify the relevant files, inputs, or constraints.
3. Execute the core task in a strict order.
4. Verify the result with the most relevant check.
5. Report outcome, open risks, and next action if needed.

## Branches

- If [condition], then [alternate path].
- If [condition], stop and [handoff or escalation].

## Output

- Include [required artifact or summary].
- Call out [risks, missing evidence, or unresolved questions].
```

## Cheat sheet: how to make your writing sound closer to Superpowers

- Lead with verbs.
- Keep paragraphs short.
- Put rules above nuance.
- Give the model a sequence, not a topic dump.
- Name important rules so they feel stable and reusable.
- Write branch logic for uncertainty and edge cases.
- Define done in observable terms.
- Build in delegation boundaries.
- Prefer compact authority over conversational warmth.
- Cut any sentence that does not change behavior.

## A simple before/after example

### Too soft

```md
Try to understand the issue and consider whether tests might be helpful. You may also want to review related files before making changes.
```

### Closer to the Superpowers style

```md
Read the failing path first.
Review the touched files before editing.
Add or update a test when behavior is changing.
If the issue is still ambiguous, stop and gather more evidence.
```

## Final takeaway

The signature style of these skills and agents is:

- concise
- imperative
- structured around workflow
- explicit about rules
- explicit about delegation
- optimized for consistent execution under pressure

If you want your own skills to feel closer to this repo, the biggest improvement is not fancier wording. It is converting vague guidance into ordered, enforceable instructions with clear boundaries.
