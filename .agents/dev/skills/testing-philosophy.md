---
type: skill
description: load this skill if you will write or change any tests.
---

# Testing Philosophy

Tests should protect the application's public contracts, not its implementation details.

The governing documents describe the interface and user experience of the application. Tests should do the same: confirm what a user, workflow author, or library consumer can rely on, while leaving room to change the internal design.

## Primary principle

Prefer tests at the outermost meaningful boundary.

The important boundaries are:

1. **CLI behavior**: what happens when a user or agent runs `myteam ...`.
2. **Public Python API behavior**: what workflow authors and library consumers can import, call, receive, and depend on.
3. **Documented file/resource behavior**: how skills, workflows, frontmatter, and templates are discovered and interpreted.

Tests should usually assert these contracts directly instead of asserting which private function, class, subprocess wrapper, parser helper, or internal data structure happens to implement them.

As much as possible, tests should run end-to-end, holistic flows in their natural environment, rather than in mocked setups.

## What tests should confirm

Tests should confirm user-visible and developer-visible behavior, including:

- behavior documented in `src/governing_docs/`;
- command exit codes;
- stdout and stderr that form part of the CLI contract;
- public API return values and raised exceptions;
- resource discovery;
- workflow results;
- backward-compatible public behavior when implementation internals are refactored.

If a behavior is important enough to test, it should usually be expressible as something a user, agent, workflow author, or library caller can observe.

## What tests should avoid

Avoid implementation-level tests by default. In particular, avoid tests that lock in:

- private helper function boundaries;
- exact internal class layouts;
- transient intermediate data structures;
- call ordering between internal collaborators;
- mocks that assert private interactions instead of public outcomes;
- implementation-specific exceptions from non-public code;
- specific wording of prompts;
- incidental formatting that is not part of the documented user-facing output.

These tests make refactoring expensive without increasing confidence in the application contract.

## CLI contract tests

Because `myteam` is a CLI, many high-value tests should invoke the command as a user would.

CLI tests should generally assert:

- the command that was run;
- process exit code;
- stdout when stdout is part of the contract;
- stderr when diagnostics are part of the contract;
- files or resources created, read, or changed as a result of the command.

CLI tests should not usually assert internal function calls made while serving the command.

When output is intended for an agent, tests should assert that the displayed text is composed of the correct sources, not that the text contains specific content. For example, if a command is supposed to include the text of a specific document, the test should be constructed in a way to demonstrate this provenance. 

## Public Python API tests

Because `myteam` is also a library/framework, public imports and public return values are part of the contract.

API tests should cover behavior such as:

- `from myteam import ...` and `from myteam.workflows import ...` imports that are documented or intentionally supported;
- return values from public functions;
- public dataclass or object fields, when those fields are intended for callers;
- documented exceptions and validation errors;
- equivalence between CLI output and public API output when the docs require them to match.

For example, if a CLI command prints instructions and the Python API exposes the same instructions as a string, tests should confirm that they are the same contract, not two accidentally divergent implementations.

## Implementation-level tests are exceptions

Implementation-level tests are allowed when the implementation itself is risky, hard to observe only through the public surface, or likely to regress in ways that contract tests would diagnose poorly.

Examples include:

- PTY and terminal handling;
- terminal mode restoration;
- forwarding and suppression of TUI byte streams;
- process/session lifecycle edge cases;
- socket or RPC protocol validation;
- race-prone workflow supervision behavior;
- serialization boundaries where malformed input must be rejected safely.

Even in these areas, prefer the highest-level test that gives a useful failure. Drop lower only when necessary to make the test deterministic, fast, or diagnostic.

When an implementation-level test is added, it should be clear from the test name or nearby comment why contract-level coverage is insufficient.

## Fakes over deep mocks

Prefer realistic fakes and small test fixtures over deep mocking of internals.

Good fakes act like external collaborators:

- a fake agent CLI that prints display text and reports a result;
- a temporary skill/workflow tree;
- a local socket peer speaking the public protocol;
- a subprocess fixture that exits with a controlled code.

Avoid mocks that primarily assert private call choreography. They couple tests to the implementation instead of the behavior.

## Testing Agent Prompts

Ultimately, agent prompts are implementation details. These are instructions given to a runtime with the hope of guiding behavior. What we really want to test is the behavior, not the specific instructions.

Do not write tests that lock in a specific wording in a prompt. Do write tests that demonstrate that the correct sources are being used in a prompt (e.g. listing skills displays the actual descriptions from the correct sources). 

Another suite of end-to-end, agent-evaluated tests will verify that the non-deterministic agent behavior is correct.

## Relationship to governing docs

The governing docs are the source of truth for expected behavior. Tests should be traceable to those docs.

If an implementation change breaks a test, review the governing docs to confirm whether the test is correct or overly specific to the implementation. 

If this reveals a conflict with the governing docs, review the change with the user. Some aspects of the design may be flexible if the implementation brings sufficient advantages. 

## Practical rule of thumb

Before writing a test, ask:

> If this test fails after a refactor, did a user-visible or public-API promise break?

If the answer is yes, the test is probably at the right level.

If the answer is no, either raise the test to a public boundary or document why this is one of the rare implementation-level cases worth protecting.
