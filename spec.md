# Fix cyclical dependencies

For this task we need to create a DFS-based algorithm to detect cyclical dependencies on content that is to be created. 

## What this means

When generating canvas content, we may have pages, assignments, quizzes, etc. that reference each other. For example:

- Page A links to Page B
- Page B links to Page C
- Page C links to Page A

This creates a cycle (A -> B -> C -> A) which can lead to infinite loops or other issues when trying to render or 
process the content.

## Requirements

We need to improve the `linearize_dependencies` function found in the `mdxcanvas/deploy/algorithms` file to detect and 
report cyclical dependencies. The function would then return something like `list[tuple[tuple[str, str], CanvasResource]]`
where the first element of the tuple is a tuple of the resource TYPE and ID, and the second element is the actual resource object.

We want the actual resource objects to be returned so that we can later create shells for them in Canvas to fix the cycles.
