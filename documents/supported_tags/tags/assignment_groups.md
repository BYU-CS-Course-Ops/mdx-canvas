# `<assignment-groups>` Tag

The `<assignment-groups>` tag defines assignment groups in a Canvas course. Assignment groups organize assignments into categories with individual grading weights and rules for dropping assignments. This allows you to structure your grade distribution across different assignment types (e.g., homework, quizzes, projects) and apply group-specific grading rules.

## Basic Usage

The `<assignment-groups>` tag contains one or more `<group>` child elements, each defining an individual assignment group.

```xml
<assignment-groups>
    <group id="assignments" name="Assignments" weight="50" />
    <group id="quizzes" name="Quizzes" weight="50" />
</assignment-groups>
```

## Group Attributes

### `name`

The name of the assignment group as it appears in Canvas (required).

```xml
<group id="homework" name="Homework" />
```

### `weight`

The percentage weight this group contributes to the overall course grade. The total weight of all groups typically equals 100.

```xml
<group id="assignments" name="Assignments" weight="50" />
<group id="quizzes" name="Quizzes" weight="30" />
<group id="final-project" name="Final Project" weight="20" />
```

### `id`

Unique identifier for the group (required).

A stable identifier that remains constant even if the group name changes later. This prevents creating duplicate groups during updates.

```xml
<group id="hw" name="Homework" weight="40" />
```

### `drop_lowest`

The number of lowest-scoring assignments to automatically drop from this group when calculating the grade.

```xml
<group id="quizzes" name="Quizzes" weight="20" drop_lowest="2" />
```

In this example, the two lowest quiz scores will be excluded from the grade calculation.

### `drop_highest`

The number of highest-scoring assignments to automatically drop from this group when calculating the grade. This is less common than `drop_lowest`.

```xml
<group id="assignments" name="Assignments" weight="50" drop_highest="1" />
```

### `never_drop`

A pipe-separated list of assignment names that should never be dropped, even if they would normally be candidates for being dropped. Use the assignment titles as they appear in your course.

```xml
<group id="assignments" name="Assignments" weight="50" drop_lowest="3" never_drop="Midterm|Final Exam" />
```

In this example, even though the group drops the 3 lowest assignments, the "Midterm" and "Final Exam" assignments will always be included in the grade calculation.

### `position`

The order in which the group appears in the course gradebook. Lower numbers appear first.

```xml
<group id="homework" name="Homework" weight="40" position="1" />
<group id="quizzes" name="Quizzes" weight="30" position="2" />
<group id="final-project" name="Final Project" weight="30" position="3" />
```

## Examples

### Simple Two-Category Course

```xml
<assignment-groups>
    <group id="assignments" name="Assignments" weight="50" />
    <group id="quizzes" name="Quizzes" weight="50" />
</assignment-groups>
```

### Course with Drop Rules

```xml
<assignment-groups>
    <group id="homework" name="Homework" weight="40" position="1" drop_lowest="2" />
    <group id="quizzes" name="Quizzes" weight="30" position="2" drop_lowest="3" />
    <group id="exams" name="Exams" weight="30" position="3" never_drop="Midterm|Final" />
</assignment-groups>
```

In this example:
- The two lowest homework scores are dropped
- The three lowest quiz scores are dropped
- Midterm and Final exams are always counted, even if they're among the lowest scores

### Complex Course Structure

```xml
<assignment-groups>
    <group id="participation" name="Class Participation" weight="10" />
    <group id="labs" name="Lab Assignments" weight="25" drop_lowest="1" />
    <group id="projects" name="Projects" weight="35" />
    <group id="exams" name="Exams" weight="30" never_drop="Final Exam" />
</assignment-groups>
```

## Linking Assignments to Groups

To assign an assignment to a specific group, use the `assignment_group` attribute on the `<assignment>` tag with the group's `id`:

```xml
<assignment
    title="Homework 1"
    assignment_group="homework"
    points_possible="10">
    ...
</assignment>
```

For more details, see the [`<assignment>` tag documentation](./assignment_tag.md).

## Notes

- Assignment groups are used for grade calculation and organization in Canvas. They don't affect the course structure or content visibility.
- The weights should typically total 100, but Canvas will scale them proportionally if they don't.
- Assignment names used in the `never_drop` attribute must exactly match the assignment titles as defined in your course.
- Groups without assignments will still appear in the gradebook but won't affect the grade calculation.
