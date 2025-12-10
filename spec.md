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
where the first element of the tuple is a tuple of the resource TYPE and ID, and the second element is the actual 
resource object.

We want the actual resource objects to be returned so that we can later create shells for them in Canvas to fix the 
cycles.

## Implementation Steps

1. **Graph Representation**: Represent the dependencies as a directed graph where each node is a resource and each edge 
   represents a dependency from one resource to another.
2. **DFS Traversal**: Implement a DFS traversal to explore the graph. Maintain a stack to keep track of the current 
   path of nodes being visited.
3. **Cycle Detection**: During the DFS traversal, if we encounter a node that is already in the current path stack, 
   we have detected a cycle. Record the nodes involved in the cycle.
4. **Return Cycles**: Modify the `linearize_dependencies` function to return the detected cycles along with the 
   resource objects.

## Next Steps After Cycle Detection

With the detected cycles, what we need to do is then create empty shells for one of the resources in the cycle. 

The way we plan to tackle this is by the following:

DFS -> Detect Cycle -> Make Note of the Cycle -> Deploy Empty Shell for One Resource in Cycle using the same TYPE 
and ID -> Continue Deployment -> Once all Cycles are Resolved, "Update the Shells" with Actual Content.

#### Notes (thoughts)
- We may want to edit the CanvasResource during the cycle detection phase to mark it as a "shell" or "placeholder" so 
  that we can easily identify it later.
- We should also deploy shells first then the remain content to ensure that the cycles are resolved before attempting 
  to "update" the shells with actual content.

## Shell Creation

Each page, assignment, quiz, etc. should have a method to create an empty shell version of itself. This shell should
have the same TYPE and ID but with minimal content to satisfy Canvas's requirements for creating a resource. For 
example, a shell page might just have a title and no body content, but NEEDS to have the same ID as the original page.

These methods should be stored in the respective files for deploy (e.g., `mdxcanvas/deploy/pages.py`, 
`mdxcanvas/deploy/assignments.py`, etc.) and should be called when a cycle is detected during the deployment process.

## Files to Modify
- `mdxcanvas/deploy/algorithms.py` - Modify `linearize_dependencies` to detect cycles and return them.
- `mdxcanvas/deploy/pages.py` - Add method to create shell page.
- `mdxcanvas/deploy/assignments.py` - Add method to create shell assignment
- `mdxcanvas/deploy/quizzes.py` - Add method to create shell quiz.
- `mdxcanvas/deploy/canvas_deploy.py` - Update deployment logic to handle shell creation and updating.

## Testing
- Create unit tests to verify that cycles are detected correctly.
- Create integration tests to ensure that the deployment process correctly creates shells and updates them after
  all cycles are resolved.
- Test with various scenarios including multiple cycles, nested cycles, and no cycles to ensure robustness.

Keep all tests SIMPLE and create the pages, assignments, and quizzes with minimal content to focus on cycle detection 
and resolution.

## Documentation
- Keep it simple and to the point and only relevant parts of the code that is not already self-documenting 
  (ie variable names, function names, class names, etc)
