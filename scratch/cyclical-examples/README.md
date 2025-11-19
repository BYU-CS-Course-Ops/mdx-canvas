# Cyclical Include Examples

This directory contains example Canvas resources that demonstrate **cyclical includes** - where resources reference each other in circular dependencies.

These examples are designed to test and demonstrate the DFS-based dependency resolution algorithm with back edge detection.

## Files

### Pages (3 files)
- `page1-intro.canvas.md.xml` - Introduction to Course
- `page2-advanced.canvas.md.xml` - Advanced Topics
- `page3-study-guide.canvas.md.xml` - Study Guide

### Assignments (2 files)
- `assignment1-hw1.canvas.md.xml` - Homework 1
- `assignment2-hw2.canvas.md.xml` - Homework 2

### Quizzes (2 files)
- `quiz1-practice.canvas.md.xml` - Practice Quiz
- `quiz2-final.canvas.md.xml` - Final Quiz

## Cyclical Dependencies

### Direct Cycles (Back Edges)

1. **Page Cycle**: `page1-intro` ↔ `page2-advanced`
   - `page1-intro.canvas.md.xml` includes `page2-advanced.canvas.md.xml`
   - `page2-advanced.canvas.md.xml` includes `page1-intro.canvas.md.xml`
   - **Back edge**: advanced → intro

2. **Assignment Cycle**: `assignment1-hw1` ↔ `assignment2-hw2`
   - `assignment1-hw1.canvas.md.xml` includes `assignment2-hw2.canvas.md.xml`
   - `assignment2-hw2.canvas.md.xml` includes `assignment1-hw1.canvas.md.xml`
   - **Back edge**: hw1 → hw2

3. **Quiz Cycle**: `quiz1-practice` ↔ `quiz2-final`
   - `quiz1-practice.canvas.md.xml` includes `quiz2-final.canvas.md.xml`
   - `quiz2-final.canvas.md.xml` includes `quiz1-practice.canvas.md.xml`
   - **Back edge**: practice → final

### Complex Multi-Resource Cycles

4. **Study Guide → Practice Quiz → Final Quiz → Homework 2 → Advanced Topics → Intro → Study Guide**
   - `page3-study-guide` includes `page1-intro`
   - `page1-intro` references `assignment1-hw1` (via course-link)
   - `assignment1-hw1` includes `page1-intro` AND includes `assignment2-hw2`
   - `assignment2-hw2` includes `page2-advanced`
   - `page2-advanced` includes `page1-intro`
   - `quiz1-practice` includes `page3-study-guide` AND includes `quiz2-final`
   - `quiz2-final` includes `quiz1-practice` AND includes `assignment2-hw2`
   - **Multiple back edges** creating interconnected cycles

## Dependency Graph

```
page1-intro
├─> page2-advanced (included)
└─> assignment1-hw1 (referenced)

page2-advanced
├─> page1-intro (included) ← BACK EDGE (creates cycle)
└─> quiz2-final (referenced)

page3-study-guide
├─> page1-intro (included)
└─> quiz1-practice (referenced)

assignment1-hw1
├─> page1-intro (included)
└─> assignment2-hw2 (included)

assignment2-hw2
├─> assignment1-hw1 (included) ← BACK EDGE (creates cycle)
└─> page2-advanced (included)

quiz1-practice
├─> page3-study-guide (included)
└─> quiz2-final (included)

quiz2-final
├─> assignment2-hw2 (included)
└─> quiz1-practice (included) ← BACK EDGE (creates cycle)
```

## Expected Back Edges (Cycles)

When processed by the DFS algorithm, these back edges should be detected:

1. `page2-advanced → page1-intro` (page cycle)
2. `assignment1-hw1 → assignment2-hw2` (assignment cycle)
3. `quiz1-practice → quiz2-final` (quiz cycle)
4. `page3-study-guide → page1-intro` (indirect page cycle)
5. `assignment1-hw1 → page1-intro` (assignment→page cycle)
6. `assignment2-hw2 → page2-advanced` (assignment→page cycle)

## Testing

To test these examples with the DFS algorithm:

```python
from mdxcanvas.deploy.algorithms import linearize_dependencies
from mdxcanvas.resources import CanvasResource

# Load these files and parse them
# Build the dependency graph
# Call linearize_dependencies(graph, resources)
# Check the logs for detected back edges
```

## How to Handle Cycles

When the DFS algorithm detects a back edge (cycle), the recommended approach is:

1. **Create placeholder resources**: For the resource being referenced via a back edge, create an empty placeholder with the same metadata (id, title, etc.) but with `data=None` or empty body.

2. **First pass**: Process resources in the linearized order, using placeholders for back edge dependencies.

3. **Second pass**: Update the placeholder resources with their actual content.

This two-pass approach allows circular references to work without creating infinite loops.

## Example Use Case

This mirrors real-world scenarios where:
- An **introduction page** references advanced topics for students who want to read ahead
- The **advanced page** tells students to review the introduction if they're confused
- **Homework assignments** reference future assignments to show progression
- **Quizzes** reference each other (practice quiz mentions final, final quiz references practice)
- **Study guides** pull in content from multiple resources that may reference back to the guide

These circular references are natural in educational content and need to be handled gracefully!
