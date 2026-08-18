# MDXCanvas Deployment Engineer Feedback

## Suspected typo in default stale-resource types

**Observed version:** MDXCanvas source reports `0.7.6`.

**Affected role guidance:** The role states that normal deployment removes stale quizzes and module items. This accurately describes the installed source's literal behavior, but that source behavior is likely defective.

### Evidence

- `mdxcanvas/deploy/canvas_deploy.py` defines:

  ```python
  DEFAULT_STALE_RESOURCE_TYPES = frozenset({'quiz', 'module_item'})
  ```

- `QuizTagProcessor` emits each question as an independent `quiz_question` resource with a stable key of `<quiz-id>|<question-id>`.
- `deploy_quiz()` creates/updates quiz metadata only.
- `deploy_quiz_question()` creates or edits questions; it does not remove a question omitted from source.
- Generic stale-resource handling explicitly supports `quiz_question`, looks it up through its parent quiz, prioritizes it for deletion, and deletes it during full `--cleanup`.
- The pre-0.6.15 migration explicitly prunes questions absent from the ledger, but this is a one-time migration path and does not handle ordinary source removals after migration.
- Therefore, ordinary removal of a question from source leaves that Canvas question behind, while omission of an entire quiz from a targeted graph can delete the whole quiz.
- `tests/test_stale_cleanup.py` and CLI help currently assert/document stale `quiz` behavior. They confirm current behavior but may encode the same typo rather than establish desired semantics.
- Git history introduced the constant in commit `c740459` with a test that expects `quiz`; this means the current behavior was committed deliberately, but it does not resolve the mismatch with question-level deployment semantics.

### Likely correction

The probable intended default is:

```python
DEFAULT_STALE_RESOURCE_TYPES = frozenset({'quiz_question', 'module_item'})
```

This needs maintainer confirmation and focused tests before changing production behavior.

### Operational impact

Until fixed and released:

- normal deployments can delete whole tracked quizzes omitted from the rendered graph;
- removed source questions can remain in existing Canvas quizzes;
- targeted deployments are especially dangerous because unrelated tracked quizzes may appear stale;
- operators must inspect both stale quizzes and stale quiz questions and verify actual behavior for the installed version;
- do not compensate with full `--cleanup` on a live course without explicit destructive-action review.

### Resolution

Corrected for MDXCanvas `0.7.7`: the default stale set is now `{'quiz_question', 'module_item'}`. CLI help, focused cleanup tests, and the Deployment Engineer role were updated to match. The submitted-quiz safeguard used during question updates is not invoked by stale-question deletion, so operators must still review stale questions and parent-quiz submissions before deployment.

## Python compatibility issue found during verification

**Observed environment:** Python 3.11.4.

The focused stale-cleanup tests pass, but full test collection fails in `mdxcanvas/text_processing/markdown_processing.py` because an f-string expression contains `"\n"` and requires newer f-string parsing behavior. `pyproject.toml` currently declares Python `^3.10`, so this is a package compatibility discrepancy rather than a failure caused by the stale-cleanup change.

Recommended follow-up: either rewrite that expression to remain compatible with the declared Python range or intentionally raise the package's minimum Python version. Until resolved, use a verified compatible environment for full-suite and deployment work.
