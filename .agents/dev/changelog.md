---
type: workflow
description: start this workflow when it is time to prepare the changelog notes for a new release.
output:
    myteam-version: the version of `myteam` we are describing
    changes-of-note: [a list of observed changes in the git branch]
    changes-to-include: [a list of which changes are appropriate for the changelog]
    changelog-notes: the text included in the changelog for this version
---

# Changelog Preparation

Your task is the prepare the changelog notes for the new `myteam` release.

The project version is found in the pyproject.toml. 

When preparing the changelog notes, first observe which changes have occurred. 

Then consider each of those changes: which changes are important to mention to our users? Do not include details that don't affect the user experience or are purely implementation details. These are public-facing notes.

Then synthesize the changes into coherent changelog notes. Write these notes to `src/myteam/CHANGELOG.md` using a `##` version header and a bulleted list of notes. 

Then return the requested output.

